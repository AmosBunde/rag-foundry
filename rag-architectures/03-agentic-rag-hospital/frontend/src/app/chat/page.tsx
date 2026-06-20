"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, LogOut, Send, ShieldCheck, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { useToast } from "@/components/ui/use-toast";
import { querySchema, type QueryFormData } from "@/lib/validation";
import { queryAgent, type AgentQueryResponse, type Source } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";

export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, logout } = useAuth();
  const { toast } = useToast();
  const [result, setResult] = useState<AgentQueryResponse | null>(null);

  useEffect(() => {
    if (isAuthenticated === false) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<QueryFormData>({
    resolver: zodResolver(querySchema),
    defaultValues: {
      top_k: 5,
    },
  });

  const mutation = useMutation({
    mutationFn: (data: QueryFormData) =>
      queryAgent(data.query, data.patient_id, data.top_k),
    onSuccess: (data) => {
      setResult(data);
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
    setResult(null);
    mutation.mutate(data);
  };

  if (isAuthenticated === null || isAuthenticated === false) {
    return null;
  }

  return (
    <main className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between border-b px-6 py-4">
        <h1 className="text-xl font-semibold">Agentic RAG Hospital</h1>
        <nav className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push("/ingest")}>
            Ingest
          </Button>
          <Button variant="ghost" size="icon" onClick={logout} aria-label="Log out">
            <LogOut className="h-5 w-5" />
          </Button>
        </nav>
      </header>

      <section className="mx-auto w-full max-w-4xl flex-1 gap-4 p-6">
        <Card>
          <CardHeader>
            <CardTitle>Ask a medical question</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="query">Query</Label>
                <Input
                  id="query"
                  placeholder="Ask a medical question"
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

                <div className="space-y-2">
                  <Label htmlFor="patient_id">Patient ID (optional)</Label>
                  <Input
                    id="patient_id"
                    placeholder="pat-001"
                    {...register("patient_id")}
                  />
                </div>
              </div>

              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Send className="mr-2 h-4 w-4" />
                )}
                {mutation.isPending ? "Asking agent..." : "Ask agent"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {result && (
          <div className="mt-6 space-y-4">
            <div className="flex items-center gap-3">
              {result.safety_checks_passed ? (
                <Badge variant="outline" className="gap-1 text-emerald-700">
                  <ShieldCheck className="h-3 w-3" /> Safety checks passed
                </Badge>
              ) : (
                <Badge variant="destructive" className="gap-1">
                  <ShieldAlert className="h-3 w-3" /> Safety check failed
                </Badge>
              )}
              <span className="text-sm text-muted-foreground">
                {result.latency_ms.toFixed(1)} ms
              </span>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Answer</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-wrap">{result.answer}</p>
              </CardContent>
            </Card>

            <Accordion type="single" collapsible>
              <AccordionItem value="reasoning">
                <AccordionTrigger>Agent reasoning</AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-2">
                    {result.plan.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold">Plan</h4>
                        <ol className="ml-5 list-decimal text-sm text-muted-foreground">
                          {result.plan.map((step, idx) => (
                            <li key={idx}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}
                    {result.reasoning.map((step, idx) => (
                      <div key={idx} className="rounded border p-2">
                        <Badge variant="secondary">{step.agent}</Badge>
                        <p className="text-sm">{step.step}</p>
                      </div>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="sources">
                <AccordionTrigger>Sources ({result.sources.length})</AccordionTrigger>
                <AccordionContent>
                  <div className="grid gap-3">
                    {result.sources.map((source: Source) => (
                      <Card key={source.id}>
                        <CardContent className="pt-6">
                          <div className="mb-2 flex items-center justify-between">
                            <Badge variant="outline">{source.source}</Badge>
                            <span className="text-sm text-muted-foreground">
                              Score: {source.score.toFixed(4)}
                            </span>
                          </div>
                          <p className="whitespace-pre-wrap text-sm">{source.text}</p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        )}
      </section>
    </main>
  );
}
