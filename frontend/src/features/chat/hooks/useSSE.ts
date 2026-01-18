import { useRef, useCallback } from "react";
import { ChatMessage, ChatResponse, ReasoningPlan, ChartData } from "../types";

interface SSEOptions {
    apiUrl: string;
    userId: string;
    conversationId: string | null;
    onChunk: (chunk: string) => void;
    onReasoning: (plan: ReasoningPlan, runId: string) => void;
    onChart: (chartData: ChartData, conversationId?: string) => void;
    onDone: (data: ChatResponse) => void;
    onError: (error: string) => void;
}

export function useSSE() {
    const currentStreamAbortControllerRef = useRef<AbortController | null>(null);

    const stopStream = useCallback(() => {
        if (currentStreamAbortControllerRef.current) {
            currentStreamAbortControllerRef.current.abort();
            currentStreamAbortControllerRef.current = null;
        }
    }, []);

    const startStream = useCallback(async (
        message: string,
        options: SSEOptions,
        params: { visualization?: boolean; actionId?: string; imageUrl?: string; context?: Record<string, unknown> }
    ) => {
        stopStream();
        const abortController = new AbortController();
        currentStreamAbortControllerRef.current = abortController;

        try {
            const response = await fetch(`${options.apiUrl}/chat/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${typeof window !== "undefined" ? localStorage.getItem("treq_token") || "" : ""}`,
                },
                body: JSON.stringify({
                    message,
                    user_id: options.userId,
                    conversation_id: options.conversationId,
                    context: params.context,
                    stream: true,
                    visualization: params.visualization || false,
                    action_id: params.actionId,
                    image_url: params.imageUrl,
                }),
                signal: abortController.signal,
            });

            if (!response.ok) {
                if (response.status === 401) {
                    localStorage.removeItem("treq_token");
                    window.location.href = "/login";
                    throw new Error("Sessão expirada. Redirecionando...");
                }
                throw new Error(`Erro na API: ${response.statusText}`);
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder("utf-8");
            if (!reader) throw new Error("Stream não disponível");

            let buffer = "";
            let fullResponse = "";
            let parseErrorCount = 0;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n\n");
                buffer = lines.pop() || "";

                for (const line of lines) {
                    if (!line.startsWith("data: ")) continue;

                    try {
                        const data = JSON.parse(line.slice(6));
                        if (data.error) throw new Error(data.error);

                        if (data.chunk) {
                            fullResponse += data.chunk;
                            options.onChunk(fullResponse);
                        }

                        if (data.type === 'reasoning' && data.plan) {
                            options.onReasoning(data.plan, data.run_id);
                        }

                        if (data.chart_data) {
                            options.onChart(data.chart_data, data.conversation_id);
                            if (data.done) {
                                options.onDone({
                                    response: data.chart_data.title || "Gráfico gerado",
                                    conversation_id: data.conversation_id,
                                    chart_data: data.chart_data,
                                    context_summary: data.context_summary || "",
                                    sources: data.sources || [],
                                    run_id: data.run_id
                                });
                                return;
                            }
                        }

                        if (data.done) {
                            options.onDone({
                                response: fullResponse,
                                conversation_id: data.conversation_id,
                                context_summary: data.context_summary || "",
                                sources: data.sources || [],
                                fallback: data.fallback || false,
                                fallback_reason: data.fallback_reason,
                                fallback_message: data.fallback_message,
                                run_id: data.run_id
                            });
                            return;
                        }
                        parseErrorCount = 0;
                    } catch (e) {
                        parseErrorCount++;
                        if (parseErrorCount >= 5) throw new Error("Muitos erros de processamento no stream.");
                    }
                }
            }
        } catch (err) {
            if (err instanceof Error && err.name === "AbortError") return;
            options.onError(err instanceof Error ? err.message : "Erro no stream");
            throw err;
        } finally {
            currentStreamAbortControllerRef.current = null;
        }
    }, [stopStream]);

    return { startStream, stopStream };
}
