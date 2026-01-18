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
    const [showComment, setShowComment] = useState(false);
    const [comment, setComment] = useState("");

    const handleFeedback = async (type: "positive" | "negative") => {
        if (feedback === "positive" || isSubmitting) return;

        if (type === "negative" && !showComment) {
            setShowComment(true);
            return;
        }

        setIsSubmitting(true);

        try {
            if (onFeedback) {
                onFeedback(type, messageId);
            }

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";
            await fetch(`${apiUrl}/feedback`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message_id: messageId,
                    feedback_type: type,
                    comment: type === "negative" ? comment : undefined,
                    timestamp: new Date().toISOString(),
                }),
            });

            setFeedback(type);
            setShowComment(false);
        } catch (error) {
            console.debug("Feedback não enviado para backend:", error);
            setFeedback(type); // Mostrar sucesso local mesmo se backend falhar
        } finally {
            setIsSubmitting(false);
        }
    };

    if (feedback) {
        return (
            <div className={`flex items-center gap-2 text-xs animate-in fade-in duration-300 ${className}`}>
                {feedback === "positive" ? (
                    <span className="flex items-center gap-1.5 text-green-600 font-medium bg-green-50 px-2 py-1 rounded-md border border-green-100">
                        <ThumbsUp className="w-3.5 h-3.5" />
                        Obrigado! Isso nos ajuda a melhorar.
                    </span>
                ) : (
                    <span className="flex items-center gap-1.5 text-treq-gray-600 font-medium bg-treq-gray-100 px-2 py-1 rounded-md border border-treq-gray-200">
                        <ThumbsDown className="w-3.5 h-3.5" />
                        Feedback registrado. Analisaremos esta resposta.
                    </span>
                )}
            </div>
        );
    }

    return (
        <div className={`flex flex-col gap-2 ${className}`}>
            <div className="flex items-center gap-1">
                {!showComment && (
                    <span className="text-xs text-treq-gray-400 mr-1 hidden sm:inline">
                        Útil?
                    </span>
                )}

                <button
                    onClick={() => handleFeedback("positive")}
                    disabled={isSubmitting || showComment}
                    className={`p-1.5 rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-1
                       hover:scale-110 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed
                       min-w-[32px] min-h-[32px] flex items-center justify-center
                       ${feedback === "positive" ? "text-green-600 bg-green-50" : "text-treq-gray-400 hover:text-green-600 hover:bg-green-50"}`}
                    title="Gostei"
                >
                    <ThumbsUp className="w-4 h-4" />
                </button>

                <button
                    onClick={() => handleFeedback("negative")}
                    disabled={isSubmitting}
                    className={`p-1.5 rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1
                       hover:scale-110 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed
                       min-w-[32px] min-h-[32px] flex items-center justify-center
                       ${showComment ? "text-red-600 bg-red-50 ring-2 ring-red-500" : "text-treq-gray-400 hover:text-red-600 hover:bg-red-50"}`}
                    title="Não gostei"
                >
                    <ThumbsDown className="w-4 h-4" />
                </button>

                {showComment && (
                    <button
                        onClick={() => setShowComment(false)}
                        className="text-[10px] text-treq-gray-400 hover:text-treq-gray-600 ml-1 underline"
                    >
                        Cancelar
                    </button>
                )}
            </div>

            {showComment && (
                <div className="flex flex-col gap-2 animate-in slide-in-from-top-1 duration-200">
                    <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="O que estava errado? (Opcional)"
                        className="text-xs p-2 border border-treq-gray-200 rounded-md focus:ring-1 focus:ring-treq-yellow focus:border-treq-yellow outline-none resize-none h-16 w-full max-w-[240px]"
                        autoFocus
                    />
                    <button
                        onClick={() => handleFeedback("negative")}
                        disabled={isSubmitting}
                        className="bg-treq-black text-white text-[10px] py-1 px-3 rounded-md hover:bg-treq-gray-800 transition-colors self-start font-bold uppercase tracking-wider"
                    >
                        {isSubmitting ? "Enviando..." : "Enviar Melhoria"}
                    </button>
                </div>
            )}
        </div>
    );
}
