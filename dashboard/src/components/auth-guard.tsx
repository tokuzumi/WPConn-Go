"use client";

import { useEffect } from "react";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";

export function AuthGuard({ children }: { children: React.ReactNode }) {
    const { isAuthenticated } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isAuthenticated) {
            router.push("/login");
        }
    }, [isAuthenticated, router]);

    if (!isAuthenticated) {
        return null; // or a loading spinner
    }

    return <>{children}</>;
}
