"use client";

import { useState } from "react";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { querySchema, type QueryFormData } from "@/lib/validation";
import { queryGraph, type QueryResponse } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import Link from "next/link";

export default function ChatPage() {
  const { toast } = useToast();
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<QueryFormData>({
    resolver: zodResolver(querySchema),
    defaultValues: { top_k: 5, graph_depth: 2 },
  });

  const mutation = useMutation({
    mutationFn: (data: QueryFormData) =>
      queryGraph(data.query, data.top_k, data.graph_depth),
    onSuccess: (data) => setResponse(data),
    onError: (error) => {
      toast({
        title: "Query failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: QueryFormData) => {
    setResponse(null);
    mutation.mutate(data);
  };

  return (
    <main className="container mx-auto max-w-5xl p-4">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Graph RAG Chat</h1>
        <div className="space-x-2">
          <Button variant="outline" asChild>
            <Link href="/ingest">Ingest</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/graph">Graph</Link>
          </Button>
        </div>
      </div>

      <Tabs defaultValue="chat">
        <TabsList>
          <TabsTrigger value="chat">Chat</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="chat">
          <Card>
            <CardHeader>
              <CardTitle>Ask the knowledge graph</CardTitle>
              <CardDescription>
                Graph RAG extracts entities, traverses Neo4j, and ranks Qdrant
                chunks by graph distance.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="query">Question</Label>
                  <Textarea id="query" {...register("query")} />
                  {errors.query && (
                    <p className="text-sm text-destructive">
                      {errors.query.message}
                    </p>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="top_k">Top K</Label>
                    <Input
                      id="top_k"
                      type="number"
                      {...register("top_k")}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="graph_depth">Graph depth</Label>
                    <Input
                      id="graph_depth"
                      type="number"
                      {...register("graph_depth")}
                    />
                  </div>
                </div>
                <Button type="submit" disabled={mutation.isPending}>
                  {mutation.isPending ? "Searching…" : "Search"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results">
          <Card>
            <CardHeader>
              <CardTitle>Retrieved chunks</CardTitle>
              {response && (
                <CardDescription>
                  Query: {response.query} · {response.results.length} results ·{" "}
                  {response.latency_ms.toFixed(1)} ms
                </CardDescription>
              )}
            </CardHeader>
            <CardContent>
              {response ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Source</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Text</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {response.results.map((result) => (
                      <TableRow key={result.id}>
                        <TableCell className="capitalize">
                          {result.source}
                        </TableCell>
                        <TableCell>{result.score.toFixed(3)}</TableCell>
                        <TableCell className="max-w-md truncate">
                          {result.text}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-muted-foreground">No results yet.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </main>
  );
}
