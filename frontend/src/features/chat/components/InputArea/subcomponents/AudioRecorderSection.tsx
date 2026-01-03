"use client";

import React from "react";
import { Mic } from "lucide-react";
import { useHighContrast } from "@/hooks/useHighContrast";

interface AudioRecorderSectionProps {
    audioBlob: Blob | null;
    isTranscribing: boolean;
    onClear: () => void;
    onSend: () => void;
    isProcessing: boolean;
}

export function AudioRecorderSection({
    audioBlob,
    isTranscribing,
    onClear,
    onSend,
    isProcessing,
}: AudioRecorderSectionProps) {
    const isHighContrast = useHighContrast();

    if (!audioBlob || isTranscribing) return null;

    return (
        <div
            className={`px-4 py-3 border-b flex items-center justify-between animate-fade-in ${isHighContrast
                    ? "bg-treq-yellow-dark border-treq-yellow"
                    : "bg-treq-info-light border-treq-info"
                }`}
        >
            <div className="flex items-center gap-2">
                <Mic
                    className={`w-4 h-4 ${isHighContrast ? "text-black" : "text-treq-info"}`}
                />
                <span
                    className={`text-sm font-medium ${isHighContrast ? "text-black" : "text-treq-info-dark"
                        }`}
                >
                    Áudio gravado e pronto para envio
                </span>
            </div>
            <div className="flex gap-2">
                <button
                    onClick={onClear}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 ${isHighContrast
                            ? "text-black hover:bg-treq-yellow-light"
                            : "text-treq-info-dark hover:bg-treq-info"
                        }`}
                    aria-label="Cancelar gravação de áudio"
                >
                    Cancelar
                </button>
                <button
                    onClick={onSend}
                    disabled={isProcessing}
                    className={`px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 ${isHighContrast
                            ? "bg-treq-yellow text-black hover:bg-treq-yellow-light"
                            : "bg-treq-info text-white hover:bg-treq-info-dark"
                        }`}
                    aria-label="Enviar áudio gravado"
                >
                    Enviar Áudio
                </button>
            </div>
        </div>
    );
}
