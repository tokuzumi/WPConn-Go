"use client";

import React, { useState, useEffect } from "react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, User, Code } from "lucide-react";
import { DetailedHostessSession, getHostessSessionDetails } from "@/lib/mock-data";
import { useTenant } from "@/context/tenant-context";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";

interface SessionDetailsSheetProps {
  sessionId: number;
  children: React.ReactNode;
}

const parseMessageString = (item: string) => {
  try {
    const parsed = JSON.parse(item);
    return parsed;
  } catch (e) {
    const roleMatch = item.match(/role='(user|assistant)'/);
    const contentMatch = item.match(/content=\['(.*?)'\]/);
    const typeMatch = item.match(/type='(message|function_call_output)'/);

    if (roleMatch && contentMatch && typeMatch) {
      return {
        type: typeMatch[1],
        role: roleMatch[1],
        content: contentMatch[1],
      };
    }
  }
  return null;
};

const ConversationHistory = ({ history }: { history: any[] }) => {
  if (!history || history.length === 0) {
    return <p className="text-sm text-muted-foreground italic">Nenhum histórico de conversa disponível.</p>;
  }

  return (
    <div className="space-y-4">
      {history.map((item, index) => {
        const parsed = parseMessageString(item);
        if (!parsed) return null;

        if (parsed.type === 'message') {
          const isUser = parsed.role === 'user';
          return (
            <div key={index} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-3 rounded-lg shadow-sm ${isUser ? 'bg-primary text-primary-foreground rounded-br-none' : 'bg-muted text-foreground rounded-tl-none'}`}>
                <p className="text-xs font-semibold mb-1 flex items-center gap-1">
                  {isUser ? <User className="size-3" /> : <MessageSquare className="size-3" />}
                  {isUser ? 'Usuário' : 'IA'}
                </p>
                <p className="text-sm whitespace-pre-wrap">{parsed.content}</p>
              </div>
            </div>
          );
        }

        if (parsed.type === 'function_call') {
          return (
            <div key={index} className="flex justify-start">
              <div className="max-w-[80%] p-2 rounded-lg border border-dashed bg-accent text-accent-foreground text-xs italic">
                <p className="font-semibold flex items-center gap-1 mb-1">
                  <Code className="size-3 text-muted-foreground" />
                  Chamada de Função: {parsed.name}
                </p>
                <pre className="whitespace-pre-wrap text-[10px] text-muted-foreground">
                  {parsed.arguments}
                </pre>
              </div>
            </div>
          );
        }
        return null;
      })}
    </div>
  );
};

const DetailsSkeleton = () => (
  <div className="flex flex-col gap-4 p-4">
    <Skeleton className="h-6 w-3/4" />
    <Skeleton className="h-4 w-1/2" />
    <Separator />
    <div className="grid grid-cols-2 gap-3">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="flex flex-col gap-1">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-4 w-16" />
        </div>
      ))}
    </div>
    <Separator />
    <Skeleton className="h-4 w-1/3" />
    <div className="space-y-3">
      <Skeleton className="h-16 w-full" />
      <Skeleton className="h-16 w-full" />
    </div>
  </div>
);

export function SessionDetailsSheet({ sessionId, children }: SessionDetailsSheetProps) {
  const { clientId } = useTenant();
  const [sessionDetails, setSessionDetails] = useState<DetailedHostessSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const fetchDetails = async (id: number) => {
    if (!clientId) return;
    setIsLoading(true);
    const data = await getHostessSessionDetails(id, clientId);
    setSessionDetails(data);
    setIsLoading(false);
  };

  useEffect(() => {
    if (isOpen && sessionId) {
      fetchDetails(sessionId);
    }
  }, [isOpen, sessionId, clientId]);

  const startTime = sessionDetails?.session_start_time ? new Date(sessionDetails.session_start_time) : null;
  const formattedDate = startTime ? format(startTime, 'dd/MM/yyyy', { locale: ptBR }) : 'N/A';
  const formattedTime = startTime ? format(startTime, 'HH:mm:ss') : 'N/A';
  const status = sessionDetails ? 'Concluída' : 'Erro';

  const renderDetails = () => {
    if (isLoading) return <DetailsSkeleton />;
    if (!sessionDetails) return <div className="p-4 text-center text-muted-foreground">Detalhes da sessão não encontrados.</div>;

    return (
      <ScrollArea className="h-full p-4">
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex flex-col"><span className="font-medium text-muted-foreground">Duração Total</span><span className="font-semibold text-foreground">{sessionDetails.session_duration} segundos</span></div>
            <div className="flex flex-col"><span className="font-medium text-muted-foreground">Status</span><Badge variant="secondary" className="w-fit mt-1">{status}</Badge></div>
            <div className="flex flex-col"><span className="font-medium text-muted-foreground">Tokens de Entrada (LLM)</span><span className="font-semibold text-foreground">{sessionDetails.llm_input_tokens_total?.toLocaleString('pt-BR') || '0'}</span></div>
            <div className="flex flex-col"><span className="font-medium text-muted-foreground">Tokens de Saída (LLM)</span><span className="font-semibold text-foreground">{sessionDetails.llm_output_tokens_total?.toLocaleString('pt-BR') || '0'}</span></div>
          </div>
          <Separator />
          <div className="flex flex-col gap-3">
            <h4 className="font-semibold text-lg flex items-center gap-2 text-foreground"><MessageSquare className="size-5 text-primary" />Transcrição e Histórico</h4>
            <ConversationHistory history={sessionDetails.conversation_history || []} />
          </div>
        </div>
      </ScrollArea>
    );
  };

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>{children}</SheetTrigger>
      <SheetContent className="sm:max-w-md w-full flex flex-col">
        <SheetHeader>
          <SheetTitle>Detalhes da Sessão #{sessionId}</SheetTitle>
          <SheetDescription>Iniciada em {formattedDate} às {formattedTime}</SheetDescription>
        </SheetHeader>
        <div className="flex-grow overflow-hidden">{renderDetails()}</div>
      </SheetContent>
    </Sheet>
  );
}