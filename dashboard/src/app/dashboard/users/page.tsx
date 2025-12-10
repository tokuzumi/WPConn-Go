"use client";

import { useState, useEffect } from "react";
import { api, User } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetTrigger } from "@/components/ui/sheet";
import { Plus, Trash2, User as UserIcon } from "lucide-react";
import { toast } from "sonner";

export default function UsersPage() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(false);

    const [newName, setNewName] = useState("");
    const [newEmail, setNewEmail] = useState("");
    const [newPassword, setNewPassword] = useState("");

    const [isDialogOpen, setIsDialogOpen] = useState(false);

    const apiKey = process.env.NEXT_PUBLIC_API_KEY || "admin-key";

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        setLoading(true);
        try {
            const data = await api.getUsers(apiKey);
            setUsers(data);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load users");
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async () => {
        try {
            await api.createUser({
                name: newName,
                email: newEmail,
                password: newPassword,
                role: "user"
            }, apiKey);

            toast.success("User created");
            setIsDialogOpen(false);
            loadUsers();

            setNewName("");
            setNewEmail("");
            setNewPassword("");
        } catch (error) {
            console.error(error);
            toast.error("Failed to create user");
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure?")) return;
        try {
            await api.deleteUser(id, apiKey);
            toast.success("User deleted");
            loadUsers();
        } catch (error) {
            console.error(error);
            toast.error("Failed to delete user");
        }
    };

    return (
        <div className="p-4 pt-1 space-y-4">
            <div className="flex items-center justify-end">
                <Sheet open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <SheetTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" /> Novo Usuário
                        </Button>
                    </SheetTrigger>
                    <SheetContent>
                        <SheetHeader>
                            <SheetTitle>Novo Usuário</SheetTitle>
                            <SheetDescription>
                                Crie um novo usuário para acessar o dashboard.
                            </SheetDescription>
                        </SheetHeader>
                        <div className="space-y-4 py-4 mt-4">
                            <div className="space-y-2">
                                <Label>Nome</Label>
                                <Input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Nome completo" />
                            </div>
                            <div className="space-y-2">
                                <Label>Email</Label>
                                <Input value={newEmail} onChange={(e) => setNewEmail(e.target.value)} placeholder="email@exemplo.com" type="email" />
                            </div>
                            <div className="space-y-2">
                                <Label>Senha</Label>
                                <Input value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="******" type="password" />
                            </div>
                            <Button onClick={handleCreate} className="w-full">Salvar</Button>
                        </div>
                    </SheetContent>
                </Sheet>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Gerenciar Acesso</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Nome</TableHead>
                                <TableHead>Email</TableHead>
                                <TableHead>Role</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="w-[100px]">Ações</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {users.map((user) => (
                                <TableRow key={user.id}>
                                    <TableCell className="font-medium flex items-center gap-2">
                                        <UserIcon className="h-4 w-4 text-muted-foreground" />
                                        {user.name}
                                    </TableCell>
                                    <TableCell>{user.email}</TableCell>
                                    <TableCell>
                                        <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                                            {user.role}
                                        </span>
                                    </TableCell>
                                    <TableCell>
                                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${user.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                                            {user.is_active ? "Ativo" : "Inativo"}
                                        </span>
                                    </TableCell>
                                    <TableCell>
                                        <Button variant="ghost" size="icon" onClick={() => handleDelete(user.id)}>
                                            <Trash2 className="h-4 w-4 text-red-500" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {users.length === 0 && !loading && (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                                        Nenhum usuário encontrado.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
