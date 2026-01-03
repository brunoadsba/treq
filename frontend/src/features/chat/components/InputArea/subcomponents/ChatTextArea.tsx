"use client";

import React, { useRef, useEffect } from "react";
import { useHighContrast } from "@/hooks/useHighContrast";

interface ChatTextAreaProps {
    value: string;
    onChange: (value: string) => void;
    onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
    placeholder: string;
    disabled: boolean;
    isTranscribing: boolean;
}

export function ChatTextArea({
    value,
    onChange,
    onKeyDown,
    placeholder,
    disabled,
    isTranscribing,
}: ChatTextAreaProps) {
    const isHighContrast = useHighContrast();
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Auto-resize logic
    useEffect(() => {
        const el = textareaRef.current;
        if (el) {
            el.style.height = "0px";
            const scrollHeight = el.scrollHeight;
            el.style.height = scrollHeight + "px";
        }
    }, [value]);

    return (
        <div className="flex-1 relative">
            <textarea
                ref={textareaRef}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder={placeholder}
                rows={1}
                disabled={disabled}
                className={`w-full min-h-[44px] sm:min-h-[52px] max-h-[150px] sm:max-h-[200px] px-2 py-3 rounded-xl text-sm sm:text-base focus:outline-none disabled:opacity-50 transition-all resize-none overflow-y-auto scrollbar-hide bg-transparent ${isHighContrast
                    ? "text-white placeholder:text-treq-gray-400"
                    : "text-treq-gray-900 placeholder:text-treq-gray-400"
                    }`}
                style={{
                    fontSize: isHighContrast ? "1.125rem" : undefined,
                    height: "auto",
                }}
                aria-label="Campo de entrada de mensagem"
                aria-describedby={isTranscribing ? "transcribing-status" : undefined}
            />
            {isTranscribing && (
                <span id="transcribing-status" className="sr-only">
                    Transcrevendo áudio, aguarde...
                </span>
            )}
        </div>
    );
}
