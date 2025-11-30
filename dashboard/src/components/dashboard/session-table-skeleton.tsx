import React from 'react';
import { TableBody, TableCell, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";

export function SessionTableSkeleton() {
  return (
    <TableBody>
      {[1, 2, 3, 4, 5].map((i) => (
        <TableRow key={i}>
          <TableCell className="ps-6 pe-4 py-3 w-[150px]">
            <Skeleton className="h-4 w-24" />
          </TableCell>
          <TableCell className="px-4 py-3 w-[100px]">
            <Skeleton className="h-4 w-12" />
          </TableCell>
          <TableCell className="w-[250px] px-4 py-3">
            <div className="flex items-center gap-x-3">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-1.5 w-24" />
            </div>
          </TableCell>
          <TableCell className="w-px whitespace-nowrap px-4 py-3 text-center">
            <div className="flex justify-center">
              <Skeleton className="h-6 w-20 rounded-full" />
            </div>
          </TableCell>
          <TableCell className="w-px whitespace-nowrap px-4 py-3 text-center">
            <div className="flex justify-center">
              <Skeleton className="h-6 w-12 rounded-full" />
            </div>
          </TableCell>
          <TableCell className="w-px whitespace-nowrap ps-4 pe-6 py-3 text-center">
            <div className="flex justify-center">
              <Skeleton className="size-8 rounded-full" />
            </div>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  );
}