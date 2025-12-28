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
    async (message: string, context?: Record<string, any>, useStream: boolean = true) => {
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
        // Criar mensagem do assistente vazia para streaming
        const assistantMessageId = Date.now();
        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: "",
          timestamp: new Date().toISOString(),
        };

        if (useStream) {
          // Modo streaming via SSE
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
            }),
          });

          if (!response.ok) {
            throw new Error(`Erro na API: ${response.statusText}`);
          }

          // Adicionar mensagem vazia para começar a stream
          setMessages((prev) => [...prev, assistantMessage]);

          // Ler stream SSE
          const reader = response.body?.getReader();
          const decoder = new TextDecoder();

          if (!reader) {
            throw new Error("Stream não disponível");
          }

          let buffer = "";
          let fullResponse = "";

          while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });
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

                  if (data.done) {
                    // Atualizar conversation ID se fornecido
                    if (data.conversation_id) {
                      setConversationId(data.conversation_id);
                    }
                    setIsLoading(false);
                    return {
                      response: fullResponse,
                      conversation_id: data.conversation_id,
                      context_summary: data.context_summary || "",
                      sources: data.sources || [],
                    };
                  }
                } catch (e) {
                  console.error("Erro ao processar chunk SSE:", e);
                }
              }
            }
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

