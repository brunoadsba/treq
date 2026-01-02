"use client";

import { useState } from "react";
import { ThumbsUp, ThumbsDown } from "lucide-react";

interface FeedbackButtonsProps {
    messageId?: string;
    onFeedback?: (type: "positive" | "negative", messageId?: string) => void;
    className?: string;
}

/**
 * Botões de feedback (Gostei / Não Gostei) para mensagens do assistente.
 * 
 * Conforme plano chat-inteligente.md:
 * "Implemente um botão de Feedback (Gostei / Não Gostei) em cada mensagem.
 * Isso será crucial para a Fase 4 (Otimização e Monitoramento)."
 */
export function FeedbackButtons({ messageId, onFeedback, className = "" }: FeedbackButtonsProps) {
    const [feedback, setFeedback] = useState<"positive" | "negative" | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleFeedback = async (type: "positive" | "negative") => {
        if (feedback || isSubmitting) return; // Já deu feedback ou está submetendo

        setIsSubmitting(true);

        try {
            // Chamar callback se fornecido
            if (onFeedback) {
                onFeedback(type, messageId);
            }

            // Enviar feedback para o backend (opcional - para analytics futuros)
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";
                await fetch(`${apiUrl}/feedback`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        message_id: messageId,
                        feedback_type: type,
                        timestamp: new Date().toISOString(),
                    }),
                });
            } catch (error) {
                // Silenciar erro - feedback é opcional
                console.debug("Feedback não enviado para backend:", error);
            }

            setFeedback(type);
        } finally {
            setIsSubmitting(false);
        }
    };

    // Se já deu feedback, mostrar confirmação
    if (feedback) {
        return (
            <div className={`flex items-center gap-2 text-xs ${className}`}>
                <span className="text-treq-gray-500">
                    {feedback === "positive" ? (
                        <span className="flex items-center gap-1 text-green-600">
                            <ThumbsUp className="w-3.5 h-3.5" />
                            Obrigado pelo feedback!
                        </span>
                    ) : (
                        <span className="flex items-center gap-1 text-treq-gray-500">
                            <ThumbsDown className="w-3.5 h-3.5" />
                            Feedback registrado
                        </span>
                    )}
                </span>
            </div>
        );
    }

    return (
        <div className={`flex items-center gap-1 ${className}`}>
            <span className="text-xs text-treq-gray-400 mr-1 hidden sm:inline">
                Esta resposta foi útil?
            </span>

            <button
                onClick={() => handleFeedback("positive")}
                disabled={isSubmitting}
                className="p-1.5 sm:p-2 rounded-lg text-treq-gray-400 hover:text-green-600 hover:bg-green-50 
                   transition-all focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-1
                   hover:scale-110 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed
                   min-w-[32px] min-h-[32px] sm:min-w-[36px] sm:min-h-[36px] flex items-center justify-center"
                title="Gostei"
                aria-label="Gostei desta resposta"
            >
                <ThumbsUp className="w-4 h-4" />
            </button>

            <button
                onClick={() => handleFeedback("negative")}
                disabled={isSubmitting}
                className="p-1.5 sm:p-2 rounded-lg text-treq-gray-400 hover:text-red-500 hover:bg-red-50 
                   transition-all focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1
                   hover:scale-110 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed
                   min-w-[32px] min-h-[32px] sm:min-w-[36px] sm:min-h-[36px] flex items-center justify-center"
                title="Não gostei"
                aria-label="Não gostei desta resposta"
            >
                <ThumbsDown className="w-4 h-4" />
            </button>
        </div>
    );
}
