"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, LogOut, Send, ThumbsDown, ThumbsUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";
import { querySchema, type QueryFormData } from "@/lib/validation";
import {
  queryCorrective,
  submitFeedback,
  type CorrectiveIteration,
  type CorrectiveResponse,
  type QueryResult,
} from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";

function confidenceColor(confidence: number): string {
  if (confidence >= 0.75) return "text-emerald-600";
  if (confidence >= 0.5) return "text-amber-600";
  return "text-destructive";
}

export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, logout } = useAuth();
  const { toast } = useToast();
  const [response, setResponse] = useState<CorrectiveResponse | null>(null);
  const [feedbackMap, setFeedbackMap] = useState<Record<string, boolean | null>>({});

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

  const queryMutation = useMutation({
    mutationFn: (data: QueryFormData) =>
      queryCorrective(data.query, data.top_k, data.use_dense, data.use_sparse),
    onSuccess: (data) => {
      setResponse(data);
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Query failed",
        description: error instanceof Error ? error.message : "Please try again.",
      });
    },
  });

  const feedbackMutation = useMutation({
    mutationFn: ({
      resultId,
      helpful,
    }: {
      queryId: string;
      resultId: string;
      helpful: boolean;
    }) =>
      submitFeedback({
        query_id: response?.original_query || "unknown",
        result_id: resultId,
        helpful,
      }),
    onSuccess: (_, variables) => {
      setFeedbackMap((prev) => ({ ...prev, [variables.resultId]: variables.helpful }));
      toast({ title: "Feedback recorded", description: "Thank you for your feedback." });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Feedback failed",
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
    setResponse(null);
    setFeedbackMap({});
    queryMutation.mutate(data);
  };

  const handleFeedback = (resultId: string, helpful: boolean) => {
    feedbackMutation.mutate({
      queryId: response?.original_query || "unknown",
      resultId,
      helpful,
    });
  };

  if (isAuthenticated === null || isAuthenticated === false) {
    return null;
  }

  return (
    <main className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between border-b px-6 py-4">
        <h1 className="text-xl font-semibold">Corrective RAG</h1>
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
                    onCheckedChange={(checked) => setValue("use_dense", checked === true)}
                  />
                  <Label htmlFor="use_dense" className="cursor-pointer">
                    Dense retrieval
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="use_sparse"
                    checked={useSparse}
                    onCheckedChange={(checked) => setValue("use_sparse", checked === true)}
                  />
                  <Label htmlFor="use_sparse" className="cursor-pointer">
                    Sparse retrieval
                  </Label>
                </div>
              </div>

              <Button type="submit" disabled={queryMutation.isPending}>
                {queryMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Send className="mr-2 h-4 w-4" />
                )}
                {queryMutation.isPending ? "Searching..." : "Search"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {response && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Answer</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-wrap text-sm">{response.answer}</p>
                <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                  <span>
                    Final confidence:{" "}
                    <span className={confidenceColor(response.final_confidence)}>
                      {(response.final_confidence * 100).toFixed(1)}%
                    </span>
                  </span>
                  <span>Rewrites: {response.rewrite_count}</span>
                  <span>Iterations: {response.iterations.length}</span>
                  <span>Latency: {response.latency_ms.toFixed(1)} ms</span>
                </div>
              </CardContent>
            </Card>

            <Tabs defaultValue="final">
              <TabsList>
                <TabsTrigger value="final">Final results</TabsTrigger>
                <TabsTrigger value="iterations">Retrieval iterations</TabsTrigger>
              </TabsList>

              <TabsContent value="final" className="space-y-4">
                {response.final_results.map((result) => (
                  <ResultCard
                    key={result.id}
                    result={result}
                    feedback={feedbackMap[result.id]}
                    onFeedback={handleFeedback}
                    submitting={feedbackMutation.isPending}
                  />
                ))}
              </TabsContent>

              <TabsContent value="iterations" className="space-y-6">
                {response.iterations.map((iteration) => (
                  <IterationCard key={iteration.iteration} iteration={iteration} />
                ))}
              </TabsContent>
            </Tabs>
          </div>
        )}
      </section>
    </main>
  );
}

function ResultCard({
  result,
  feedback,
  onFeedback,
  submitting,
}: {
  result: QueryResult;
  feedback: boolean | null | undefined;
  onFeedback: (resultId: string, helpful: boolean) => void;
  submitting: boolean;
}) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="mb-2 flex items-center justify-between">
          <Badge variant={result.source}>{result.source}</Badge>
          <span className="text-sm text-muted-foreground">Score: {result.score.toFixed(4)}</span>
        </div>
        <p className="whitespace-pre-wrap text-sm">{result.text}</p>
        {Object.keys(result.metadata).length > 0 && (
          <pre className="mt-3 overflow-x-auto rounded bg-muted p-2 text-xs">
            {JSON.stringify(result.metadata, null, 2)}
          </pre>
        )}
        <div className="mt-4 flex items-center gap-2">
          <Button
            variant={feedback === true ? "default" : "outline"}
            size="sm"
            onClick={() => onFeedback(result.id, true)}
            disabled={submitting || feedback !== undefined}
            aria-label="Helpful"
          >
            <ThumbsUp className="mr-1 h-4 w-4" /> Helpful
          </Button>
          <Button
            variant={feedback === false ? "destructive" : "outline"}
            size="sm"
            onClick={() => onFeedback(result.id, false)}
            disabled={submitting || feedback !== undefined}
            aria-label="Not helpful"
          >
            <ThumbsDown className="mr-1 h-4 w-4" /> Not helpful
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function IterationCard({ iteration }: { iteration: CorrectiveIteration }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Iteration {iteration.iteration}</CardTitle>
          {iteration.rewritten && <Badge variant="secondary">Rewritten query</Badge>}
        </div>
        <p className="text-sm text-muted-foreground">
          Query: <span className="font-medium text-foreground">{iteration.query}</span>
        </p>
        <p className="text-sm text-muted-foreground">
          Confidence:{" "}
          <span className={confidenceColor(iteration.confidence)}>
            {(iteration.confidence * 100).toFixed(1)}%
          </span>
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        {iteration.results.map((result) => (
          <div key={result.id} className="rounded border p-3">
            <div className="mb-1 flex items-center justify-between">
              <Badge variant={result.source}>{result.source}</Badge>
              <span className="text-xs text-muted-foreground">Score: {result.score.toFixed(4)}</span>
            </div>
            <p className="text-sm">{result.text}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
