"use client";

import React, { useState, useEffect } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Check, XCircle, Eye } from "lucide-react";
import { cn } from "@/lib/utils";
import { getRecentHostessSessions, HostessSession } from "@/lib/mock-data";
import { SessionTableSkeleton } from "./session-table-skeleton";
import { useTenant } from "@/context/tenant-context";
import { SessionDetailsSheet } from "./session-details-sheet";

const MAX_DURATION_SECONDS = 300;

const StatusBadge = ({ status }: { status: HostessSession['status'] }) => {
  const isCompleted = status === 'Concluído';
  return (
    <span className={cn("py-1 px-1.5 inline-flex items-center gap-x-1 text-xs font-medium rounded-full", isCompleted ? "bg-teal-100 text-teal-800 dark:bg-teal-500/10 dark:text-teal-500" : "bg-red-100 text-red-800 dark:bg-red-500/10 dark:text-red-500")}>
      {isCompleted ? <Check className="size-2.5" /> : <XCircle className="size-2.5" />}
      {status}
    </span>
  );
};

const PendingBadge = ({ hasPendingIssues }: { hasPendingIssues: boolean }) => {
  return (
    <span className={cn("py-1 px-1.5 inline-flex items-center gap-x-1 text-xs font-medium rounded-full", hasPendingIssues ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-500/10 dark:text-yellow-500" : "bg-gray-100 text-gray-800 dark:bg-gray-500/10 dark:text-gray-500")}>
      {hasPendingIssues ? "Sim" : "Não"}
    </span>
  );
};

const SessionRow = ({ session }: { session: HostessSession }) => {
  const progressPercentage = (Math.min(session.durationSeconds, MAX_DURATION_SECONDS) / MAX_DURATION_SECONDS) * 100;
  const isOverLimit = session.durationSeconds > MAX_DURATION_SECONDS;

  return (
    <TableRow>
      <TableCell className="ps-6 pe-4 py-3 w-[150px]"><span className="block text-sm font-semibold text-foreground">{session.date}</span></TableCell>
      <TableCell className="px-4 py-3 w-[100px]"><span className="block text-sm text-muted-foreground">{session.time}</span></TableCell>
      <TableCell className="w-[250px] px-4 py-3">
        <div className="flex items-center gap-x-3">
          <span className="text-xs font-medium whitespace-nowrap text-foreground">{session.durationSeconds} / {MAX_DURATION_SECONDS}s</span>
          <Progress value={progressPercentage} className="h-1.5 w-24" indicatorClassName={isOverLimit ? "bg-destructive" : "bg-primary"} />
        </div>
      </TableCell>
      <TableCell className="w-px whitespace-nowrap px-4 py-3 text-center"><div className="flex justify-center"><StatusBadge status={session.status} /></div></TableCell>
      <TableCell className="w-px whitespace-nowrap px-4 py-3 text-center"><div className="flex justify-center"><PendingBadge hasPendingIssues={session.hasPendingIssues} /></div></TableCell>
      <TableCell className="w-px whitespace-nowrap ps-4 pe-6 py-3 text-center">
        <div className="flex justify-center">
          <SessionDetailsSheet sessionId={session.id}>
            <Button variant="ghost" size="icon" className="size-8">
              <Eye className="size-4" />
              <span className="sr-only">Ver Detalhes</span>
            </Button>
          </SessionDetailsSheet>
        </div>
      </TableCell>
    </TableRow>
  );
};

export function RecentSessionsTable() {
  const { clientId } = useTenant();
  const [recentSessions, setRecentSessions] = useState<HostessSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadSessions() {
      if (!clientId) return;
      setIsLoading(true);
      const sessions = await getRecentHostessSessions(clientId);
      setRecentSessions(sessions);
      setIsLoading(false);
    }
    loadSessions();
  }, [clientId]);

  return (
    <Card className="shadow-none">
      <CardHeader className="px-6 py-4 border-b">
        <CardTitle className="text-xl font-semibold text-foreground">Sessões Recentes</CardTitle>
      </CardHeader>
      <div className="overflow-x-auto">
        <Table className="min-w-full divide-y">
          <TableHeader>
            <TableRow className="bg-muted/50 hover:bg-muted/50">
              <TableHead className="ps-6 pe-4 w-[150px]">Data</TableHead>
              <TableHead className="px-4 w-[100px]">Hora</TableHead>
              <TableHead className="px-4 w-[250px]">Duração</TableHead>
              <TableHead className="px-4 text-center">Status</TableHead>
              <TableHead className="px-4 text-center">Pendências</TableHead>
              <TableHead className="ps-4 pe-6 w-px whitespace-nowrap text-center">Transcrição</TableHead>
            </TableRow>
          </TableHeader>
          {isLoading ? <SessionTableSkeleton /> : (
            <TableBody>
              {recentSessions.length > 0 ? recentSessions.map((session) => <SessionRow key={session.id} session={session} />) : (
                <TableRow><TableCell colSpan={6} className="h-24 text-center text-muted-foreground">Nenhuma sessão recente encontrada.</TableCell></TableRow>
              )}
            </TableBody>
          )}
        </Table>
      </div>
    </Card>
  );
}