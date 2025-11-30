"use client";

import React from "react";
import { DashboardHeader } from "./dashboard-header";
import { DashboardSidebar } from "./dashboard-sidebar";
import { Toaster } from "@/components/ui/sonner";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-muted/40">
      <DashboardSidebar />
      <div className="lg:pl-65">
        <DashboardHeader />
        <main className="pt-6">
          {children}
        </main>
      </div>
      <Toaster />
    </div>
  );
}