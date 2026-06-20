"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/use-toast";
import { getPatient, type PatientSummary } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";

export default function PatientPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { isAuthenticated, logout } = useAuth();
  const { toast } = useToast();
  const [patient, setPatient] = useState<PatientSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated === false) {
      router.push("/login");
      return;
    }
    if (isAuthenticated) {
      getPatient(params.id)
        .then(setPatient)
        .catch((error) => {
          toast({
            variant: "destructive",
            title: "Failed to load patient",
            description: error instanceof Error ? error.message : "Please try again.",
          });
        })
        .finally(() => setIsLoading(false));
    }
  }, [isAuthenticated, params.id, router, toast]);

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
          <Button variant="ghost" size="icon" onClick={logout} aria-label="Log out">
            <LogOut className="h-5 w-5" />
          </Button>
        </nav>
      </header>

      <section className="mx-auto w-full max-w-3xl flex-1 p-6">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : patient ? (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>{patient.name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm text-muted-foreground">ID: {patient.patient_id}</p>
                <p className="text-sm text-muted-foreground">Gender: {patient.gender}</p>
                <p className="text-sm text-muted-foreground">Birth date: {patient.birth_date}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Conditions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {patient.conditions.length > 0 ? (
                    patient.conditions.map((c) => (
                      <Badge key={c} variant="secondary">
                        {c}
                      </Badge>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">No known conditions.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Medications</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {patient.medications.length > 0 ? (
                    patient.medications.map((m) => (
                      <Badge key={m} variant="outline">
                        {m}
                      </Badge>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">No active medications.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Allergies</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {patient.allergies.length > 0 ? (
                    patient.allergies.map((a) => (
                      <Badge key={a} variant="destructive">
                        {a}
                      </Badge>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">No known allergies.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <p className="text-center text-muted-foreground">Patient not found.</p>
        )}
      </section>
    </main>
  );
}
