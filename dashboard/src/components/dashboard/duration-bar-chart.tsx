"use client";

import React, { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getLastSessionsDuration } from "@/lib/mock-data";
import { Skeleton } from "@/components/ui/skeleton";
import { useTenant } from "@/context/tenant-context";

export function DurationBarChart() {
  const { clientId } = useTenant();
  const [chartData, setChartData] = useState<{ id: number, duration: number }[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [averageDuration, setAverageDuration] = useState<number>(0);

  useEffect(() => {
    async function loadData() {
      if (!clientId) return;
      setIsLoading(true);
      const data = await getLastSessionsDuration(clientId, 15);
      setChartData(data);
      const avg = data.length > 0 ? data.reduce((sum, item) => sum + item.duration, 0) / data.length : 0;
      setAverageDuration(Math.round(avg));
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
          <CardTitle className="text-sm text-muted-foreground font-normal">Duração da Sessão (Últimas 15)</CardTitle>
          <p className="text-xl sm:text-2xl font-medium text-foreground">Média: {averageDuration}s</p>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-0 h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 10, left: -10, bottom: 5 }}>
            <CartesianGrid vertical={false} stroke="hsl(var(--border))" strokeDasharray="3 3" />
            <XAxis dataKey="id" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} label={{ value: 'ID da Sessão', position: 'bottom', fill: 'hsl(var(--muted-foreground))', dy: 10 }} />
            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}s`} />
            <Tooltip content={({ active, payload, label }) => active && payload?.length ? <div className="rounded-lg border bg-background p-2 shadow-sm"><p className="text-sm font-medium">ID da Sessão: {label}</p><div className="flex items-center justify-between gap-x-4 mt-1"><div className="flex items-center gap-x-2"><div className="size-2 rounded-full bg-primary" /><span className="text-xs text-muted-foreground">Duração:</span></div><span className="text-xs font-medium text-foreground">{payload[0].value}s</span></div></div> : null} />
            <Bar dataKey="duration" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} barSize={16} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}