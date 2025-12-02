"use client";

import { useState, useEffect } from "react";
import { api, Log } from "@/services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, RefreshCw } from "lucide-react";
import { toast } from "sonner";

export default function LogsPage() {
    const [logs, setLogs] = useState<Log[]>([]);
    const [loading, setLoading] = useState(false);
    const [eventFilter, setEventFilter] = useState("");
    const [activeTab, setActiveTab] = useState("global");
    const [page, setPage] = useState(1);
    const limit = 50;

    const apiKey = process.env.NEXT_PUBLIC_API_KEY || "admin-key";

    useEffect(() => {
        loadLogs();
    }, [activeTab, page]);

    const loadLogs = async () => {
        setLoading(true);
        try {
            const params: any = {
                limit: limit,
                offset: (page - 1) * limit,
                event: eventFilter || undefined
            };

            if (activeTab === "errors") {
                if (!eventFilter) {
                    params.event = "error";
                }
            }

            const data = await api.getLogs(apiKey, params);
            setLogs(data);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load logs");
        } finally {
            setLoading(false);
        }
    };

    const handleNextPage = () => setPage(p => p + 1);
    const handlePrevPage = () => setPage(p => Math.max(1, p - 1));

    return (
        <div className="p-4 pt-1 space-y-4">

            <Tabs defaultValue="global" value={activeTab} onValueChange={(v) => { setActiveTab(v); setPage(1); }} className="w-full">
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
                            onKeyDown={(e) => { if (e.key === 'Enter') { setPage(1); loadLogs(); } }}
                        />
                    </div>
                    <Button onClick={() => { setPage(1); loadLogs(); }}>
                        <Search className="mr-2 h-4 w-4" /> Buscar
                    </Button>
                </div>

                <TabsContent value="global" className="mt-0">
                    <LogsTable logs={logs} loading={loading} apiKey={apiKey} onRetrySuccess={loadLogs} />
                </TabsContent>
                <TabsContent value="phone" className="mt-0">
                    <LogsTable logs={logs} loading={loading} apiKey={apiKey} onRetrySuccess={loadLogs} />
                </TabsContent>
                <TabsContent value="errors" className="mt-0">
                    <LogsTable logs={logs} loading={loading} apiKey={apiKey} onRetrySuccess={loadLogs} />
                </TabsContent>

                <div className="flex justify-end gap-2 mt-4">
                    <Button variant="outline" onClick={handlePrevPage} disabled={page === 1 || loading}>
                        Anterior
                    </Button>
                    <Button variant="outline" onClick={handleNextPage} disabled={logs.length < limit || loading}>
                        Próxima
                    </Button>
                </div>
            </Tabs>
        </div>
    );
}

function LogsTable({ logs, loading, apiKey, onRetrySuccess }: { logs: Log[], loading: boolean, apiKey: string, onRetrySuccess: () => void }) {
    const [retrying, setRetrying] = useState<number | null>(null);

    const handleRetry = async (logId: number) => {
        setRetrying(logId);
        const toastId = toast.loading("Reenviando webhook...");
        try {
            await api.retryWebhook(logId, apiKey);
            toast.dismiss(toastId);
            toast.success("Webhook reenviado com sucesso!");
            onRetrySuccess();
        } catch (error: any) {
            toast.dismiss(toastId);
            toast.error("Falha ao reenviar: " + (error.message || "Erro desconhecido"));
        } finally {
            setRetrying(null);
        }
    };

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
                            <TableHead className="w-[100px]">Ações</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {logs.map((log) => (
                            <TableRow key={log.id}>
                                <TableCell className="whitespace-nowrap">
                                    {new Date(log.created_at.endsWith("Z") ? log.created_at : log.created_at + "Z").toLocaleString()}
                                </TableCell>
                                <TableCell className="font-medium">{log.event}</TableCell>
                                <TableCell className="max-w-[400px] truncate" title={log.detail}>
                                    {log.detail || "-"}
                                </TableCell>
                                <TableCell className="font-mono text-xs">
                                    {log.tenant_id || "-"}
                                </TableCell>
                                <TableCell>
                                    {log.event === 'webhook_delivery_failed' && (
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => handleRetry(log.id)}
                                            disabled={retrying === log.id}
                                        >
                                            <RefreshCw className={`h-3 w-3 mr-1 ${retrying === log.id ? 'animate-spin' : ''}`} />
                                            Reenviar
                                        </Button>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                        {logs.length === 0 && !loading && (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
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
