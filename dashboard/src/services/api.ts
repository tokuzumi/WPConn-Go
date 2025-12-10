let API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Force HTTPS if the page is loaded over HTTPS
if (typeof window !== 'undefined' && window.location.protocol === 'https:' && API_URL.startsWith('http://')) {
    API_URL = API_URL.replace('http://', 'https://');
}


export interface Tenant {
    id: string;
    name: string;
    alias?: string;
    waba_id: string;
    phone_number_id: string;
    webhook_url?: string;
    api_key: string;
    is_active: boolean;
    created_at: string;
}

export interface CreateTenantData {
    name: string;
    alias?: string;
    waba_id: string;
    phone_number_id: string;
    token: string;
    webhook_url?: string;
}

export interface Message {
    id: string;
    tenant_phone_id?: string;
    tenant_alias?: string;
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

export interface KPIData {
    pending_webhooks: number;
    error_rate_24h: number;
    daily_messages: number;
    active_tenants: number;
}

export interface HourlyTraffic {
    hour: string;
    inbound: number;
    outbound: number;
}

export interface MessageStatusDistribution {
    status: string;
    count: number;
}

export interface EventHealth {
    status: string;
    count: number;
}

export interface CriticalError {
    id: number;
    tenant_name: string;
    event: string;
    detail: string;
    created_at: string;
}

export interface DashboardStatsResponse {
    kpis: KPIData;
    hourly_traffic: HourlyTraffic[];
    status_distribution: MessageStatusDistribution[];
    event_health: EventHealth[];
    recent_errors: CriticalError[];
}

export interface TenantUpdateData {
    name?: string;
    alias?: string;
    waba_id?: string;
    phone_number_id?: string;
    token?: string;
    webhook_url?: string;
    is_active?: boolean;
}

export const api = {
    getTenants: async (apiKey: string, params?: { limit?: number; offset?: number }): Promise<Tenant[]> => {
        const query = new URLSearchParams();
        if (params?.limit) query.append("limit", params.limit.toString());
        if (params?.offset) query.append("offset", params.offset.toString());

        const response = await fetch(`${API_URL}/tenants/?${query.toString()}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) throw new Error("Failed to fetch tenants");
        return response.json();
    },

    updateTenant: async (id: string, data: TenantUpdateData, apiKey: string): Promise<Tenant> => {
        const response = await fetch(`${API_URL}/tenants/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": apiKey,
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error("Failed to update tenant");
        return response.json();
    },

    createTenant: async (data: CreateTenantData, apiKey: string): Promise<Tenant> => {
        const response = await fetch(`${API_URL}/tenants/`, {
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

        const response = await fetch(`${API_URL}/messages/?${query.toString()}`, {
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

        const response = await fetch(`${API_URL}/logs/?${query.toString()}`, {
            method: "GET",
            headers: {
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) throw new Error("Failed to fetch logs");
        return response.json();
    },

    retryWebhook: async (logId: number, apiKey: string): Promise<any> => {
        const response = await fetch(`${API_URL}/logs/${logId}/retry`, {
            method: "POST",
            headers: {
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Failed to retry webhook");
        }
        return response.json();
    },

    getUsers: async (apiKey: string): Promise<User[]> => {
        const response = await fetch(`${API_URL}/users/`, {
            method: "GET",
            headers: {
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) throw new Error("Failed to fetch users");
        return response.json();
    },

    createUser: async (user: CreateUserData, apiKey: string): Promise<User> => {
        const response = await fetch(`${API_URL}/users/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": apiKey,
            },
            body: JSON.stringify(user),
        });
        if (!response.ok) throw new Error("Failed to create user");
        return response.json();
    },

    deleteUser: async (id: string, apiKey: string): Promise<void> => {
        const response = await fetch(`${API_URL}/users/${id}`, {
            method: "DELETE",
            headers: {
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) throw new Error("Failed to delete user");
    },

    login: async (email: string, password: string): Promise<User> => {
        const response = await fetch(`${API_URL}/users/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        });
        if (!response.ok) throw new Error("Invalid credentials");
        return response.json();
    },

    getDashboardStats: async (apiKey: string): Promise<DashboardStatsResponse> => {
        const response = await fetch(`${API_URL}/dashboard/stats`, {
            method: "GET",
            headers: {
                "x-api-key": apiKey,
            },
        });
        if (!response.ok) throw new Error("Failed to fetch dashboard stats");
        return response.json();
    }
};
