import { format, startOfDay, endOfDay, startOfWeek, endOfWeek, startOfMonth, endOfMonth, subMonths, subMinutes, subSeconds } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export interface HostessSession {
  id: number;
  date: string;
  time: string;
  status: 'Concluído' | 'Erro';
  durationSeconds: number;
  hasPendingIssues: boolean;
}

export interface DetailedHostessSession {
  id: number;
  session_start_time: string;
  session_end_time: string | null;
  session_duration: number;
  llm_input_tokens_total: number | null;
  llm_output_tokens_total: number | null;
  conversation_history: any[];
}

// --- Mock Data Generation ---

const generateMockSession = (id: number, date: Date): HostessSession => {
  const duration = Math.floor(Math.random() * 300) + 15; // 15s to 315s
  return {
    id,
    date: format(date, 'dd MMM, yyyy', { locale: ptBR }),
    time: format(date, 'HH:mm'),
    status: Math.random() > 0.1 ? 'Concluído' : 'Erro',
    durationSeconds: duration,
    hasPendingIssues: Math.random() > 0.8,
  };
};

const generateDetailedMockSession = (id: number): DetailedHostessSession => {
    const now = new Date();
    const duration = Math.floor(Math.random() * 280) + 20;
    const startTime = subSeconds(now, duration + id * 60);
    const endTime = subSeconds(now, id * 60);

    return {
        id,
        session_start_time: startTime.toISOString(),
        session_end_time: endTime.toISOString(),
        session_duration: duration,
        llm_input_tokens_total: Math.floor(Math.random() * 1000) + 500,
        llm_output_tokens_total: Math.floor(Math.random() * 800) + 400,
        conversation_history: [
            { type: 'message', role: 'user', content: 'Olá, qual o status do meu pedido?' },
            { type: 'function_call', name: 'check_order_status', arguments: '{ "order_id": "12345" }' },
            "type='function_call_output' role='assistant' content='{\"status\": \"enviado\"}'",
            { type: 'message', role: 'assistant', content: 'Seu pedido #12345 já foi enviado.' },
            { type: 'message', role: 'user', content: 'Ótimo, obrigado!' },
        ].map(item => typeof item === 'string' ? item : JSON.stringify(item)),
    };
};


// --- Mock API Functions ---

export async function getRecentHostessSessions(clientId: string): Promise<HostessSession[]> {
  const now = new Date();
  return [
    generateMockSession(101, subMinutes(now, 5)),
    generateMockSession(102, subMinutes(now, 25)),
    generateMockSession(103, subMinutes(now, 75)),
    generateMockSession(104, subMinutes(now, 120)),
    generateMockSession(105, subMinutes(now, 240)),
  ];
}

export async function getHostessSessionDetails(sessionId: number, clientId: string): Promise<DetailedHostessSession | null> {
    return generateDetailedMockSession(sessionId);
}

export async function getTotalSessionsCount(clientId: string): Promise<number> {
  return 1843;
}

export async function getTodaySessionsCount(clientId: string): Promise<number> {
  return 27;
}

export async function getWeekSessionsCount(clientId: string): Promise<number> {
  return 192;
}

export async function getMonthSessionsCount(clientId: string): Promise<number> {
  return 789;
}

export async function getMonthlySessionsChartData(clientId: string, months: number = 6): Promise<{ month: string, count: number }[]> {
  const results: { month: string, count: number }[] = [];
  const today = new Date();
  for (let i = months - 1; i >= 0; i--) {
    const date = subMonths(today, i);
    results.push({
      month: format(date, 'MMM/yy', { locale: ptBR }),
      count: Math.floor(Math.random() * 500) + 200,
    });
  }
  return results;
}

export async function getLastSessionsDuration(clientId: string, limit: number = 15): Promise<{ id: number, duration: number }[]> {
  const results: { id: number, duration: number }[] = [];
  for (let i = 0; i < limit; i++) {
    results.push({
      id: 200 + i,
      duration: Math.floor(Math.random() * 250) + 30,
    });
  }
  return results;
}