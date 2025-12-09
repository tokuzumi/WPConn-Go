"use client";

import { useEffect, useState } from "react";
import { api, DashboardStatsResponse } from "@/services/api";
import { KPICards } from "@/components/dashboard/kpi-cards";
import { TrafficChart } from "@/components/dashboard/traffic-chart";
import { StatusDonut } from "@/components/dashboard/status-donut";
import { EventHealthChart } from "@/components/dashboard/event-health-chart";
import { useAuth } from "@/context/auth-context";
import { Loader2 } from "lucide-react";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // TODO: Get real API key from auth context or secure storage
        const apiKey = process.env.NEXT_PUBLIC_API_KEY || "";
        
        if (!apiKey) {
           console.error("NEXT_PUBLIC_API_KEY is not defined");
           // Optional: You could allow it to fail gracefully if the backend allows public access, 
           // but given the 401 error, we know it requires a key.
        }
        const data = await api.getDashboardStats(apiKey);
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch dashboard stats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        Falha ao carregar dados do dashboard.
      </div>
    )
  }

  return (
    <div className="flex-1 space-y-4 p-4 pt-1">
      <KPICards data={stats.kpis} />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
        <StatusDonut data={stats.status_distribution} />
        <EventHealthChart data={stats.event_health} />
      </div>

      <div className="grid gap-4 md:grid-cols-1">
        <TrafficChart data={stats.hourly_traffic} />
      </div>
    </div>
  );
}