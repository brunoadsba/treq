"use client";

import React, { useRef, useEffect, useState } from 'react';
import { Mic, Paperclip, ArrowUp, X, Loader2, Camera } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface ManusInputProps {
    onSend: (message: string, file?: File) => void;
    isLoading?: boolean;
    disabled?: boolean;
    placeholder?: string;
    isRecording?: boolean;
    onStartRecording?: () => void;
    onStopRecording?: () => void;
    onCameraClick?: () => void;

    // Controlled props (Optional)
    value?: string;
    onValueChange?: (value: string) => void;
    file?: File | null;
    onFileChange?: (file: File | null) => void;
}

export function ManusInput({
    onSend,
    isLoading,
    disabled,
    placeholder = "Como posso ajudar?",
    isRecording = false,
    onStartRecording,
    onStopRecording,
    onCameraClick,
    value: controlledValue,
    onValueChange,
    file: controlledFile,
    onFileChange
}: ManusInputProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Internal state for uncontrolled mode
    const [internalValue, setInternalValue] = useState("");
    const [internalFile, setInternalFile] = useState<File | null>(null);

    const isControlledValue = controlledValue !== undefined;
    const isControlledFile = controlledFile !== undefined;

    const value = isControlledValue ? controlledValue : internalValue;
    const file = isControlledFile ? controlledFile : internalFile;

    const [isFocused, setIsFocused] = useState(false);

    // Auto-resize
    const adjustHeight = () => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            const newHeight = Math.min(textarea.scrollHeight, 160);
            textarea.style.height = `${newHeight}px`;
        }
    };

    useEffect(() => {
        adjustHeight();
    }, [value]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleSend = () => {
        if ((!value.trim() && !file) || isLoading || disabled) return;

        onSend(value, file || undefined);

        if (!isControlledValue) setInternalValue("");
        else onValueChange?.("");

        if (!isControlledFile) setInternalFile(null);
        else onFileChange?.(null);

        if (textareaRef.current) textareaRef.current.style.height = 'auto';
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            if (!isControlledFile) setInternalFile(selectedFile);
            else onFileChange?.(selectedFile);
        }
        // Reset input value to allow selecting the same file again if needed
        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    const handleRemoveFile = () => {
        if (!isControlledFile) setInternalFile(null);
        else onFileChange?.(null);
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const newValue = e.target.value;
        if (!isControlledValue) setInternalValue(newValue);
        else onValueChange?.(newValue);
    };

    return (
        <div className="w-full max-w-4xl mx-auto px-4 pb-4">
            {/* File Preview (Floating above) */}
            {file && (
                <div className="mb-2 mx-auto max-w-[95%] p-2 bg-gray-50 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-100 dark:border-gray-700 rounded-lg flex items-center justify-between animate-in fade-in slide-in-from-bottom-2 shadow-sm">
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                        <Paperclip className="w-4 h-4 text-treq-yellow" />
                        <span className="truncate max-w-[200px] font-medium">{file.name}</span>
                    </div>
                    <button
                        onClick={handleRemoveFile}
                        className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            )}

            {/* Input Capsule */}
            <div
                className={cn(
                    "relative flex items-end gap-2 p-2 transition-all duration-300 ease-out",
                    "bg-white dark:bg-treq-gray-900/50",
                    "border border-gray-200 dark:border-gray-800",
                    "shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.2)]",
                    "rounded-[32px]",
                    isFocused && "ring-2 ring-treq-yellow/20 border-treq-yellow/50 shadow-[0_8px_40px_rgb(0,0,0,0.08)]"
                )}
            >
                {/* Left Actions */}
                <div className="pb-1 pl-1 flex gap-1">
                    {/* Camera Button */}
                    {onCameraClick && (
                        <button
                            onClick={onCameraClick}
                            disabled={isLoading || disabled}
                            className="p-2.5 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-full transition-all active:scale-95"
                            title="Abrir câmera"
                        >
                            <Camera size={20} strokeWidth={1.5} />
                        </button>
                    )}

                    {/* Attach Button */}
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isLoading || disabled}
                        className="p-2.5 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-full transition-all active:scale-95"
                        title="Anexar arquivo"
                    >
                        <Paperclip size={20} strokeWidth={1.5} />
                    </button>
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        onChange={handleFileSelect}
                    />
                </div>

                {/* Text Area */}
                <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={handleChange}
                    onKeyDown={handleKeyDown}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    placeholder={isRecording ? "Ouvindo..." : placeholder}
                    disabled={disabled || isLoading}
                    rows={1}
                    className="flex-1 max-h-[160px] min-h-[44px] w-full resize-none bg-transparent border-0 focus:ring-0 text-[16px] leading-relaxed py-3 px-2 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 disabled:opacity-50 font-normal"
                    style={{ overflowY: value.length > 100 ? 'auto' : 'hidden' }}
                />

                {/* Right Actions: Mic & Send */}
                <div className="pb-1 pr-1 flex gap-1">
                    {/* Mic Button (Show when empty) */}
                    {!value.trim() && !file && !isRecording && (
                        <button
                            onClick={onStartRecording}
                            disabled={isLoading}
                            className="p-2.5 text-gray-400 hover:text-treq-yellow dark:text-gray-500 dark:hover:text-treq-yellow hover:bg-gray-50 dark:hover:bg-gray-800 rounded-full transition-all active:scale-95"
                            title="Gravar áudio"
                        >
                            <Mic size={22} strokeWidth={1.5} />
                        </button>
                    )}

                    {/* Send Button (Always present, changes style) */}
                    {(value.trim() || file || isRecording) && (
                        <button
                            onClick={isRecording ? onStopRecording : handleSend}
                            disabled={(!value.trim() && !file && !isRecording) || isLoading}
                            className={cn(
                                "w-10 h-10 flex items-center justify-center rounded-full transition-all duration-300 shadow-sm",
                                (value.trim() || file)
                                    ? "bg-black dark:bg-white text-white dark:text-black hover:scale-105 active:scale-95"
                                    : "bg-treq-gray-100 text-treq-gray-400",
                                isRecording && "bg-red-500 hover:bg-red-600 animate-pulse text-white"
                            )}
                        >
                            {isLoading ? (
                                <Loader2 size={18} className="animate-spin" />
                            ) : isRecording ? (
                                <div className="w-3 h-3 bg-white rounded-sm" />
                            ) : (
                                <ArrowUp size={20} strokeWidth={2.5} />
                            )}
                        </button>
                    )}
                </div>
            </div>

            {/* Disclaimer */}
            <div className="text-center mt-3 animate-in fade-in duration-700 delay-150">
                <p className="text-[10px] sm:text-xs text-gray-400 dark:text-gray-600 font-medium tracking-wide opacity-80">
                    Treq pode cometer erros. Verifique informações críticas.
                </p>
            </div>
        </div>
    );
}
