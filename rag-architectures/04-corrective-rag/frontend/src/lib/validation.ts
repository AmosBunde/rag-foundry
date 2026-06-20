import { z } from "zod";

export const loginSchema = z.object({
  username: z
    .string()
    .min(1, "Username is required")
    .max(64, "Username must be at most 64 characters")
    .regex(/^[a-zA-Z0-9_]+$/, "Username must be alphanumeric"),
  password: z
    .string()
    .min(1, "Password is required")
    .max(128, "Password must be at most 128 characters"),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const querySchema = z.object({
  query: z
    .string()
    .min(3, "Query must be at least 3 characters")
    .max(2000, "Query must be at most 2000 characters"),
  top_k: z.coerce.number().min(1).max(50).default(5),
  use_dense: z.boolean().default(true),
  use_sparse: z.boolean().default(true),
});

export type QueryFormData = z.infer<typeof querySchema>;

export const ingestSchema = z.object({
  id: z
    .string()
    .min(1, "ID is required")
    .max(256, "ID must be at most 256 characters")
    .regex(/^[a-zA-Z0-9_-]+$/, "ID must be alphanumeric with underscores or dashes"),
  text: z
    .string()
    .min(1, "Text is required")
    .max(100_000, "Text must be at most 100,000 characters"),
  metadata: z.string().max(2000, "Metadata must be at most 2000 characters").optional(),
});

export type IngestFormData = z.infer<typeof ingestSchema>;

export function parseMetadata(value: string | undefined): Record<string, unknown> {
  if (!value || value.trim() === "") return {};
  try {
    return JSON.parse(value);
  } catch {
    throw new Error("Metadata must be valid JSON");
  }
}
