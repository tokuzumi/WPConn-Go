import { DashboardStats } from "@/components/dashboard/dashboard-stats";
import { DurationBarChart } from "@/components/dashboard/duration-bar-chart";
import { SessionsAreaChart } from "@/components/dashboard/sessions-area-chart";
import { RecentSessionsTable } from "@/components/dashboard/recent-sessions-table";

export default function DashboardPage() {
  return (
    <div className="px-4 sm:px-6 pb-6 space-y-4 sm:space-y-6">
      <DashboardStats />
      <RecentSessionsTable />
      <div className="grid lg:grid-cols-2 gap-4 sm:gap-6">
        <SessionsAreaChart />
        <DurationBarChart />
      </div>
    </div>
  );
}