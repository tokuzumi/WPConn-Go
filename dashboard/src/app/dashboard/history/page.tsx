"use client";

import { useState, useEffect } from "react";
import { api, Message } from "@/services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Eye, Search } from "lucide-react";
import { toast } from "sonner";

export default function HistoryPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState("");
    const [phoneFilter, setPhoneFilter] = useState("");
    const [activeTab, setActiveTab] = useState("global");
    const [page, setPage] = useState(1);
    const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
    const [isSheetOpen, setIsSheetOpen] = useState(false);
    const limit = 50;

    const apiKey = process.env.NEXT_PUBLIC_API_KEY || "admin-key";

    useEffect(() => {
        loadMessages();
    }, [activeTab, page]);

    const loadMessages = async () => {
        setLoading(true);
        try {
            const params: any = {
                limit: limit,
                offset: (page - 1) * limit,
                search: search || undefined
            };

            if (activeTab === "phone" && phoneFilter) {
                params.phone = phoneFilter;
            }

            const data = await api.getMessages(apiKey, params);
            setMessages(data);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load messages");
        } finally {
            setLoading(false);
        }
    };

    const handleNextPage = () => setPage(p => p + 1);
    const handlePrevPage = () => setPage(p => Math.max(1, p - 1));

    const handleViewDetails = (msg: Message) => {
        setSelectedMessage(msg);
        setIsSheetOpen(true);
    };

    return (
        <div className="p-4 pt-1 space-y-4">
            <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
                <SheetContent>
                    <SheetHeader>
                        <SheetTitle>Detalhes da Mensagem</SheetTitle>
                        <SheetDescription>
                            ID: {selectedMessage?.id}
                        </SheetDescription>
                    </SheetHeader>
                    {selectedMessage && (
                        <div className="mt-6 space-y-4">
                            <div>
                                <h4 className="text-sm font-medium">Data</h4>
                                <p className="text-sm text-muted-foreground">
                                    {new Date(selectedMessage.created_at.endsWith("Z") ? selectedMessage.created_at : selectedMessage.created_at + "Z").toLocaleString()}
                                </p>
                            </div>
                            <div>
                                <h4 className="text-sm font-medium">De/Para</h4>
                                <p className="text-sm text-muted-foreground">{selectedMessage.phone}</p>
                            </div>
                            <div>
                                <h4 className="text-sm font-medium">Direção</h4>
                                <p className="text-sm text-muted-foreground">
                                    {selectedMessage.direction === 'inbound' ? "Recebida" : "Enviada"}
                                </p>
                            </div>
                            <div>
                                <h4 className="text-sm font-medium">Tipo</h4>
                                <p className="text-sm text-muted-foreground capitalize">{selectedMessage.type}</p>
                            </div>
                            <div>
                                <h4 className="text-sm font-medium">Status</h4>
                                <p className="text-sm text-muted-foreground capitalize">{selectedMessage.status}</p>
                            </div>
                            <div>
                                <h4 className="text-sm font-medium">Conteúdo Completo</h4>
                                <div className="mt-1 rounded-md bg-muted p-2 text-sm whitespace-pre-wrap break-words">
                                    {selectedMessage.content || (selectedMessage.media_url ? "Mídia: " + selectedMessage.media_url : "-")}
                                </div>
                            </div>
                            {selectedMessage.wamid && (
                                <div>
                                    <h4 className="text-sm font-medium">WAMID</h4>
                                    <p className="text-xs text-muted-foreground break-all">{selectedMessage.wamid}</p>
                                </div>
                            )}
                        </div>
                    )}
                </SheetContent>
            </Sheet>

            <Tabs defaultValue="global" value={activeTab} onValueChange={(v) => { setActiveTab(v); setPage(1); }} className="w-full">
                <TabsList>
                    <TabsTrigger value="global">Global</TabsTrigger>
                    <TabsTrigger value="phone">Por Telefone</TabsTrigger>
                </TabsList>

                <div className="my-4 flex gap-4">
                    <div className="flex-1">
                        <Input
                            placeholder="Buscar Mensagem"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            onKeyDown={(e) => { if (e.key === 'Enter') { setPage(1); loadMessages(); } }}
                        />
                    </div>

                    {activeTab === "phone" && (
                        <div className="w-[200px]">
                            <Input
                                placeholder="Filtrar por número..."
                                value={phoneFilter}
                                onChange={(e) => setPhoneFilter(e.target.value)}
                                onKeyDown={(e) => { if (e.key === 'Enter') { setPage(1); loadMessages(); } }}
                            />
                        </div>
                    )}

                    <Button onClick={() => { setPage(1); loadMessages(); }}>
                        <Search className="mr-2 h-4 w-4" /> Buscar
                    </Button>
                </div>

                <TabsContent value="global" className="mt-0">
                    <MessagesTable messages={messages} loading={loading} onViewDetails={handleViewDetails} />
                </TabsContent>
                <TabsContent value="phone" className="mt-0">
                    <MessagesTable messages={messages} loading={loading} onViewDetails={handleViewDetails} />
                </TabsContent>

                <div className="flex justify-end gap-2 mt-4">
                    <Button variant="outline" onClick={handlePrevPage} disabled={page === 1 || loading}>
                        Anterior
                    </Button>
                    <Button variant="outline" onClick={handleNextPage} disabled={messages.length < limit || loading}>
                        Próxima
                    </Button>
                </div>
            </Tabs>
        </div>
    );
}

function MessagesTable({ messages, loading, onViewDetails }: { messages: Message[], loading: boolean, onViewDetails: (msg: Message) => void }) {
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
                            <TableHead>Mensagem</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead className="w-[50px]">Detalhes</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {messages.map((msg) => (
                            <TableRow key={msg.id}>
                                <TableCell className="whitespace-nowrap">
                                    {new Date(msg.created_at.endsWith("Z") ? msg.created_at : msg.created_at + "Z").toLocaleString()}
                                </TableCell>
                                <TableCell>{msg.phone}</TableCell>
                                <TableCell>
                                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${msg.direction === 'inbound' ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800"}`}>
                                        {msg.direction === 'inbound' ? "Recebida" : "Enviada"}
                                    </span>
                                </TableCell>
                                <TableCell>{msg.type}</TableCell>
                                <TableCell className="max-w-[300px]" title={msg.content || ""}>
                                    {msg.content ? (
                                        msg.content.length > 45 ? msg.content.substring(0, 45) + "..." : msg.content
                                    ) : (
                                        msg.media_url ? "Mídia" : "-"
                                    )}
                                </TableCell>
                                <TableCell>
                                    <span className="capitalize">{msg.status}</span>
                                </TableCell>
                                <TableCell>
                                    <Button variant="ghost" size="icon" onClick={() => onViewDetails(msg)}>
                                        <Eye className="h-4 w-4" />
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                        {messages.length === 0 && !loading && (
                            <TableRow>
                                <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
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
