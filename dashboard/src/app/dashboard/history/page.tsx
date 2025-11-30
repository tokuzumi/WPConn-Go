"use client";

import { useState, useEffect } from "react";
import { api, Message } from "@/services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search } from "lucide-react";
import { toast } from "sonner";

export default function HistoryPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState("");
    const [phoneFilter, setPhoneFilter] = useState("");
    const [activeTab, setActiveTab] = useState("global");

    const apiKey = "admin-key";

    useEffect(() => {
        loadMessages();
    }, [activeTab]); // Reload when tab changes

    const loadMessages = async () => {
        setLoading(true);
        try {
            // If tab is 'global', we ignore phone filter unless explicitly typed in search? 
            // User asked for "Global | Telefone". 
            // In "Telefone" tab, we probably want to enforce a phone filter or show a specific UI for it.
            // For now, I'll keep the filters common but maybe preset them based on tab?
            // Actually, "Global" implies everything. "Telefone" implies filtering by a specific number.

            const params: any = {
                limit: 50,
                search: search || undefined
            };

            if (activeTab === "phone" && phoneFilter) {
                params.phone = phoneFilter;
            } else if (activeTab === "phone" && !phoneFilter) {
                // If in phone tab but no phone typed, maybe don't fetch or fetch all?
                // Let's fetch all but user knows they should type a phone.
            }

            // If user manually typed phone in Global tab, we still respect it if we want, 
            // but let's stick to the requested UI separation.

            const data = await api.getMessages(apiKey, params);
            setMessages(data);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load messages");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Histórico</h1>
            </div>

            <Tabs defaultValue="global" value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList>
                    <TabsTrigger value="global">Global</TabsTrigger>
                    <TabsTrigger value="phone">Por Telefone</TabsTrigger>
                </TabsList>

                <div className="my-4 flex gap-4">
                    <div className="flex-1">
                        <Input
                            placeholder="Buscar conteúdo..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && loadMessages()}
                        />
                    </div>

                    {activeTab === "phone" && (
                        <div className="w-[200px]">
                            <Input
                                placeholder="Filtrar por número..."
                                value={phoneFilter}
                                onChange={(e) => setPhoneFilter(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && loadMessages()}
                            />
                        </div>
                    )}

                    <Button onClick={loadMessages}>
                        <Search className="mr-2 h-4 w-4" /> Buscar
                    </Button>
                </div>

                <TabsContent value="global" className="mt-0">
                    <MessagesTable messages={messages} loading={loading} />
                </TabsContent>
                <TabsContent value="phone" className="mt-0">
                    <MessagesTable messages={messages} loading={loading} />
                </TabsContent>
            </Tabs>
        </div>
    );
}

function MessagesTable({ messages, loading }: { messages: Message[], loading: boolean }) {
    return (
        <Card>
            <CardContent className="p-0">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Data</TableHead>
                            <TableHead>Número</TableHead>
                            <TableHead>Direção</TableHead>
                            <TableHead>Tipo</TableHead>
                            <TableHead>Conteúdo</TableHead>
                            <TableHead>Status</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {messages.map((msg) => (
                            <TableRow key={msg.id}>
                                <TableCell className="whitespace-nowrap">
                                    {new Date(msg.created_at).toLocaleString()}
                                </TableCell>
                                <TableCell>{msg.phone}</TableCell>
                                <TableCell>
                                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${msg.direction === 'inbound' ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800"}`}>
                                        {msg.direction === 'inbound' ? "Recebida" : "Enviada"}
                                    </span>
                                </TableCell>
                                <TableCell>{msg.type}</TableCell>
                                <TableCell className="max-w-[300px] truncate">
                                    {msg.content || (msg.media_url ? "Mídia" : "-")}
                                </TableCell>
                                <TableCell>
                                    <span className="capitalize">{msg.status}</span>
                                </TableCell>
                            </TableRow>
                        ))}
                        {messages.length === 0 && !loading && (
                            <TableRow>
                                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                                    Nenhuma mensagem encontrada.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    )
}
