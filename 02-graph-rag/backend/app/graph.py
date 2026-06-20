import re
from typing import Any

import neo4j

from app.config import settings


def _make_entity_id(name: str) -> str:
    return f"entity:{name.lower().strip().replace(' ', '_')}"


class GraphRepository:
    """Neo4j-backed knowledge graph repository for Graph RAG."""

    def __init__(self) -> None:
        self._driver: neo4j.AsyncDriver | None = None

    @property
    def driver(self) -> neo4j.AsyncDriver:
        if self._driver is None:
            self._driver = neo4j.AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
        return self._driver

    async def close(self) -> None:
        if self._driver is not None:
            await self._driver.close()
            self._driver = None

    async def ready(self) -> bool:
        try:
            await self.driver.verify_connectivity()
            return True
        except Exception:
            return False

    async def ingest_document_graph(
        self,
        doc_id: str,
        chunks: list[dict[str, Any]],
        entities: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
    ) -> tuple[int, int]:
        """Persist a document, its chunks, entities and relationships in Neo4j."""
        if not entities:
            return 0, 0

        entity_params = [
            {
                "id": e["id"],
                "name": e["name"],
                "label": e.get("label", "Entity"),
                "chunk_id": e.get("chunk_id"),
            }
            for e in entities
        ]
        rel_params = [
            {
                "source_id": r["source_id"],
                "target_id": r["target_id"],
                "type": r.get("type", "RELATED_TO"),
                "chunk_id": r.get("chunk_id"),
            }
            for r in relationships
        ]
        chunk_params = [
            {
                "id": c["id"],
                "text": c.get("text", ""),
                "parent_id": c.get("parent_id"),
                "chunk_index": c.get("chunk_index", 0),
            }
            for c in chunks
        ]

        async with self.driver.session() as session:
            await session.run(
                """
                MERGE (d:Document {id: $doc_id})
                WITH d
                UNWIND $chunks AS chunk
                MERGE (c:Chunk {id: chunk.id})
                SET c.text = chunk.text, c.chunk_index = chunk.chunk_index
                MERGE (d)-[:HAS_CHUNK]->(c)
                """,
                doc_id=doc_id,
                chunks=chunk_params,
            )

            await session.run(
                """
                UNWIND $entities AS e
                MERGE (ent:Entity {id: e.id})
                SET ent.name = e.name, ent.label = e.label
                WITH e, ent
                MATCH (c:Chunk {id: e.chunk_id})
                MERGE (c)-[:MENTIONS]->(ent)
                """,
                entities=entity_params,
            )

            result = await session.run(
                """
                UNWIND $relationships AS r
                MATCH (a:Entity {id: r.source_id}), (b:Entity {id: r.target_id})
                MERGE (a)-[rel:RELATED_TO {chunk_id: r.chunk_id}]->(b)
                SET rel.type = r.type
                RETURN count(rel) AS rel_count
                """,
                relationships=rel_params,
            )
            record = await result.single()
            rel_count = record["rel_count"] if record else 0

        return len(entity_params), rel_count

    async def get_entities(self, name_query: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        async with self.driver.session() as session:
            if name_query:
                result = await session.run(
                    """
                    MATCH (e:Entity)
                    WHERE toLower(e.name) CONTAINS toLower($name_query)
                    RETURN e.id AS id, e.name AS name, e.label AS label
                    LIMIT $limit
                    """,
                    name_query=name_query,
                    limit=limit,
                )
            else:
                result = await session.run(
                    """
                    MATCH (e:Entity)
                    RETURN e.id AS id, e.name AS name, e.label AS label
                    LIMIT $limit
                    """,
                    limit=limit,
                )
            return [dict(record) async for record in result]

    async def expand_entity(self, entity_id: str, depth: int = 1) -> dict[str, Any] | None:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (e:Entity {id: $entity_id})
                OPTIONAL MATCH path = (e)-[:RELATED_TO*1..$depth]-(related:Entity)
                WITH e, related, min(length(path)) AS dist
                RETURN e.id AS id, e.name AS name, e.label AS label,
                       collect(DISTINCT {id: related.id, name: related.name, label: related.label, distance: dist}) AS related
                """,
                entity_id=entity_id,
                depth=depth,
            )
            record = await result.single()
            if record is None:
                return None
            return {
                "id": record["id"],
                "name": record["name"],
                "label": record["label"],
                "related": [r for r in record["related"] if r["id"] is not None],
            }

    async def get_chunk_ids_near_entities(
        self, entity_ids: list[str], depth: int = 2
    ) -> dict[str, int]:
        """Return a mapping chunk_id -> minimum graph distance from any start entity."""
        if not entity_ids:
            return {}
        async with self.driver.session() as session:
            result = await session.run(
                """
                UNWIND $entity_ids AS start_id
                MATCH (start:Entity {id: start_id})
                OPTIONAL MATCH path = (start)-[:RELATED_TO*0..$depth]-(:Entity)<-[:MENTIONS]-(c:Chunk)
                WITH c, min(length(path)) AS dist
                WHERE c IS NOT NULL
                RETURN c.id AS chunk_id, dist
                """,
                entity_ids=entity_ids,
                depth=depth,
            )
            distances: dict[str, int] = {}
            async for record in result:
                chunk_id = record["chunk_id"]
                dist = record["dist"] or 0
                if chunk_id is not None:
                    distances[chunk_id] = min(distances.get(chunk_id, 10_000), int(dist))
            return distances

    async def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[dict[str, Any]]:
        if not chunk_ids:
            return []
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (c:Chunk)
                WHERE c.id IN $chunk_ids
                RETURN c.id AS id, c.text AS text, c.chunk_index AS chunk_index
                """,
                chunk_ids=chunk_ids,
            )
            return [dict(record) async for record in result]


def extract_entities(text: str, chunk_id: str, max_entities: int = 20) -> list[dict[str, Any]]:
    """Lightweight entity extraction using regex heuristics.

    Production deployments can swap this for spaCy NER or an LLM call.
    """
    # Match capitalised phrases (e.g. "Neo4j", "Graph RAG", "New York")
    pattern = re.compile(r"\b([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)+)\b")
    candidates: list[str] = []
    for match in pattern.finditer(text):
        candidate = match.group(1).strip()
        if len(candidate) < 3 or candidate.isupper():
            continue
        candidates.append(candidate)

    # Also match quoted strings as potential entities
    quote_pattern = re.compile(r'"([^"]{3,60})"')
    for match in quote_pattern.finditer(text):
        candidates.append(match.group(1))

    seen: set[str] = set()
    entities: list[dict[str, Any]] = []
    for name in candidates:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        entities.append({
            "id": _make_entity_id(name),
            "name": name,
            "label": "Entity",
            "chunk_id": chunk_id,
        })
        if len(entities) >= max_entities:
            break

    return entities


def build_relationships(entities: list[dict[str, Any]], chunk_id: str) -> list[dict[str, Any]]:
    """Create CO_OCCURS_WITH relationships between entities found in the same chunk."""
    relationships: list[dict[str, Any]] = []
    if len(entities) < 2:
        return relationships
    ids = [e["id"] for e in entities]
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            relationships.append({
                "source_id": ids[i],
                "target_id": ids[j],
                "type": "CO_OCCURS_WITH",
                "chunk_id": chunk_id,
            })
    return relationships
