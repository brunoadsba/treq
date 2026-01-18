import { useState, useCallback, useRef, useEffect } from "react";
import { useChatContext } from "@/context/ChatContext";
import {
  ChatMessage,
  ChatResponse,
  SavedConversation,
  ReasoningPlan,
  ChartData
} from "@/features/chat/types";
import { useSSE } from "@/features/chat/hooks/useSSE";
import { useConversationManagement } from "@/features/chat/hooks/useConversationManagement";

export function useChat(userId: string = "default-user") {
  const {
    chatState,
    setChatState,
    clearChatSession
  } = useChatContext();

  const { messages, conversationId, isLoading, error } = chatState;
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const isRequestInProgressRef = useRef(false);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

  const { startStream, stopStream } = useSSE();
  const {
    getSavedConversations,
    saveConversation,
    deleteConversationFromStorage
  } = useConversationManagement(userId);

  // Helper setters
  const setMessages = useCallback((updater: ChatMessage[] | ((prev: ChatMessage[]) => ChatMessage[])) => {
    setChatState(prev => ({
      ...prev,
      messages: typeof updater === 'function' ? updater(prev.messages) : updater
    }));
  }, [setChatState]);

  const setConversationId = useCallback((id: string | null) => {
    setChatState(prev => ({ ...prev, conversationId: id }));
  }, [setChatState]);

  const setIsLoading = useCallback((loading: boolean) => {
    setChatState(prev => ({ ...prev, isLoading: loading }));
  }, [setChatState]);

  const setError = useCallback((err: string | null) => {
    setChatState(prev => ({ ...prev, error: err }));
  }, [setChatState]);

  // Persistência automática
  useEffect(() => {
    if (typeof window === "undefined" || messages.length === 0) return;
    const timeoutId = setTimeout(() => {
      const id = saveConversation(messages, conversationId, currentConversationId);
      if (id && !currentConversationId) setCurrentConversationId(id);
    }, 2000);
    return () => clearTimeout(timeoutId);
  }, [messages, conversationId, currentConversationId, saveConversation]);

  const sendMessage = useCallback(
    async (
      message: string,
      context?: Record<string, any>,
      useStream: boolean = true,
      visualization?: boolean,
      actionId?: string,
      imageUrl?: string
    ) => {
      if (!message.trim() || isRequestInProgressRef.current) return;

      isRequestInProgressRef.current = true;
      setIsLoading(true);
      setError(null);

      const userMessage: ChatMessage = {
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
        imageUrl
      };

      setMessages((prev: ChatMessage[]) => [...prev, userMessage]);

      try {
        const startTime = Date.now();
        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: "",
          isThinking: true,
          timestamp: new Date().toISOString(),
        };

        if (useStream) {
          setMessages((prev: ChatMessage[]) => [...prev, assistantMessage]);

          await startStream(message, {
            apiUrl,
            userId,
            conversationId,
            onChunk: (content: string) => {
              setMessages((prev: ChatMessage[]) => prev.map((msg, idx) =>
                idx === prev.length - 1 && msg.role === "assistant"
                  ? { ...msg, content, isThinking: false, thinkingDuration: msg.thinkingDuration || Math.round((Date.now() - startTime) / 1000) }
                  : msg
              ));
            },
            onReasoning: (reasoning: ReasoningPlan, runId: string) => {
              setMessages((prev: ChatMessage[]) => prev.map((msg, idx) =>
                idx === prev.length - 1 && msg.role === "assistant" ? { ...msg, reasoning, runId } : msg
              ));
            },
            onChart: (chartData: ChartData, convId?: string) => {
              const chartMsg: ChatMessage = {
                role: "assistant",
                content: chartData.title || "Gráfico gerado",
                timestamp: new Date().toISOString(),
                chartData,
              };
              setMessages((prev: ChatMessage[]) => {
                const filtered = prev.filter(m => m.content !== "" || m.role !== "assistant");
                return [...filtered, chartMsg];
              });
              if (convId) setConversationId(convId);
            },
            onDone: (data: ChatResponse) => {
              if (data.conversation_id) setConversationId(data.conversation_id);
              isRequestInProgressRef.current = false;
              setIsLoading(false);
            },
            onError: (err: string) => setError(err)
          }, { visualization, actionId, imageUrl, context });
        } else {
          // Fallback síncrono (simples)
          const response = await fetch(`${apiUrl}/chat/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${typeof window !== "undefined" ? localStorage.getItem("treq_token") || "" : ""}`,
            },
            body: JSON.stringify({ message, user_id: userId, conversation_id: conversationId, context, stream: false, visualization: visualization || false, action_id: actionId }),
          });
          if (!response.ok) throw new Error("Erro na API");
          const data: ChatResponse = await response.json();
          if (data.conversation_id) setConversationId(data.conversation_id);
          setMessages((prev: ChatMessage[]) => [...prev, { role: "assistant", content: data.response, runId: data.run_id, timestamp: new Date().toISOString() }]);
        }
      } catch (err) {
        if (!(err instanceof Error && err.name === "AbortError")) {
          setError(err instanceof Error ? err.message : "Erro desconhecido");
          setMessages((prev: ChatMessage[]) => prev.filter(m => m.content !== "" || m.role !== "assistant"));
          setMessages((prev: ChatMessage[]) => [...prev, { role: "assistant", content: `❌ Erro: ${err instanceof Error ? err.message : "Erro"}`, timestamp: new Date().toISOString() }]);
        }
      } finally {
        isRequestInProgressRef.current = false;
        setIsLoading(false);
      }
    },
    [apiUrl, userId, conversationId, setMessages, setConversationId, setIsLoading, setError, startStream]
  );

  const startNewConversation = useCallback(() => {
    if (messages.length > 0) saveConversation(messages, conversationId, currentConversationId);
    setMessages([]);
    setConversationId(null);
    setError(null);
    setCurrentConversationId(null);
  }, [messages, conversationId, currentConversationId, saveConversation, setMessages, setConversationId, setError]);

  const loadConversation = useCallback((id: string) => {
    const conversations = getSavedConversations();
    const conv = conversations.find(c => c.id === id);
    if (conv) {
      setMessages(conv.messages);
      setConversationId(conv.conversationId);
      setCurrentConversationId(conv.id);
      setError(null);
    }
  }, [getSavedConversations, setMessages, setConversationId, setError]);

  const deleteConversation = useCallback((id: string) => {
    deleteConversationFromStorage(id);
    if (currentConversationId === id) {
      setMessages([]);
      setConversationId(null);
      setCurrentConversationId(null);
    }
  }, [currentConversationId, deleteConversationFromStorage, setMessages, setConversationId]);

  const exportConversation = useCallback(() => {
    const data = { messages, conversationId, exportedAt: new Date().toISOString() };
    return JSON.stringify(data, null, 2);
  }, [messages, conversationId]);

  return {
    messages, isLoading, error, sendMessage, conversationId, currentConversationId,
    startNewConversation, loadConversation, deleteConversation, getSavedConversations, exportConversation
  };
}
