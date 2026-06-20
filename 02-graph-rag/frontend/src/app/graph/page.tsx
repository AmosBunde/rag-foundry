"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import { listEntities, expandEntity, type Entity, type ExpandResponse } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import Link from "next/link";

export default function GraphPage() {
  const { toast } = useToast();
  const [nameFilter, setNameFilter] = useState("");
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);

  const entitiesQuery = useQuery({
    queryKey: ["entities", nameFilter],
    queryFn: () => listEntities(nameFilter || undefined),
  });

  const expandQuery = useQuery({
    queryKey: ["expand", selectedEntity?.id],
    queryFn: () => expandEntity(selectedEntity!.id),
    enabled: !!selectedEntity,
  });

  return (
    <main className="container mx-auto max-w-5xl p-4">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Knowledge Graph</h1>
        <Button variant="outline" asChild>
          <Link href="/chat">Chat</Link>
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Entities</CardTitle>
            <CardDescription>
              Search extracted entities stored in Neo4j.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Filter by name"
              value={nameFilter}
              onChange={(e) => setNameFilter(e.target.value)}
            />
            {entitiesQuery.isLoading ? (
              <p className="text-muted-foreground">Loading…</p>
            ) : entitiesQuery.error ? (
              <p className="text-destructive">Failed to load entities.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Label</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {entitiesQuery.data?.map((entity) => (
                    <TableRow
                      key={entity.id}
                      className="cursor-pointer"
                      onClick={() => {
                        setSelectedEntity(entity);
                        expandQuery.refetch().catch((error) => {
                          toast({
                            title: "Expand failed",
                            description:
                              error instanceof Error ? error.message : "Error",
                            variant: "destructive",
                          });
                        });
                      }}
                    >
                      <TableCell>{entity.name}</TableCell>
                      <TableCell>{entity.label}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Entity details</CardTitle>
            <CardDescription>
              Related entities and chunks for the selected node.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedEntity ? (
              <div className="space-y-4">
                <div>
                  <p className="font-semibold">{selectedEntity.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {selectedEntity.label}
                  </p>
                </div>
                {expandQuery.isLoading ? (
                  <p className="text-muted-foreground">Loading…</p>
                ) : expandQuery.data ? (
                  <ExpandDetails data={expandQuery.data} />
                ) : null}
              </div>
            ) : (
              <p className="text-muted-foreground">
                Select an entity to see its neighbourhood.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

function ExpandDetails({ data }: { data: ExpandResponse }) {
  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-medium">Related entities</p>
        {data.related_entities.length === 0 ? (
          <p className="text-sm text-muted-foreground">None found.</p>
        ) : (
          <ul className="mt-1 list-inside list-disc text-sm">
            {data.related_entities.map((entity) => (
              <li key={entity.id}>{entity.name}</li>
            ))}
          </ul>
        )}
      </div>
      <div>
        <p className="text-sm font-medium">Mentioned in chunks</p>
        {data.chunks.length === 0 ? (
          <p className="text-sm text-muted-foreground">None loaded.</p>
        ) : (
          <ul className="mt-1 space-y-1 text-sm">
            {data.chunks.map((chunk) => (
              <li key={chunk.id} className="truncate">
                {chunk.text}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
