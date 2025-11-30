import { Home, Smartphone, History, FileText, Users } from "lucide-react";

export const sidebarNavItems = [
  {
    title: "Painel",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "Telefones",
    href: "/dashboard/connections",
    icon: Smartphone,
  },
  {
    title: "Histórico",
    href: "/dashboard/history",
    icon: History,
  },
  {
    title: "Logs",
    href: "/dashboard/logs",
    icon: FileText,
  },
  {
    title: "Usuários",
    href: "/dashboard/users",
    icon: Users,
  },
];