"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EventHealth } from "@/services/api";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from "recharts";

interface EventHealthChartProps {
    data: EventHealth[];
}

const COLORS = {
    processed: "#22c55e", // green-500
    failed: "#ef4444",    // red-500
    pending: "#eab308",   // yellow-500
    processing: "#3b82f6" // blue-500
};

export function EventHealthChart({ data }: EventHealthChartProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Saúde do Processamento de Eventos</CardTitle>
            </CardHeader>
            <CardContent>
                {data.length === 0 ? (
                    <div className="flex h-[300px] items-center justify-center text-muted-foreground">
                        Sem dados registrados
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis
                                dataKey="status"
                                stroke="#888888"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(value) => value.charAt(0).toUpperCase() + value.slice(1)}
                            />
                            <YAxis
                                stroke="#888888"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                            />
                            <Tooltip
                                cursor={{ fill: 'transparent' }}
                                contentStyle={{ borderRadius: '8px' }}
                            />
                            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                                {data.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={COLORS[entry.status as keyof typeof COLORS] || "#8884d8"}
                                    />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                )}
            </CardContent>
        </Card>
    );
}
