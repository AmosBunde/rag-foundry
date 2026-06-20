from collections import defaultdict

from app.models import RetrievedChunk


def reciprocal_rank_fusion(
    dense_results: list[RetrievedChunk],
    sparse_results: list[RetrievedChunk],
    k: int = 60,
    top_k: int = 5,
) -> list[RetrievedChunk]:
    """Combine ranked lists using Reciprocal Rank Fusion (RRF).

    score = sum(1 / (k + rank)) for each list the document appears in.
    """
    scores: defaultdict[str, float] = defaultdict(float)
    texts: dict[str, str] = {}
    metadata: dict[str, dict] = {}

    def _process(results: list[RetrievedChunk]) -> None:
        for rank, chunk in enumerate(results, start=1):
            scores[chunk.id] += 1 / (k + rank)
            texts.setdefault(chunk.id, chunk.text)
            metadata.setdefault(chunk.id, chunk.metadata)

    _process(dense_results)
    _process(sparse_results)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [
        RetrievedChunk(
            id=doc_id,
            text=texts[doc_id],
            score=score,
            metadata=metadata[doc_id],
            source="fusion",
        )
        for doc_id, score in ranked
    ]
