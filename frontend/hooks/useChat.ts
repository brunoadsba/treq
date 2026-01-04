"use client";

import { useState, useCallback, useRef, useEffect } from "react";

export interface ChartData {
  type: "bar_chart" | "pie_chart" | "line_chart";
  title: string;
  subtitle?: string;
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor?: string | string[];
      borderColor?: string | string[];
      borderWidth?: number;
      type?: "line" | "bar";
      tension?: number;
    }>;
  };
  options?: {
    responsive?: boolean;
    maintainAspectRatio?: boolean;
    scales?: any;
    plugins?: any;
  };
  metadata?: {
    period?: string;
    unit?: string;
    total_alerts?: number;
    last_updated?: string;
    empty?: boolean;
    message?: string;
  };
}

export interface ReasoningPlan {
  intent: string;
  context_status: string;
  context_analysis: string;
  missing_info: string[];
  strategy: string;
  needs_visualization: boolean;
  visualization_type: string | null;
  reasoning_steps: string[];
  key_entities: string[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  chartData?: ChartData;
  reasoning?: ReasoningPlan;
  runId?: string;
  isThinking?: boolean;
  thinkingDuration?: number;
  imageUrl?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id?: string;
  context_summary: string;
  sources: Array<{
    content: string;
    similarity: number;
    metadata: Record<string, any>;
  }>;
  fallback?: boolean;
  fallback_reason?: string;
  fallback_message?: string;
  chart_data?: ChartData;
  reasoning?: ReasoningPlan;
  run_id?: string;
}

export interface SavedConversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  conversationId: string | null;
  createdAt: string;
  updatedAt: string;
}

