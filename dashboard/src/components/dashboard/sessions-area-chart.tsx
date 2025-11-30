"use client";

import React, { useState, useEffect } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getMonthlySessionsChartData } from "@/lib/mock-data";
import { Skeleton } from "@/components/ui/skeleton";
import { useTenant } from "@/context/tenant-context";

export function SessionsAreaChart() {
  const { clientId } = useTenant();
  const [chartData, setChartData] = useState<{ month: string, count: number }[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [totalSessions, setTotalSessions] = useState<number>(0);

  useEffect(() => {
    async function loadData() {
      if (!clientId) return;
      setIsLoading(true);
      const data = await getMonthlySessionsChartData(clientId, 6);
      setChartData(data);
      setTotalSessions(data.reduce((sum, item) => sum + item.count, 0));
      setIsLoading(false);
    }
    loadData();
  }, [clientId]);

  if (isLoading) {
    return (
      <Card className="shadow-none min-h-[410px] flex flex-col">
        <CardHeader className="p-4 md:p-5"><Skeleton className="h-4 w-1/3 mb-2" /><Skeleton className="h-8 w-1/4" /></CardHeader>
        <CardContent className="flex-grow p-0 h-[300px]"><div className="flex items-center justify-center h-full"><Skeleton className="h-[280px] w-[95%]" /></div></CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-none min-h-[410px] flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between p-4 md:p-5">
        <div>
          <CardTitle className="text-sm text-muted-foreground font-normal">Sessões (Últimos 6 meses)</CardTitle>
          <p className="text-xl sm:text-2xl font-medium text-foreground">{totalSessions.toLocaleString('pt-BR')}</p>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-0 h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 20, right: 10, left: -10, bottom: 5 }}>
            <CartesianGrid vertical={false} stroke="hsl(var(--border))" strokeDasharray="3 3" />
            <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => v >= 1000 ? `${v/1000}k` : v} />
            <Tooltip content={({ active, payload, label }) => active && payload?.length ? <div className="rounded-lg border bg-background p-2 shadow-sm"><p className="text-sm font-medium">{label}</p><div className="flex items-center justify-between gap-x-4 mt-1"><div className="flex items-center gap-x-2"><div className="size-2 rounded-full bg-primary" /><span className="text-xs text-muted-foreground">Sessões:</span></div><span className="text-xs font-medium text-foreground">{payload[0].value}</span></div></div> : null} />
            <defs><linearGradient id="colorSessions" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8} /><stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0.1} /></linearGradient></defs>
            <Area type="monotone" dataKey="count" stroke="hsl(var(--primary))" fill="url(#colorSessions)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}