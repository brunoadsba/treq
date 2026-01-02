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
      actionId?: string
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

      // Variável para armazenar mensagem de fallback
      let fallbackMessage: string | undefined = undefined;

      // Cancelar stream anterior se existir
      if (currentStreamAbortControllerRef.current) {
        currentStreamAbortControllerRef.current.abort();
        currentStreamAbortControllerRef.current = null;
      }

      // Adicionar mensagem do usuário imediatamente
      const userMessage: ChatMessage = {
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);

      try {
        // Criar mensagem do assistente vazia para streaming
        const assistantMessageId = Date.now();
        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: "",
          timestamp: new Date().toISOString(),
        };

        if (useStream) {
          // Modo streaming via SSE
          const abortController = new AbortController();
          currentStreamAbortControllerRef.current = abortController;

          const response = await fetch(`${apiUrl}/chat/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              message,
              user_id: userId,
              conversation_id: conversationId,
              context,
              stream: true,
              visualization: visualization || false,
              action_id: actionId,
            }),
            signal: abortController.signal,
          });

          if (!response.ok) {
            throw new Error(`Erro na API: ${response.statusText}`);
          }

          // Adicionar mensagem vazia para começar a stream
          setMessages((prev) => [...prev, assistantMessage]);

          // Ler stream SSE
          const reader = response.body?.getReader();
          const decoder = new TextDecoder("utf-8", { fatal: false });

          if (!reader) {
            throw new Error("Stream não disponível");
          }

          let buffer = "";
          let fullResponse = "";
          let parseErrorCount = 0;
          const MAX_PARSE_ERRORS = 5; // Limite de erros de parse antes de abortar (aumentado de 3 para 5)

          try {
            while (true) {
              const { done, value } = await reader.read();

              if (done) {
                // Processar buffer restante antes de sair
                if (buffer.trim()) {
                  const lines = buffer.split("\n\n");
                  for (const line of lines) {
                    if (line.startsWith("data: ")) {
                      try {
                        const data = JSON.parse(line.slice(6));
                        if (data.done) {
                          // Processar evento done final
                          if (data.conversation_id) {
                            setConversationId(data.conversation_id);
                          }
                          // Atualizar mensagem final se houver conteúdo
                          if (fullResponse) {
                            setMessages((prev) =>
                              prev.map((msg, idx) =>
                                idx === prev.length - 1 && msg.role === "assistant"
                                  ? { ...msg, content: fullResponse }
                                  : msg
                              )
                            );
                          }
                        }
                      } catch (e) {
                        // Ignorar erros de parse no último buffer
                        console.warn("Erro ao processar último buffer:", e);
                      }
                    }
                  }
                }
                // Garantir que loading seja desativado ao sair do loop
                isRequestInProgressRef.current = false;
                currentStreamAbortControllerRef.current = null;
                setIsLoading(false);
                break;
              }

              // Decodificar com tratamento de erros UTF-8
              try {
                buffer += decoder.decode(value, { stream: true });
              } catch (decodeError) {
                console.error("Erro ao decodificar chunk UTF-8:", decodeError);
                // Continuar mesmo com erro de decodificação
                continue;
              }

              const lines = buffer.split("\n\n");
              buffer = lines.pop() || "";

              for (const line of lines) {
                if (line.startsWith("data: ")) {
                  try {
                    const data = JSON.parse(line.slice(6));

                    if (data.error) {
                      throw new Error(data.error);
                    }

                    if (data.chunk) {
                      fullResponse += data.chunk;
                      // Atualizar mensagem do assistente incrementalmente
                      setMessages((prev) =>
                        prev.map((msg, idx) =>
                          idx === prev.length - 1 && msg.role === "assistant"
                            ? { ...msg, content: fullResponse }
                            : msg
                        )
                      );
                    }

                    // NOVO: Detectar reasoning (CoT) no stream
                    if (data.type === 'reasoning' && data.plan) {
                      setMessages((prev) =>
                        prev.map((msg, idx) =>
                          idx === prev.length - 1 && msg.role === "assistant"
                            ? { ...msg, reasoning: data.plan }
                            : msg
                        )
                      );
                      continue;
                    }

                    // NOVO: Detectar chart_data no stream
                    if (data.chart_data) {
                      console.log("[CHAT] Chart data recebido:", {
                        type: data.chart_data.type,
                        title: data.chart_data.title,
                        empty: data.chart_data.metadata?.empty,
                        metrics_found: data.chart_data.metadata?.metrics_found,
                        metrics_total: data.chart_data.metadata?.metrics_total,
                        done: data.done,
                      });

                      // Criar mensagem especial com chart_data
                      const chartMessage: ChatMessage = {
                        role: "assistant",
                        content: data.chart_data.title || "Gráfico gerado",
                        timestamp: new Date().toISOString(),
                        chartData: data.chart_data,
                      };

                      // Remover mensagem vazia do assistente se existir
                      setMessages((prev) => {
                        const filtered = prev.filter((msg) => msg.content !== "" || msg.role !== "assistant");
                        return [...filtered, chartMessage];
                      });

                      // Atualizar conversation ID se fornecido
                      if (data.conversation_id) {
                        setConversationId(data.conversation_id);
                      }

                      // IMPORTANTE: Desativar loading mesmo quando chart_data vem com done
                      isRequestInProgressRef.current = false;
                      currentStreamAbortControllerRef.current = null;
                      setIsLoading(false);

                      // Log de sucesso
                      if (data.chart_data.metadata?.empty) {
                        console.warn("[CHAT] Gráfico gerado mas está vazio:", data.chart_data.metadata);
                      } else {
                        console.log("[CHAT] Gráfico gerado com sucesso");
                      }

                      // Se também tem done: true, não processar evento done separadamente
                      if (data.done) {
                        return {
                          response: data.chart_data.title || "Gráfico gerado",
                          conversation_id: data.conversation_id,
                          chart_data: data.chart_data,
                          context_summary: data.context_summary || "",
                          sources: data.sources || [],
                        };
                      }

                      // Se não tem done, continuar processando stream
                      return {
                        response: data.chart_data.title || "Gráfico gerado",
                        conversation_id: data.conversation_id,
                        chart_data: data.chart_data,
                        context_summary: "",
                        sources: [],
                      };
                    }

                    if (data.done) {
                      // Atualizar conversation ID se fornecido
                      if (data.conversation_id) {
                        setConversationId(data.conversation_id);
                      }

                      // Atualizar mensagem final com conteúdo completo
                      if (fullResponse) {
                        setMessages((prev) =>
                          prev.map((msg, idx) =>
                            idx === prev.length - 1 && msg.role === "assistant"
                              ? { ...msg, content: fullResponse }
                              : msg
                          )
                        );
                      }

                      // Desativar loading imediatamente
                      isRequestInProgressRef.current = false;
                      currentStreamAbortControllerRef.current = null;
                      setIsLoading(false);

                      return {
                        response: fullResponse,
                        conversation_id: data.conversation_id,
                        context_summary: data.context_summary || "",
                        sources: data.sources || [],
                        fallback: data.fallback || false,
                        fallback_reason: data.fallback_reason,
                        fallback_message: data.fallback_message,
                      };
                    }

                    // Resetar contador de erros após parse bem-sucedido
                    parseErrorCount = 0;
                  } catch (parseError) {
                    parseErrorCount++;
                    console.error(`Erro ao processar chunk SSE (${parseErrorCount}/${MAX_PARSE_ERRORS}):`, parseError);

                    // Se exceder limite de erros, abortar stream
                    if (parseErrorCount >= MAX_PARSE_ERRORS) {
                      reader.cancel();
                      // Notificar usuário sobre interrupção do streaming
                      setError("Streaming interrompido. Mostrando resposta completa.");
                      throw new Error("Muitos erros ao processar stream. Conexão pode estar corrompida.");
                    }
                  }
                }
              }
            }
          } catch (streamError) {
            // Se for erro de abort, não fazer nada (stream foi cancelado intencionalmente)
            if (streamError instanceof Error && streamError.name === "AbortError") {
              console.log("Stream cancelado pelo usuário");
              throw streamError;
            }
            // Para outros erros, propagar
            throw streamError;
          } finally {
            // Garantir que isLoading seja false ao finalizar
            isRequestInProgressRef.current = false;
            currentStreamAbortControllerRef.current = null;
            setIsLoading(false);
          }
        } else {
          // Modo não-streaming (fallback)
          const response = await fetch(`${apiUrl}/chat/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              message,
              user_id: userId,
              conversation_id: conversationId,
              context,
              stream: false,
              visualization: visualization || false,
              action_id: actionId,
            }),
          });

          if (!response.ok) {
            throw new Error(`Erro na API: ${response.statusText}`);
          }

          const data: ChatResponse = await response.json();

          // Adicionar resposta do assistente
          assistantMessage.content = data.response;
          setMessages((prev) => [...prev, assistantMessage]);

          // Atualizar conversation ID se fornecido
          if (data.conversation_id) {
            setConversationId(data.conversation_id);
          }

          return data;
        }
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

