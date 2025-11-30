"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Info } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  tooltip?: string;
}

export function StatCard({ title, value, tooltip }: StatCardProps) {
  return (
    <TooltipProvider>
      <Card className="shadow-none">
        <CardContent className="p-4 md:p-5">
          <div className="flex items-center gap-x-2">
            <p className="text-xs uppercase text-muted-foreground">
              {title}
            </p>
            {tooltip && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="shrink-0 size-4 text-muted-foreground cursor-help" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>{tooltip}</p>
                </TooltipContent>
              </Tooltip>
            )}
          </div>

          <div className="mt-1 flex items-center gap-x-2">
            <h3 className="text-xl sm:text-2xl font-medium text-foreground">
              {value}
            </h3>
          </div>
        </CardContent>
      </Card>
    </TooltipProvider>
  );
}