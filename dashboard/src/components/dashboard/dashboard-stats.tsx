"use client";

import React, { useState, useEffect } from "react";
import { StatCard } from "./stat-card";
import { getTotalSessionsCount, getTodaySessionsCount, getWeekSessionsCount, getMonthSessionsCount } from "@/lib/mock-data";
import { Skeleton } from "@/components/ui/skeleton";
import { useTenant } from "@/context/tenant-context";

function StatCardSkeleton() {
  return (
    <div className="p-4 md:p-5 border rounded-lg shadow-none">
      <Skeleton className="h-4 w-32 mb-2" />
      <Skeleton className="h-8 w-24" />
    </div>
  );
}

export function DashboardStats() {
  const { clientId } = useTenant();
  const [totalSessions, setTotalSessions] = useState<number | null>(null);
  const [todaySessions, setTodaySessions] = useState<number | null>(null);
  const [weekSessions, setWeekSessions] = useState<number | null>(null);
  const [monthSessions, setMonthSessions] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      if (!clientId) return;

      setIsLoading(true);
      const [total, today, week, month] = await Promise.all([
        getTotalSessionsCount(clientId),
        getTodaySessionsCount(clientId),
        getWeekSessionsCount(clientId),
        getMonthSessionsCount(clientId),
      ]);
      setTotalSessions(total);
      setTodaySessions(today);
      setWeekSessions(week);
      setMonthSessions(month);
      setIsLoading(false);
    }
    loadStats();
  }, [clientId]);

  if (isLoading) {
    return (
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
      </div>
    );
  }

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      <StatCard
        title="Sessões Totais"
        value={totalSessions?.toLocaleString('pt-BR') || '0'}
      />
      <StatCard
        title="Sessões Hoje"
        value={todaySessions?.toLocaleString('pt-BR') || '0'}
      />
      <StatCard
        title="Sessões na Semana"
        value={weekSessions?.toLocaleString('pt-BR') || '0'}
      />
      <StatCard
        title="Sessões no Mês"
        value={monthSessions?.toLocaleString('pt-BR') || '0'}
      />
    </div>
  );
}