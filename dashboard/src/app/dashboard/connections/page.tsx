"use client";

import { useState, useEffect } from "react";
import { api, Tenant } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

export default function ConnectionsPage() {
    const [tenants, setTenants] = useState<Tenant[]>([]);
    const [loading, setLoading] = useState(false);

    const [newTenantName, setNewTenantName] = useState("");
    const [newTenantWabaId, setNewTenantWabaId] = useState("");
    const [newTenantPhoneId, setNewTenantPhoneId] = useState("");
    const [newTenantToken, setNewTenantToken] = useState("");
    const [newTenantWebhook, setNewTenantWebhook] = useState("");

    const [isDialogOpen, setIsDialogOpen] = useState(false);

    // Hardcoded API Key for now or fetch from Auth Context if we implement user-based keys
    const apiKey = "admin-key"; // Placeholder

    useEffect(() => {
        loadTenants();
    }, []);

    const loadTenants = async () => {
        setLoading(true);
        try {
            const data = await api.getTenants(apiKey);
            setTenants(data);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load connections");
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async () => {
        try {
            await api.createTenant({
                name: newTenantName,
                waba_id: newTenantWabaId,
                phone_number_id: newTenantPhoneId,
                token: newTenantToken,
                webhook_url: newTenantWebhook
            }, apiKey);

            toast.success("Connection created");
            setIsDialogOpen(false);
            loadTenants();

            // Reset form
            setNewTenantName("");
            setNewTenantWabaId("");
            setNewTenantPhoneId("");
            setNewTenantToken("");
            setNewTenantWebhook("");
        } catch (error) {
            console.error(error);
            toast.error("Failed to create connection");
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure?")) return;
        try {
            await api.deleteTenant(id, apiKey);
            toast.success("Connection deleted");
            loadTenants();
        } catch (error) {
            console.error(error);
            toast.error("Failed to delete connection");
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Telefones</h1>
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" /> Nova Conexão
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Nova Conexão WhatsApp</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4 py-4">
                            <div className="space-y-2">
                                <Label>Nome</Label>
                                <Input value={newTenantName} onChange={(e) => setNewTenantName(e.target.value)} placeholder="Ex: Vendas" />
                            </div>
                            <div className="space-y-2">
                                <Label>WABA ID</Label>
                                <Input value={newTenantWabaId} onChange={(e) => setNewTenantWabaId(e.target.value)} placeholder="WABA ID" />
                            </div>
                            <div className="space-y-2">
                                <Label>Phone Number ID</Label>
                                <Input value={newTenantPhoneId} onChange={(e) => setNewTenantPhoneId(e.target.value)} placeholder="Phone Number ID" />
                            </div>
                            <div className="space-y-2">
                                <Label>Token (Permanente)</Label>
                                <Input value={newTenantToken} onChange={(e) => setNewTenantToken(e.target.value)} placeholder="Token de Acesso" type="password" />
                            </div>
                            <div className="space-y-2">
                                <Label>Webhook URL (Opcional)</Label>
                                <Input value={newTenantWebhook} onChange={(e) => setNewTenantWebhook(e.target.value)} placeholder="https://..." />
                            </div>
                            <Button onClick={handleCreate} className="w-full">Salvar</Button>
                        </div>
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Gerenciar Números</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Nome</TableHead>
                                <TableHead>API Key</TableHead>
                                <TableHead>Webhook</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="w-[100px]">Ações</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {tenants.map((tenant) => (
                                <TableRow key={tenant.id}>
                                    <TableCell>{tenant.name}</TableCell>
                                    <TableCell className="font-mono text-xs">{tenant.api_key}</TableCell>
                                    <TableCell>{tenant.webhook_url || "-"}</TableCell>
                                    <TableCell>
                                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${tenant.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                                            {tenant.is_active ? "Ativo" : "Inativo"}
                                        </span>
                                    </TableCell>
                                    <TableCell>
                                        <Button variant="ghost" size="icon" onClick={() => handleDelete(tenant.id)}>
                                            <Trash2 className="h-4 w-4 text-red-500" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {tenants.length === 0 && !loading && (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center text-muted-foreground">Nenhuma conexão encontrada.</TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
