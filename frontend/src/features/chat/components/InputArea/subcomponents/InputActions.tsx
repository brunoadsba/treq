"use client";

import React from "react";
import { Camera, Paperclip, Mic } from "lucide-react";
import { useHighContrast } from "@/hooks/useHighContrast";

interface InputActionsProps {
    onCameraClick: () => void;
    onFileClick: () => void;
    onMicClick: () => void;
    isRecording: boolean;
    disabled: boolean;
    hasFile: boolean;
}

export function InputActions({
    onCameraClick,
    onFileClick,
    onMicClick,
    isRecording,
    disabled,
    hasFile,
}: InputActionsProps) {
    const isHighContrast = useHighContrast();

    return (
        <div className="flex items-center gap-1.5 sm:gap-2 md:gap-3">
            {/* Botão de Câmera */}
            <button
                type="button"
                onClick={onCameraClick}
                disabled={disabled}
                className={`min-w-[44px] min-h-[44px] sm:min-w-[52px] sm:min-h-[52px] px-2 sm:px-3 rounded-xl font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 hover:scale-110 active:scale-90 shadow-sm hover:shadow-md ${isHighContrast
                    ? "bg-treq-yellow text-black hover:bg-treq-yellow-light"
                    : "bg-white border border-treq-gray-200 text-treq-gray-600 hover:text-treq-yellow hover:border-treq-yellow"
                    }`}
                title="Usar câmera"
                aria-label="Abrir câmera"
            >
                <Camera className="w-5 h-5 sm:w-5.5 sm:h-5.5 transition-transform" />
            </button>

            {/* Botão de anexar documento */}
            <button
                type="button"
                onClick={onFileClick}
                disabled={disabled}
                className={`min-w-[44px] min-h-[44px] sm:min-w-[52px] sm:min-h-[52px] px-2 sm:px-3 rounded-xl font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 hover:scale-110 active:scale-90 shadow-sm hover:shadow-md ${hasFile
                    ? isHighContrast
                        ? "bg-treq-yellow text-black hover:bg-treq-yellow-light"
                        : "bg-treq-info text-white hover:bg-treq-info-dark"
                    : isHighContrast
                        ? "bg-treq-yellow text-black hover:bg-treq-yellow-light"
                        : "bg-white border border-treq-gray-200 text-treq-gray-600 hover:text-treq-info hover:border-treq-info"
                    }`}
                title={hasFile ? "Arquivo anexado - Clique para trocar" : "Anexar documento"}
                aria-label={hasFile ? "Arquivo anexado" : "Anexar documento"}
            >
                <Paperclip
                    className={`w-5 h-5 sm:w-5.5 sm:h-5.5 transition-transform ${hasFile ? "rotate-45" : ""
                        }`}
                />
            </button>

            {/* Botão de gravação */}
            <button
                type="button"
                onClick={onMicClick}
                disabled={disabled}
                className={`relative min-w-[44px] min-h-[44px] sm:min-w-[52px] sm:min-h-[52px] px-2 sm:px-3 rounded-xl font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 active:scale-90 shadow-sm hover:shadow-md ${isRecording
                    ? "bg-treq-error text-white hover:bg-treq-error-dark shadow-lg shadow-treq-error/50"
                    : isHighContrast
                        ? "bg-treq-yellow text-black hover:bg-treq-yellow-light hover:scale-110"
                        : "bg-white border border-treq-gray-200 text-treq-gray-600 hover:text-treq-error hover:border-treq-error hover:scale-110"
                    }`}
                title={isRecording ? "Parar gravação" : "Gravar áudio"}
                aria-label={isRecording ? "Parar gravação" : "Iniciar gravação de áudio"}
                aria-pressed={isRecording}
            >
                {isRecording ? (
                    <div className="flex items-center gap-0.75 h-5">
                        <div className="w-1 h-3 bg-white rounded-full animate-soundwave" style={{ animationDelay: '0s' }}></div>
                        <div className="w-1 h-5 bg-white rounded-full animate-soundwave" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-1 h-4 bg-white rounded-full animate-soundwave" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                ) : (
                    <Mic
                        className={`w-5 h-5 sm:w-5.5 sm:h-5.5 transition-transform`}
                    />
                )}
            </button>
        </div>
    );
}
