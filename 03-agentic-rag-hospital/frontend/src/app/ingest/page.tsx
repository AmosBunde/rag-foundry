"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Loader2, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { ingestSchema, parseMetadata } from "@/lib/validation";
import { ingestDocuments, type IngestDocument } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";

interface DocumentForm {
  id: string;
  text: string;
  metadata: string;
}

export default function IngestPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [documents, setDocuments] = useState<DocumentForm[]>([{ id: "", text: "", metadata: "" }]);
  const [errors, setErrors] = useState<Record<number, Record<string, string>>>({});

  useEffect(() => {
    if (isAuthenticated === false) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  const mutation = useMutation({
    mutationFn: ingestDocuments,
    onSuccess: (data) => {
      toast({
        title: "Ingested",
        description: `Indexed ${data.indexed} document(s).`,
      });
      if (data.errors.length > 0) {
        toast({
          variant: "destructive",
          title: "Some documents failed",
          description: data.errors.join("; "),
        });
      }
      setDocuments([{ id: "", text: "", metadata: "" }]);
      setErrors({});
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Ingestion failed",
        description: error instanceof Error ? error.message : "Please try again.",
      });
    },
  });

  const updateDocument = (index: number, field: keyof DocumentForm, value: string) => {
    setDocuments((prev) => prev.map((doc, i) => (i === index ? { ...doc, [field]: value } : doc)));
    setErrors((prev) => {
      const next = { ...prev };
      if (next[index]) {
        delete next[index][field];
      }
      return next;
    });
  };

  const addDocument = () => {
    setDocuments((prev) => [...prev, { id: "", text: "", metadata: "" }]);
  };

  const removeDocument = (index: number) => {
    setDocuments((prev) => prev.filter((_, i) => i !== index));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[index];
      return next;
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const nextErrors: Record<number, Record<string, string>> = {};
    const validDocuments: IngestDocument[] = [];

    documents.forEach((doc, index) => {
      const parsed = ingestSchema.safeParse(doc);
      if (!parsed.success) {
        nextErrors[index] = {};
        parsed.error.errors.forEach((err) => {
          const key = err.path[0] as string;
          nextErrors[index][key] = err.message;
        });
        return;
      }

      try {
        validDocuments.push({
          id: parsed.data.id,
          text: parsed.data.text,
          metadata: parseMetadata(parsed.data.metadata),
        });
      } catch (error) {
        nextErrors[index] = {
          metadata: error instanceof Error ? error.message : "Invalid metadata",
        };
      }
    });

    const ids = validDocuments.map((d) => d.id);
    if (new Set(ids).size !== ids.length) {
      toast({
        variant: "destructive",
        title: "Duplicate IDs",
        description: "Document IDs must be unique.",
      });
      return;
    }

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    mutation.mutate(validDocuments);
  };

  if (isAuthenticated === null || isAuthenticated === false) {
    return null;
  }

  return (
    <main className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between border-b px-6 py-4">
        <h1 className="text-xl font-semibold">Agentic RAG Hospital</h1>
        <nav className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push("/chat")}>
            Chat
          </Button>
        </nav>
      </header>

      <section className="mx-auto w-full max-w-3xl flex-1 p-6">
        <Card>
          <CardHeader>
            <CardTitle>Ingest documents</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {documents.map((doc, index) => (
                <div key={index} className="space-y-4 rounded-lg border p-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-medium">Document {index + 1}</h3>
                    {documents.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => removeDocument(index)}
                        aria-label={`Remove document ${index + 1}`}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`id-${index}`}>ID</Label>
                    <Input
                      id={`id-${index}`}
                      value={doc.id}
                      onChange={(e) => updateDocument(index, "id", e.target.value)}
                      placeholder="doc-1"
                    />
                    {errors[index]?.id && (
                      <p className="text-sm text-destructive">{errors[index].id}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`text-${index}`}>Text</Label>
                    <Textarea
                      id={`text-${index}`}
                      value={doc.text}
                      onChange={(e) => updateDocument(index, "text", e.target.value)}
                      rows={5}
                      placeholder="Document content..."
                    />
                    {errors[index]?.text && (
                      <p className="text-sm text-destructive">{errors[index].text}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`metadata-${index}`}>Metadata (JSON, optional)</Label>
                    <Textarea
                      id={`metadata-${index}`}
                      value={doc.metadata}
                      onChange={(e) => updateDocument(index, "metadata", e.target.value)}
                      rows={2}
                      placeholder='{"author": "name"}'
                    />
                    {errors[index]?.metadata && (
                      <p className="text-sm text-destructive">{errors[index].metadata}</p>
                    )}
                  </div>
                </div>
              ))}

              <div className="flex flex-wrap items-center gap-4">
                <Button type="button" variant="outline" onClick={addDocument}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add document
                </Button>
                <Button type="submit" disabled={mutation.isPending}>
                  {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {mutation.isPending ? "Ingesting..." : "Ingest"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}
