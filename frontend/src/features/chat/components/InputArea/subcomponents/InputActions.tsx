"use client";

import React from "react";
import { Camera, Paperclip } from "lucide-react";
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
    const [isOpen, setIsOpen] = React.useState(false);

    return (
        <div className="relative flex items-center">
            {/* Botão Único de Anexo (Grok Style) */}
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                disabled={disabled}
                className={`w-10 h-10 sm:w-11 sm:h-11 rounded-full flex items-center justify-center transition-all duration-200 hover:bg-treq-gray-100 focus:outline-none ${isOpen ? 'rotate-45' : ''}`}
                aria-label="Abrir menu de anexos"
            >
                <Paperclip className={`w-5 h-5 transition-colors ${isOpen ? 'text-treq-yellow' : 'text-treq-gray-400'}`} />
            </button>

            {/* Menu Suspenso de Ações */}
            {isOpen && (
                <>
                    <div
                        className="fixed inset-0 z-20"
                        onClick={() => setIsOpen(false)}
                    />
                    <div className="absolute bottom-14 left-0 z-30 w-48 bg-white border border-treq-gray-200 rounded-2xl shadow-xl p-2 animate-in fade-in slide-in-from-bottom-2 duration-200">
                        <button
                            type="button"
                            onClick={() => { onCameraClick(); setIsOpen(false); }}
                            className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-treq-gray-50 rounded-xl transition-colors text-treq-gray-700 font-medium text-sm"
                        >
                            <Camera className="w-5 h-5 text-treq-gray-400" />
                            Câmera
                        </button>
                        <button
                            type="button"
                            onClick={() => { onFileClick(); setIsOpen(false); }}
                            className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-treq-gray-50 rounded-xl transition-colors text-treq-gray-700 font-medium text-sm"
                        >
                            <Paperclip className="w-5 h-5 text-treq-gray-400" />
                            Arquivos
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}
