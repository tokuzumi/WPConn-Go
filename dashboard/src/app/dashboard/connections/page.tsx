"use client";

import { useState, useEffect } from "react";
import { api, Tenant } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetTrigger } from "@/components/ui/sheet";
import { Switch } from "@/components/ui/switch";
import { Plus, Trash2, Edit } from "lucide-react";
import { toast } from "sonner";

export default function ConnectionsPage() {
    const [tenants, setTenants] = useState<Tenant[]>([]);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(1);
    const limit = 50;

    // Create State
    const [newTenantAlias, setNewTenantAlias] = useState("");
    const [newTenantWabaId, setNewTenantWabaId] = useState("");
    const [newTenantPhoneId, setNewTenantPhoneId] = useState("");
    const [newTenantToken, setNewTenantToken] = useState("");
    const [newTenantWebhook, setNewTenantWebhook] = useState("");
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    // Edit State
    const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null);
    const [isSheetOpen, setIsSheetOpen] = useState(false);
    const [editAlias, setEditAlias] = useState("");
    const [editWabaId, setEditWabaId] = useState("");
    const [editPhoneId, setEditPhoneId] = useState("");
    const [editToken, setEditToken] = useState("");
    const [editWebhook, setEditWebhook] = useState("");
    const [editIsActive, setEditIsActive] = useState(true);

    const apiKey = process.env.NEXT_PUBLIC_API_KEY || "admin-key";

    useEffect(() => {
        loadTenants();
    }, [page]);

    const loadTenants = async () => {
        setLoading(true);
        try {
            const data = await api.getTenants(apiKey, { limit, offset: (page - 1) * limit });
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
                alias: newTenantAlias,
                waba_id: newTenantWabaId,
                phone_number_id: newTenantPhoneId,
                token: newTenantToken,
                webhook_url: newTenantWebhook
            }, apiKey);

            toast.success("Connection created");
            setIsDialogOpen(false);
            loadTenants();

            // Reset form
            setNewTenantAlias("");
            setNewTenantWabaId("");
            setNewTenantPhoneId("");
            setNewTenantToken("");
            setNewTenantWebhook("");
        } catch (error) {
            console.error(error);
            toast.error("Failed to create connection");
        }
    };

    const handleEdit = (tenant: Tenant) => {
        setSelectedTenant(tenant);
        setEditAlias(tenant.alias || "");
        setEditWabaId(tenant.waba_id);
        setEditPhoneId(tenant.phone_number_id);
        setEditToken(""); // Don't show existing token for security, only allow overwrite
        setEditWebhook(tenant.webhook_url || "");
        setEditIsActive(tenant.is_active);
        setIsSheetOpen(true);
    };

    const handleUpdate = async () => {
        if (!selectedTenant) return;
        try {
            await api.updateTenant(selectedTenant.id, {
                alias: editAlias,
                waba_id: editWabaId,
                phone_number_id: editPhoneId,
                token: editToken || undefined, // Only send if not empty
                webhook_url: editWebhook,
                is_active: editIsActive
            }, apiKey);

            toast.success("Connection updated");
            setIsSheetOpen(false);
            loadTenants();
        } catch (error) {
            console.error(error);
            toast.error("Failed to update connection");
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

    const handleNextPage = () => setPage(p => p + 1);
    const handlePrevPage = () => setPage(p => Math.max(1, p - 1));

    return (
        <div className="p-4 pt-1 space-y-4">
            <div className="flex items-center justify-end">
                <Sheet open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <SheetTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" /> Novo Telefone
                        </Button>
                    </SheetTrigger>
                    <SheetContent>
                        <SheetHeader>
                            <SheetTitle>Nova Conexão WhatsApp</SheetTitle>
                            <SheetDescription>
                                Preencha os dados abaixo para conectar um novo número.
                            </SheetDescription>
                        </SheetHeader>
                        <div className="space-y-4 py-4 mt-4">
                            <div className="space-y-2">
                                <Label>Cliente (Alias)</Label>
                                <Input value={newTenantAlias} onChange={(e) => setNewTenantAlias(e.target.value)} placeholder="Ex: Divisão Sul" />
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
                    </SheetContent>
                </Sheet>
            </div>

            <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
                <SheetContent>
                    <SheetHeader>
                        <SheetTitle>Editar Conexão</SheetTitle>
                        <SheetDescription>
                            Atualize os dados da conexão.
                        </SheetDescription>
                    </SheetHeader>
                    <div className="space-y-4 py-4 mt-4">
                        <div className="flex items-center justify-between rounded-lg border p-3 shadow-sm">
                            <div className="space-y-0.5">
                                <Label>Status Ativo</Label>
                                <div className="text-[0.8rem] text-muted-foreground">
                                    Desative para parar de processar mensagens.
                                </div>
                            </div>
                            <Switch checked={editIsActive} onCheckedChange={setEditIsActive} />
                        </div>
                        <div className="space-y-2">
                            <Label>Cliente (Alias)</Label>
                            <Input value={editAlias} onChange={(e) => setEditAlias(e.target.value)} placeholder="Ex: Divisão Sul" />
                        </div>
                        <div className="space-y-2">
                            <Label>WABA ID</Label>
                            <Input value={editWabaId} onChange={(e) => setEditWabaId(e.target.value)} placeholder="WABA ID" />
                        </div>
                        <div className="space-y-2">
                            <Label>Phone Number ID</Label>
                            <Input value={editPhoneId} onChange={(e) => setEditPhoneId(e.target.value)} placeholder="Phone Number ID" />
                        </div>
                        <div className="space-y-2">
                            <Label>Token (Deixe em branco para manter)</Label>
                            <Input value={editToken} onChange={(e) => setEditToken(e.target.value)} placeholder="Novo Token (Opcional)" type="password" />
                        </div>
                        <div className="space-y-2">
                            <Label>Webhook URL</Label>
                            <Input value={editWebhook} onChange={(e) => setEditWebhook(e.target.value)} placeholder="https://..." />
                        </div>
                        <Button onClick={handleUpdate} className="w-full">Atualizar</Button>
                    </div>
                </SheetContent>
            </Sheet>

            <Card>
                <CardHeader>
                    <CardTitle>Gerenciar Números</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Cliente</TableHead>
                                <TableHead>API Key</TableHead>
                                <TableHead>Webhook</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="w-[50px]">Editar</TableHead>
                                <TableHead className="w-[50px]">Excluir</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {tenants.map((tenant) => (
                                <TableRow key={tenant.id}>
                                    <TableCell className="font-medium text-blue-600">{tenant.alias || "Sem Nome"}</TableCell>
                                    <TableCell className="font-mono text-xs">{tenant.api_key}</TableCell>
                                    <TableCell className="max-w-[200px] truncate" title={tenant.webhook_url}>{tenant.webhook_url || "-"}</TableCell>
                                    <TableCell>
                                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${tenant.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                                            {tenant.is_active ? "Ativo" : "Inativo"}
                                        </span>
                                    </TableCell>
                                    <TableCell>
                                        <Button variant="ghost" size="icon" onClick={() => handleEdit(tenant)}>
                                            <Edit className="h-4 w-4" />
                                        </Button>
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
                                    <TableCell colSpan={6} className="text-center text-muted-foreground">Nenhuma conexão encontrada.</TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>

                    <div className="flex justify-end gap-2 mt-4">
                        <Button variant="outline" onClick={handlePrevPage} disabled={page === 1 || loading}>
                            Anterior
                        </Button>
                        <Button variant="outline" onClick={handleNextPage} disabled={tenants.length < limit || loading}>
                            Próxima
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
