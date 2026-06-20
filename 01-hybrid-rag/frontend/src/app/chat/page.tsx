"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, LogOut, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { querySchema, type QueryFormData } from "@/lib/validation";
import { queryHybrid, type QueryResult } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";

export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, logout } = useAuth();
  const { toast } = useToast();
  const [results, setResults] = useState<QueryResult[]>([]);
  const [latency, setLatency] = useState<number | null>(null);

  useEffect(() => {
    if (isAuthenticated === false) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<QueryFormData>({
    resolver: zodResolver(querySchema),
    defaultValues: {
      top_k: 5,
      use_dense: true,
      use_sparse: true,
    },
  });

  const useDense = watch("use_dense");
  const useSparse = watch("use_sparse");

  const mutation = useMutation({
    mutationFn: (data: QueryFormData) =>
      queryHybrid(data.query, data.top_k, data.use_dense, data.use_sparse),
    onSuccess: (data) => {
      setResults(data.results);
      setLatency(data.latency_ms);
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Query failed",
        description: error instanceof Error ? error.message : "Please try again.",
      });
    },
  });

  const onSubmit = (data: QueryFormData) => {
    if (!data.use_dense && !data.use_sparse) {
      toast({
        variant: "destructive",
        title: "Invalid selection",
        description: "Select at least one retrieval strategy.",
      });
      return;
    }
    setResults([]);
    setLatency(null);
    mutation.mutate(data);
  };

  if (isAuthenticated === null || isAuthenticated === false) {
    return null;
  }

  return (
    <main className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between border-b px-6 py-4">
        <h1 className="text-xl font-semibold">Hybrid RAG</h1>
        <nav className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push("/ingest")}>
            Ingest
          </Button>
          <Button variant="ghost" size="icon" onClick={logout} aria-label="Log out">
            <LogOut className="h-5 w-5" />
          </Button>
        </nav>
      </header>

      <section className="flex flex-1 flex-col gap-4 p-6">
        <Card>
          <CardHeader>
            <CardTitle>Ask a question</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="query">Query</Label>
                <Input
                  id="query"
                  placeholder="What would you like to know?"
                  {...register("query")}
                />
                {errors.query && (
                  <p className="text-sm text-destructive">{errors.query.message}</p>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-6">
                <div className="space-y-2">
                  <Label htmlFor="top_k">Top K</Label>
                  <Input
                    id="top_k"
                    type="number"
                    min={1}
                    max={50}
                    className="w-24"
                    {...register("top_k", { valueAsNumber: true })}
                  />
                  {errors.top_k && (
                    <p className="text-sm text-destructive">{errors.top_k.message}</p>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="use_dense"
                    checked={useDense}
                    onCheckedChange={(checked) =>
                      setValue("use_dense", checked === true)
                    }
                  />
                  <Label htmlFor="use_dense" className="cursor-pointer">
                    Dense retrieval
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="use_sparse"
                    checked={useSparse}
                    onCheckedChange={(checked) =>
                      setValue("use_sparse", checked === true)
                    }
                  />
                  <Label htmlFor="use_sparse" className="cursor-pointer">
                    Sparse retrieval
                  </Label>
                </div>
              </div>

              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Send className="mr-2 h-4 w-4" />
                )}
                {mutation.isPending ? "Searching..." : "Search"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {latency !== null && (
          <p className="text-sm text-muted-foreground">
            Returned {results.length} results in {latency.toFixed(1)} ms
          </p>
        )}

        <div className="grid gap-4">
          {results.map((result) => (
            <Card key={result.id}>
              <CardContent className="pt-6">
                <div className="mb-2 flex items-center justify-between">
                  <Badge variant={result.source}>{result.source}</Badge>
                  <span className="text-sm text-muted-foreground">
                    Score: {result.score.toFixed(4)}
                  </span>
                </div>
                <p className="whitespace-pre-wrap text-sm">{result.text}</p>
                {Object.keys(result.metadata).length > 0 && (
                  <pre className="mt-3 overflow-x-auto rounded bg-muted p-2 text-xs">
                    {JSON.stringify(result.metadata, null, 2)}
                  </pre>
                )}
              </CardContent>
            </Card>
          ))}

          {!mutation.isPending && results.length === 0 && latency !== null && (
            <p className="text-center text-sm text-muted-foreground">
              No results found.
            </p>
          )}
        </div>
      </section>
    </main>
  );
}