export function useChat(userId: string = "default-user") {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);

  // Ref para rastrear requisição em andamento (previne race conditions)
  const isRequestInProgressRef = useRef(false);
  // Ref para armazenar AbortController do stream atual
  const currentStreamAbortControllerRef = useRef<AbortController | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

  // Função para obter conversas salvas (definida ANTES de ser usada)
  const getSavedConversations = useCallback((): SavedConversation[] => {
    if (typeof window === "undefined") return [];

    try {
      const conversations = JSON.parse(
        localStorage.getItem(`chat_conversations_${userId}`) || "[]"
      ) as SavedConversation[];
      return conversations;
    } catch (error) {
      console.error("Erro ao carregar conversas salvas:", error);
      return [];
    }
  }, [userId]);

  // Salvar conversa atual antes de fechar/recarregar a página
  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleBeforeUnload = () => {
      // Salvar conversa atual no histórico antes de fechar
      if (messages.length > 0) {
        const conversations = getSavedConversations();
        const firstUserMessage = messages.find(m => m.role === "user");
        const title = firstUserMessage?.content.substring(0, 50) || "Nova conversa";

        const conversationIdToUse = currentConversationId || `conv_${Date.now()}`;
        const existingIndex = conversations.findIndex(c => c.id === conversationIdToUse);

        const conversation: SavedConversation = {
          id: conversationIdToUse,
          title,
          messages: [...messages],
          conversationId,
          createdAt: messages[0]?.timestamp || new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };

        if (existingIndex >= 0) {
          conversations[existingIndex] = conversation;
        } else {
          conversations.unshift(conversation);
        }

        // Limitar a 50 conversas mais recentes
        const limitedConversations = conversations.slice(0, 50);
        localStorage.setItem(`chat_conversations_${userId}`, JSON.stringify(limitedConversations));
      }

      // Limpar dados da conversa atual para que na próxima abertura comece do zero
      localStorage.removeItem(`chat_messages_${userId}`);
      localStorage.removeItem(`chat_conversation_${userId}`);
      localStorage.removeItem(`chat_current_frontend_conversation_id_${userId}`);
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      // Também salvar ao desmontar o componente (navegação SPA)
      handleBeforeUnload();
    };
  }, [messages, conversationId, userId, currentConversationId, getSavedConversations]);

  // NÃO carregar conversa automaticamente ao montar - sempre iniciar com tela de boas-vindas
  // As conversas anteriores estão disponíveis no histórico via getSavedConversations()

  // Persistir mensagens em tempo real (debounce para evitar salvamentos excessivos)
  useEffect(() => {
    if (typeof window === "undefined" || messages.length === 0) return;

    // Debounce: salvar após 2 segundos sem mudanças
    const timeoutId = setTimeout(() => {
      const conversations = getSavedConversations();
      const firstUserMessage = messages.find(m => m.role === "user");
      const title = firstUserMessage?.content.substring(0, 50) || "Nova conversa";

      // Usar currentConversationId se existir, senão criar novo
      const conversationIdToUse = currentConversationId || `conv_${Date.now()}`;
      const existingIndex = conversations.findIndex(c => c.id === conversationIdToUse);

      const conversation: SavedConversation = {
        id: conversationIdToUse,
        title,
        messages: [...messages],
        conversationId,
        createdAt: messages[0]?.timestamp || new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      if (existingIndex >= 0) {
        conversations[existingIndex] = conversation;
      } else {
        conversations.unshift(conversation);
        if (!currentConversationId) {
          setCurrentConversationId(conversationIdToUse);
        }
      }

      // Limitar a 50 conversas mais recentes
      const limitedConversations = conversations.slice(0, 50);
      localStorage.setItem(`chat_conversations_${userId}`, JSON.stringify(limitedConversations));
    }, 2000); // 2 segundos de debounce

    return () => clearTimeout(timeoutId);
  }, [messages, conversationId, userId, currentConversationId, getSavedConversations]);

  // Limpar histórico quando usuário deslogar
  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleLogout = () => {
      localStorage.removeItem(`chat_messages_${userId}`);
      localStorage.removeItem(`chat_conversation_${userId}`);
      setMessages([]);
      setConversationId(null);
    };

    window.addEventListener("user_logout", handleLogout);
    return () => {
      window.removeEventListener("user_logout", handleLogout);
    };
  }, [userId]);

  const sendMessage = useCallback(
    async (
      message: string,
      context?: Record<string, any>,
      useStream: boolean = true,
      visualization?: boolean,
      actionId?: string,
      imageUrl?: string
    ) => {
      if (!message.trim()) return;

      // Bloquear envios concorrentes (race condition fix)
      if (isRequestInProgressRef.current) {
        console.warn("Requisição já em andamento, ignorando novo envio");
        return;
      }

      isRequestInProgressRef.current = true;
      setIsLoading(true);
      setError(null);

      // Adicionar mensagem do usuário imediatamente
      const userMessage: ChatMessage = {
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
        imageUrl: imageUrl
      };

      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message,
            history: messages.map(m => ({
              role: m.role,
              content: m.content
            })),
          }),
        });

        if (!response.ok) {
          throw new Error("Falha ao comunicar com o assistente");
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("Stream não habilitado");

        const decoder = new TextDecoder();
        let fullResponse = "";

        // Adicionar mensagem do assistente vazia para streaming
        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: "",
          timestamp: new Date().toISOString(),
          isThinking: true,
        };
        setMessages((prev) => [...prev, assistantMessage]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          fullResponse += chunk;

          setMessages((prev) =>
            prev.map((msg, idx) =>
              idx === prev.length - 1 && msg.role === "assistant"
                ? {
                  ...msg,
                  content: fullResponse,
                  isThinking: false,
                }
                : msg
            )
          );
        }

        return {
          response: fullResponse,
          conversation_id: conversationId || undefined,
          context_summary: "",
          sources: [],
        };
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Erro desconhecido";
        setError(errorMessage);

        // Remover mensagem vazia do assistente se existir
        setMessages((prev) => prev.filter((msg) => msg.content !== "" || msg.role !== "assistant"));

        // Adicionar mensagem de erro apenas se não for aborto intencional
        if (!(err instanceof Error && err.name === "AbortError")) {
          const errorMessageObj: ChatMessage = {
            role: "assistant",
            content: `❌ Erro: ${errorMessage}`,
            timestamp: new Date().toISOString(),
          };

          setMessages((prev) => [...prev, errorMessageObj]);
        }

        throw err; // Re-throw para permitir tratamento externo
      } finally {
        isRequestInProgressRef.current = false;
        setIsLoading(false);
      }
    },
    [apiUrl, userId, conversationId, currentConversationId]
  );

  // Cleanup: cancelar stream ao desmontar componente
  useEffect(() => {
    return () => {
      if (currentStreamAbortControllerRef.current) {
        currentStreamAbortControllerRef.current.abort();
      }
    };
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    setCurrentConversationId(null);

    // Limpar também do localStorage
    if (typeof window !== "undefined") {
      localStorage.removeItem(`chat_messages_${userId}`);
      localStorage.removeItem(`chat_conversation_${userId}`);
    }
  }, [userId]);

  // Função para salvar conversa atual antes de iniciar nova
  const saveCurrentConversation = useCallback((): string | null => {
    if (typeof window === "undefined" || messages.length === 0) return null;

    const conversations = getSavedConversations();
    const firstUserMessage = messages.find(m => m.role === "user");
    const title = firstUserMessage?.content.substring(0, 50) || "Nova conversa";

    const conversation: SavedConversation = {
      id: currentConversationId || `conv_${Date.now()}`,
      title,
      messages: [...messages],
      conversationId,
      createdAt: messages[0]?.timestamp || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    // Atualizar se já existe, senão adicionar
    const existingIndex = conversations.findIndex(c => c.id === conversation.id);
    if (existingIndex >= 0) {
      conversations[existingIndex] = conversation;
    } else {
      conversations.unshift(conversation);
    }

    // Limitar a 50 conversas mais recentes
    const limitedConversations = conversations.slice(0, 50);
    localStorage.setItem(`chat_conversations_${userId}`, JSON.stringify(limitedConversations));

    return conversation.id;
  }, [messages, conversationId, userId, currentConversationId, getSavedConversations]);

  // Função para iniciar nova conversa (salva atual e limpa tela)
  const startNewConversation = useCallback(() => {
    if (messages.length > 0) {
      saveCurrentConversation();
    }

    setMessages([]);
    setConversationId(null);
    setError(null);
    setCurrentConversationId(null);

    // Limpar localStorage da conversa atual para garantir estado limpo
    if (typeof window !== "undefined") {
      localStorage.removeItem(`chat_messages_${userId}`);
      localStorage.removeItem(`chat_conversation_${userId}`);
      localStorage.removeItem(`chat_current_frontend_conversation_id_${userId}`);
    }
  }, [messages, saveCurrentConversation, userId]);

  // Função para carregar conversa salva
  const loadConversation = useCallback((conversationId: string) => {
    if (typeof window === "undefined") return;

    const conversations = getSavedConversations();
    const conversation = conversations.find(c => c.id === conversationId);

    if (conversation) {
      setMessages(conversation.messages);
      setConversationId(conversation.conversationId);
      setCurrentConversationId(conversation.id);
      setError(null);

      // Atualizar localStorage para manter sincronização (mas não será carregado automaticamente na próxima abertura)
      localStorage.setItem(`chat_messages_${userId}`, JSON.stringify(conversation.messages));
      if (conversation.conversationId) {
        localStorage.setItem(`chat_conversation_${userId}`, conversation.conversationId);
      }
      localStorage.setItem(`chat_current_frontend_conversation_id_${userId}`, conversation.id);
    }
  }, [getSavedConversations, userId]);

  // Função para deletar conversa
  const deleteConversation = useCallback((conversationId: string) => {
    if (typeof window === "undefined") return;

    const conversations = getSavedConversations();
    const filtered = conversations.filter(c => c.id !== conversationId);
    localStorage.setItem(`chat_conversations_${userId}`, JSON.stringify(filtered));

    // Se for a conversa atual, limpar tela
    if (currentConversationId === conversationId) {
      setMessages([]);
      setConversationId(null);
      setCurrentConversationId(null);
    }
  }, [userId, currentConversationId, getSavedConversations]);

  // Função para exportar conversa
  const exportConversation = useCallback((conversationId?: string): string => {
    const targetConversationId = conversationId || currentConversationId;
    if (!targetConversationId) {
      // Exportar conversa atual se não houver ID
      const exportData = {
        title: messages.find(m => m.role === "user")?.content.substring(0, 50) || "Nova conversa",
        messages,
        conversationId,
        exportedAt: new Date().toISOString(),
      };
      return JSON.stringify(exportData, null, 2);
    }

    const conversations = getSavedConversations();
    const conversation = conversations.find(c => c.id === targetConversationId);

    if (conversation) {
      const exportData = {
        title: conversation.title,
        messages: conversation.messages,
        conversationId: conversation.conversationId,
        createdAt: conversation.createdAt,
        updatedAt: conversation.updatedAt,
        exportedAt: new Date().toISOString(),
      };
      return JSON.stringify(exportData, null, 2);
    }

    return "";
  }, [messages, conversationId, currentConversationId, getSavedConversations]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    conversationId,
    currentConversationId,
    startNewConversation,
    saveCurrentConversation,
    loadConversation,
    deleteConversation,
    getSavedConversations,
    exportConversation,
  };
}

