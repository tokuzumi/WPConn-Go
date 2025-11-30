"use client";

import { useState } from "react";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Image from "next/image";

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const { login } = useAuth();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (username === "admin" && password === "admin") {
            login(username);
        } else {
            alert("Invalid credentials");
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-4 h-screen w-full">
            {/* Background Image Column (3/4 width on large screens) */}
            <div className="hidden lg:block lg:col-span-3 relative bg-black">
                <Image
                    src="https://res.cloudinary.com/dco1sm3hy/image/upload/v1764468905/WPConn_login_bg_q59ozz.jpg"
                    alt="Login Background"
                    fill
                    className="object-cover opacity-80"
                    priority
                />
                <div className="absolute inset-0 bg-gradient-to-r from-black/50 to-transparent pointer-events-none" />
            </div>

            {/* Login Form Column (1/4 width on large screens) */}
            <div className="lg:col-span-1 flex items-center justify-center bg-background p-8">
                <div className="w-full max-w-[350px] space-y-6">
                    <div className="space-y-2 text-center">
                        <h1 className="text-2xl font-bold tracking-tight">WPConn</h1>
                        <div className="h-[1px] w-full bg-border" />
                    </div>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                id="username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="bg-secondary/50 border-0 focus-visible:ring-1"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="bg-secondary/50 border-0 focus-visible:ring-1"
                            />
                        </div>
                        <Button type="submit" className="w-full font-semibold">
                            Sign In
                        </Button>
                    </form>
                    <p className="text-xs text-center text-muted-foreground">
                        Desenvolvido por TkzM AI Studio
                    </p>
                </div>
            </div>
        </div>
    );
}
