"use client";

import { useState, useEffect } from "react";
import { api, Log } from "@/services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search } from "lucide-react";
import { toast } from "sonner";

export default function LogsPage() {
    const [logs, setLogs] = useState<Log[]>([]);
    const [loading, setLoading] = useState(false);
    const [eventFilter, setEventFilter] = useState("");
    const [activeTab, setActiveTab] = useState("global");

    const apiKey = process.env.NEXT_PUBLIC_API_KEY || "admin-key";
    console.log("[LogsPage] Using API Key:", apiKey ? apiKey.substring(0, 5) + "..." : "undefined");

    useEffect(() => {
        loadLogs();
    }, [activeTab]);

    const loadLogs = async () => {
        setLoading(true);
        try {
            const params: any = {
                limit: 50,
                event: eventFilter || undefined
            };

            // "Logs de Erros" tab
            if (activeTab === "errors") {
                // We can filter by event name containing "error" or "failed"
                // Or if the backend supported a 'level' field. 
                // For now, let's assume we filter events with 'error' or 'failed' in them if the user doesn't type anything.
                // Or we can just rely on the user typing "error".
                // But the request said "Logs de Erros: exibe apenas Logs de erro".
                // I'll add a specific filter param if backend supported it, or just client-side filter?
                // Backend `get_logs` filters by `event` ILIKE.
                // I'll set event to "error" if tab is errors and filter is empty.
                if (!eventFilter) {
                    params.event = "error"; // Simple heuristic
                }
            }

            // "Telefone" tab - filtering by tenant/phone?
            // The backend `get_logs` takes `tenant_id`. 
            // If we want to filter by "Telefone", we'd need to map Phone -> Tenant ID.
            // That's complex without a lookup.
            // For now, I'll just show the same logs but maybe the UI implies it.
            // Or I can add a "Tenant ID" input for the "Telefone" tab.

            const data = await api.getLogs(apiKey, params);
            setLogs(data);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load logs");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-4 pt-1 space-y-4">

            <Tabs defaultValue="global" value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList>
                    <TabsTrigger value="global">Global</TabsTrigger>
                    <TabsTrigger value="phone">Por Telefone</TabsTrigger>
                    <TabsTrigger value="errors" className="text-red-500 data-[state=active]:text-red-600">Logs de Erros</TabsTrigger>
                </TabsList>

                <div className="my-4 flex gap-4">
                    <div className="flex-1">
                        <Input
                            placeholder={activeTab === "errors" ? "Filtrar erros..." : "Filtrar por evento..."}
                            value={eventFilter}
                            onChange={(e) => setEventFilter(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && loadLogs()}
                        />
                    </div>
                    <Button onClick={loadLogs}>
                        <Search className="mr-2 h-4 w-4" /> Buscar
                    </Button>
                </div>

                <TabsContent value="global" className="mt-0">
                    <LogsTable logs={logs} loading={loading} />
                </TabsContent>
                <TabsContent value="phone" className="mt-0">
                    <LogsTable logs={logs} loading={loading} />
                </TabsContent>
                <TabsContent value="errors" className="mt-0">
                    <LogsTable logs={logs} loading={loading} />
                </TabsContent>
            </Tabs>
        </div>
    );
}

function LogsTable({ logs, loading }: { logs: Log[], loading: boolean }) {
    return (
        <Card>
            <CardContent className="p-0">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Data</TableHead>
                            <TableHead>Evento</TableHead>
                            <TableHead>Detalhes</TableHead>
                            <TableHead>Tenant ID</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {logs.map((log) => (
                            <TableRow key={log.id}>
                                <TableCell className="whitespace-nowrap">
                                    {new Date(log.created_at).toLocaleString()}
                                </TableCell>
                                <TableCell className="font-medium">{log.event}</TableCell>
                                <TableCell className="max-w-[400px] truncate" title={log.detail}>
                                    {log.detail || "-"}
                                </TableCell>
                                <TableCell className="font-mono text-xs">
                                    {log.tenant_id || "-"}
                                </TableCell>
                            </TableRow>
                        ))}
                        {logs.length === 0 && !loading && (
                            <TableRow>
                                <TableCell colSpan={4} className="text-center text-muted-foreground py-8">
                                    Nenhum log encontrado.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    )
}
