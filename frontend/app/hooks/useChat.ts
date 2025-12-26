"use client";

import { useState, useCallback } from "react";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
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
}

export function useChat(userId: string = "default-user") {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const sendMessage = useCallback(
    async (message: string, context?: Record<string, any>) => {
      if (!message.trim()) return;

      setIsLoading(true);
      setError(null);

      // Adicionar mensagem do usuário imediatamente
      const userMessage: ChatMessage = {
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);

      try {
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
          }),
        });

        if (!response.ok) {
          throw new Error(`Erro na API: ${response.statusText}`);
        }

        const data: ChatResponse = await response.json();

        // Adicionar resposta do assistente
        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: data.response,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, assistantMessage]);

        // Atualizar conversation ID se fornecido
        if (data.conversation_id) {
          setConversationId(data.conversation_id);
        }

        return data;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Erro desconhecido";
        setError(errorMessage);

        // Adicionar mensagem de erro
        const errorMessageObj: ChatMessage = {
          role: "assistant",
          content: `❌ Erro: ${errorMessage}`,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, errorMessageObj]);
        throw err; // Re-throw para permitir tratamento externo
      } finally {
        setIsLoading(false);
      }
    },
    [apiUrl, userId, conversationId]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    conversationId,
  };
}

