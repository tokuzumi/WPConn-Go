const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface Tenant {
    id: string;
    name: string;
    waba_id: string;
    phone_number_id: string;
    webhook_url?: string;
    api_key: string;
    is_active: boolean;
    created_at: string;
}

export interface CreateTenantData {
    name: string;
    waba_id: string;
    phone_number_id: string;
    token: string;
    webhook_url?: string;
}

export interface Message {
    id: string;
    wamid: string;
    phone: string;
    direction: "inbound" | "outbound";
    type: string;
    status: string;
    content?: string;
    media_url?: string;
    media_type?: string;
    caption?: string;
    created_at: string;
}

export interface Log {
    id: number;
    tenant_id?: string;
    event: string;
    detail?: string;
    created_at: string;
}

export interface User {
    id: string;
    email: string;
    name: string;
    role: string;
    is_active: boolean;
    created_at: string;
}

export interface CreateUserData {
    email: string;
    password: string;
    name: string;
    role?: string;
}

export const api = {
    getTenants: async (apiKey: string): Promise<Tenant[]> => {
        const response = await fetch(`${API_URL}/tenants`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });
        if (!response.ok) throw new Error("Failed to fetch tenants");
        return response.json();
    },

    createTenant: async (data: CreateTenantData, apiKey: string): Promise<Tenant> => {
        const response = await fetch(`${API_URL}/tenants`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": apiKey,
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error("Failed to create tenant");
        return response.json();
    },

    deleteTenant: async (tenantId: string, apiKey: string): Promise<void> => {
        const response = await fetch(`${API_URL}/tenants/${tenantId}`, {
            method: "DELETE",
            headers: {
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) throw new Error("Failed to delete tenant");
    },

    getMessages: async (apiKey: string, params?: { phone?: string; search?: string; limit?: number; offset?: number }): Promise<Message[]> => {
        const query = new URLSearchParams();
        if (params?.phone) query.append("phone", params.phone);
        if (params?.search) query.append("search", params.search);
        if (params?.limit) query.append("limit", params.limit.toString());
        if (params?.offset) query.append("offset", params.offset.toString());

        const response = await fetch(`${API_URL}/messages?${query.toString()}`, {
            method: "GET",
            headers: {
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) throw new Error("Failed to fetch messages");
        return response.json();
    },

    getLogs: async (apiKey: string, params?: { event?: string; limit?: number; offset?: number }): Promise<Log[]> => {
        const query = new URLSearchParams();
        if (params?.event) query.append("event", params.event);
        if (params?.limit) query.append("limit", params.limit.toString());
        if (params?.offset) query.append("offset", params.offset.toString());

        const response = await fetch(`${API_URL}/logs?${query.toString()}`, {
            method: "GET",
            headers: {
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) throw new Error("Failed to fetch logs");
        return response.json();
    },

    getUsers: async (apiKey: string): Promise<User[]> => {
        const response = await fetch(`${API_URL}/users`, {
            method: "GET",
            headers: {
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) throw new Error("Failed to fetch users");
        return response.json();
    },

    createUser: async (data: CreateUserData, apiKey: string): Promise<User> => {
        const response = await fetch(`${API_URL}/users`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": apiKey,
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error("Failed to create user");
        return response.json();
    },

    deleteUser: async (userId: string, apiKey: string): Promise<void> => {
        const response = await fetch(`${API_URL}/users/${userId}`, {
            method: "DELETE",
            headers: {
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) throw new Error("Failed to delete user");
    }
};
