"use client";

import React from "react";
import { Bell, Menu, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet";
import { DashboardSidebar } from "./dashboard-sidebar";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "../theme-toggle";

interface DashboardHeaderProps {
  className?: string;
}

export function DashboardHeader({ className }: DashboardHeaderProps) {
  return (
    <header
      className={cn(
        "sticky top-0 z-40 w-full border-b bg-background/80 backdrop-blur-sm",
        className
      )}
    >
      <nav className="h-16 px-4 sm:px-6 flex items-center justify-between">
        <div className="flex items-center lg:hidden">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="mr-2">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Alternar Barra Lateral</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 w-65">
              <SheetTitle className="sr-only">Menu Principal</SheetTitle>
              <DashboardSidebar isMobile={true} />
            </SheetContent>
          </Sheet>
          <a href="#" className="flex-none text-xl inline-block font-semibold text-foreground">
            WPConn Dashboard
          </a>
        </div>

        <div className="hidden md:block lg:ms-6">
          {/* Search removed */}
        </div>

        <div className="flex items-center gap-x-1 md:gap-x-3">
          <div className="hidden md:flex items-center gap-x-2 mr-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
            </span>
            <span className="text-sm font-medium text-muted-foreground">Status: on-line</span>
          </div>
          <ThemeToggle />
          <Button variant="ghost" size="icon" className="size-9.5 rounded-full">
            <Bell className="h-4 w-4" />
            <span className="sr-only">Notificações</span>
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative size-8 rounded-full">
                <Avatar className="size-8">
                  <AvatarFallback className="bg-primary text-primary-foreground">Ad</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-60" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">Admin</p>
                  <p className="text-xs leading-none text-muted-foreground">
                    admin@wpconn.com
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Sair</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </nav>
    </header>
  );
}