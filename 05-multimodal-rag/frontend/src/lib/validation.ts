import { z } from "zod";

export const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const querySchema = z.object({
  query: z.string().min(3, "Query must be at least 3 characters"),
  top_k: z.number().min(1).max(50),
  modalities: z.array(z.enum(["text", "image", "audio"])).min(1, "Select at least one modality"),
});

export type QueryFormData = z.infer<typeof querySchema>;

export const ingestSchema = z.object({
  id: z.string().min(1, "ID is required"),
  text: z.string().min(1, "Text is required"),
  metadata: z.string().optional(),
});

export type IngestFormData = z.infer<typeof ingestSchema>;

export function parseMetadata(value: string | undefined): Record<string, unknown> {
  if (!value || value.trim() === "") return {};
  try {
    return JSON.parse(value) as Record<string, unknown>;
  } catch {
    throw new Error("Invalid JSON metadata");
  }
}
