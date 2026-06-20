import { describe, it, expect } from "vitest";
import { loginSchema, querySchema, ingestSchema, parseMetadata } from "@/lib/validation";

describe("validation schemas", () => {
  it("accepts valid login data", () => {
    const result = loginSchema.safeParse({ username: "demo", password: "demo" });
    expect(result.success).toBe(true);
  });

  it("rejects invalid username characters", () => {
    const result = loginSchema.safeParse({ username: "demo user", password: "demo" });
    expect(result.success).toBe(false);
  });

  it("accepts valid query data", () => {
    const result = querySchema.safeParse({
      query: "What is RAG?",
      top_k: 10,
      use_dense: true,
      use_sparse: false,
    });
    expect(result.success).toBe(true);
  });

  it("rejects top_k out of range", () => {
    const result = querySchema.safeParse({
      query: "What is RAG?",
      top_k: 100,
      use_dense: true,
      use_sparse: true,
    });
    expect(result.success).toBe(false);
  });

  it("accepts valid ingest data", () => {
    const result = ingestSchema.safeParse({
      id: "doc-1",
      text: "Document text",
      metadata: '{"author":"test"}',
    });
    expect(result.success).toBe(true);
  });

  it("parses metadata JSON", () => {
    expect(parseMetadata('{"key":"value"}')).toEqual({ key: "value" });
    expect(parseMetadata("")).toEqual({});
    expect(parseMetadata(undefined)).toEqual({});
  });

  it("throws on invalid metadata JSON", () => {
    expect(() => parseMetadata("not json")).toThrow("Metadata must be valid JSON");
  });
});
