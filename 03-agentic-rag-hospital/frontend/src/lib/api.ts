import { getToken } from "@/lib/auth";

export const API_BASE_URL =
  typeof window === "undefined"
    ? process.env.NEXT_PUBLIC_API_URL || "http://localhost:8003"
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

export interface ReasoningStep {
  agent: string;
  step: string;
  detail?: Record<string, unknown>;
}

export interface Source {
  id: string;
  text: string;
  score: number;
  metadata: Record<string, unknown>;
  source: string;
}

export interface AgentQueryResponse {
  query: string;
  answer: string;
  plan: string[];
  reasoning: ReasoningStep[];
  sources: Source[];
  safety_checks_passed: boolean;
  disclaimer: string;
  latency_ms: number;
}

export async function queryAgent(
  query: string,
  patientId: string | undefined,
  topK: number
): Promise<AgentQueryResponse> {
  const body: Record<string, unknown> = { query, top_k: topK };
  if (patientId) body.patient_id = patientId;

  const response = await apiFetch("/api/v1/query/agent", {
    method: "POST",
    body: JSON.stringify(body),
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

export interface PatientSummary {
  patient_id: string;
  name: string;
  birth_date: string;
  gender: string;
  conditions: string[];
  medications: string[];
  allergies: string[];
}

export async function getPatient(patientId: string): Promise<PatientSummary> {
  const response = await apiFetch(`/api/v1/patients/${patientId}`, {
    method: "GET",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Patient not found" }));
    throw new Error(error.detail || "Patient not found");
  }

  return response.json();
}
