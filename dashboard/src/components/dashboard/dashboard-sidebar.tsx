"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Circle } from "lucide-react";
import { cn } from "@/lib/utils";
import { sidebarNavItems } from "./sidebar-nav";

interface DashboardSidebarProps {
  isMobile?: boolean;
}

export function DashboardSidebar({ isMobile = false }: DashboardSidebarProps) {
  const pathname = usePathname();

  return (
    <div
      className={cn(
        "flex flex-col h-full border-r bg-sidebar",
        !isMobile && "fixed inset-y-0 start-0 z-30 w-65 hidden lg:block",
        isMobile && "w-full"
      )}
    >
      <div className="px-6 flex items-center h-16 border-b">
        <a href="#" className="flex-none text-xl inline-block font-semibold text-foreground">
          WPConn Dashboard
        </a>
      </div>

      <nav className="h-full overflow-y-auto p-3">
        <ul className="flex flex-col space-y-1">
          {sidebarNavItems.map((item, index) => {
            const Icon = item.icon || Circle;
            const isActive = pathname === item.href;
            return (
              <li key={index}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-x-3.5 py-2 px-2.5 text-sm rounded-lg transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary font-medium dark:bg-primary/20"
                      : "text-muted-foreground hover:bg-muted/50 dark:hover:bg-muted/50"
                  )}
                >
                  <Icon className="shrink-0 size-4" />
                  {item.title}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}