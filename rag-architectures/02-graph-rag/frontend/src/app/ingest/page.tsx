"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { ingestSchema, type IngestFormData, parseMetadata } from "@/lib/validation";
import { ingestDocuments } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import Link from "next/link";

export default function IngestPage() {
  const { toast } = useToast();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<IngestFormData>({
    resolver: zodResolver(ingestSchema),
  });

  const mutation = useMutation({
    mutationFn: (data: IngestFormData) =>
      ingestDocuments([
        {
          id: data.id,
          text: data.text,
          metadata: parseMetadata(data.metadata),
        },
      ]),
    onSuccess: (data) => {
      toast({
        title: "Ingested",
        description: `Indexed ${data.indexed} chunks, ${data.entities_created} entities, ${data.relationships_created} relationships.`,
      });
      reset();
    },
    onError: (error) => {
      toast({
        title: "Ingestion failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    },
  });

  return (
    <main className="container mx-auto max-w-2xl p-4">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Ingest Documents</h1>
        <Button variant="outline" asChild>
          <Link href="/chat">Chat</Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>New document</CardTitle>
          <CardDescription>
            Text is chunked, embedded into Qdrant, and entities/relationships are
            stored in Neo4j.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSubmit((data) => mutation.mutate(data))}
            className="space-y-4"
          >
            <div className="space-y-2">
              <Label htmlFor="id">Document ID</Label>
              <Input id="id" {...register("id")} />
              {errors.id && (
                <p className="text-sm text-destructive">{errors.id.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="text">Text</Label>
              <Textarea id="text" rows={8} {...register("text")} />
              {errors.text && (
                <p className="text-sm text-destructive">
                  {errors.text.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="metadata">Metadata (JSON)</Label>
              <Textarea
                id="metadata"
                {...register("metadata")}
                placeholder='{"source": "docs"}'
              />
              {errors.metadata && (
                <p className="text-sm text-destructive">
                  {errors.metadata.message}
                </p>
              )}
            </div>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Ingesting…" : "Ingest"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
