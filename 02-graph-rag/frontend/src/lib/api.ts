import { getToken } from "@/lib/auth";

export const API_BASE_URL =
  typeof window === "undefined"
    ? process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"
    : "";

function getApiUrl(): string {
  if (typeof window === "undefined") return API_BASE_URL;
  return "";
}

async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();
  const headers = new Headers(options.headers);

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${getApiUrl()}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  }

  return response;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function login(
  username: string,
  password: string
): Promise<TokenResponse> {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const response = await apiFetch("/api/v1/auth/token", {
    method: "POST",
    body: formData,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(error.detail || "Login failed");
  }

  return response.json();
}

export interface QueryResult {
  id: string;
  text: string;
  score: number;
  metadata: Record<string, unknown>;
  source: "graph" | "vector" | "fusion";
}

export interface QueryResponse {
  query: string;
  results: QueryResult[];
  latency_ms: number;
}

export async function queryGraph(
  query: string,
  topK: number,
  graphDepth: number
): Promise<QueryResponse> {
  const response = await apiFetch("/api/v1/query/graph", {
    method: "POST",
    body: JSON.stringify({ query, top_k: topK, graph_depth: graphDepth }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Query failed" }));
    throw new Error(error.detail || "Query failed");
  }

  return response.json();
}

export interface IngestResponse {
  indexed: number;
  entities_created: number;
  relationships_created: number;
  errors: string[];
}

export interface IngestDocument {
  id: string;
  text: string;
  metadata?: Record<string, unknown>;
}

export async function ingestDocuments(
  documents: IngestDocument[]
): Promise<IngestResponse> {
  const response = await apiFetch("/api/v1/ingest", {
    method: "POST",
    body: JSON.stringify({ documents }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Ingestion failed" }));
    throw new Error(error.detail || "Ingestion failed");
  }

  return response.json();
}

export interface Entity {
  id: string;
  name: string;
  label: string;
}

export async function listEntities(name?: string): Promise<Entity[]> {
  const qs = name ? `?name=${encodeURIComponent(name)}` : "";
  const response = await apiFetch(`/api/v1/graph/entities${qs}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to load entities" }));
    throw new Error(error.detail || "Failed to load entities");
  }

  return response.json();
}

export interface ExpandResponse {
  entity: Entity;
  related_entities: Entity[];
  chunks: QueryResult[];
}

export async function expandEntity(entityId: string): Promise<ExpandResponse> {
  const response = await apiFetch(`/api/v1/graph/expand/${encodeURIComponent(entityId)}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to expand entity" }));
    throw new Error(error.detail || "Failed to expand entity");
  }

  return response.json();
}
