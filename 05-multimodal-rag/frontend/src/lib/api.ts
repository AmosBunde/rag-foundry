import { getToken } from "@/lib/auth";

export const API_BASE_URL =
  typeof window === "undefined"
    ? process.env.NEXT_PUBLIC_API_URL || "http://localhost:8005"
    : "";

function getApiUrl(): string {
  if (typeof window === "undefined") return API_BASE_URL;
  return "";
}

async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
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

export async function login(username: string, password: string): Promise<TokenResponse> {
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

export type Modality = "text" | "image" | "audio";

export interface QueryResult {
  id: string;
  modality: Modality;
  content: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface QueryResponse {
  query: string;
  results: QueryResult[];
  latency_ms: number;
  modalities: Modality[];
}

export async function queryMultimodal(
  query: string,
  topK: number,
  modalities: Modality[]
): Promise<QueryResponse> {
  const response = await apiFetch("/api/v1/query/multimodal", {
    method: "POST",
    body: JSON.stringify({ query, top_k: topK, modalities }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Query failed" }));
    throw new Error(error.detail || "Query failed");
  }

  return response.json();
}

export interface IngestResponse {
  indexed: number;
  errors: string[];
}

export interface IngestDocument {
  id: string;
  text: string;
  metadata?: Record<string, unknown>;
}

export async function ingestDocuments(documents: IngestDocument[]): Promise<IngestResponse> {
  const response = await apiFetch("/api/v1/ingest/text", {
    method: "POST",
    body: JSON.stringify({ documents }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Ingestion failed" }));
    throw new Error(error.detail || "Ingestion failed");
  }

  return response.json();
}

export async function ingestImage(file: File, metadata?: Record<string, unknown>): Promise<{ id: string; status: string; caption?: string }> {
  const formData = new FormData();
  formData.append("file", file);
  if (metadata) {
    formData.append("metadata", JSON.stringify(metadata));
  }

  const response = await apiFetch("/api/v1/ingest/image", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Image upload failed" }));
    throw new Error(error.detail || "Image upload failed");
  }

  return response.json();
}

export async function ingestAudio(file: File, metadata?: Record<string, unknown>): Promise<{ id: string; status: string; transcription?: string }> {
  const formData = new FormData();
  formData.append("file", file);
  if (metadata) {
    formData.append("metadata", JSON.stringify(metadata));
  }

  const response = await apiFetch("/api/v1/ingest/audio", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Audio upload failed" }));
    throw new Error(error.detail || "Audio upload failed");
  }

  return response.json();
}
