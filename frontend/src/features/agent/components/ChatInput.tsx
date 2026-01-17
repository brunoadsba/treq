import { useRef, useEffect, useState, useCallback } from 'react';
import { Send, Loader2, Mic, Paperclip, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import { useAudioTranscription } from "@/hooks/useAudioTranscription";
import { useToast } from "@/hooks/useToast";

interface ChatInputProps {
    onSend: (message: string) => void;
    isLoading?: boolean;
    disabled?: boolean;
    placeholder?: string;
}

export function ChatInput({ onSend, isLoading, disabled, placeholder = "Digite sua mensagem..." }: ChatInputProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [value, setValue] = useState("");
    const [attachedFile, setAttachedFile] = useState<File | null>(null);

    // Audio hooks
    const { isRecording, audioBlob, startRecording, stopRecording, clearRecording } = useAudioRecorder();
    const { isTranscribing, transcribeAudio } = useAudioTranscription();
    const { showToast } = useToast();

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

    // Handle transcription when audio is ready
    useEffect(() => {
        const handleTranscription = async () => {
            if (audioBlob) {
                try {
                    const text = await transcribeAudio(audioBlob);
                    if (text) {
                        setValue(prev => (prev ? `${prev} ${text}` : text));
                        clearRecording();
                    }
                } catch (error) {
                    console.error("Transcription error:", error);
                    showToast("Erro ao transcrever áudio", "error");
                }
            }
        };
        handleTranscription();
    }, [audioBlob, transcribeAudio, clearRecording, showToast]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleSend = () => {
        if ((!value.trim() && !attachedFile) || isLoading || disabled || isTranscribing) return;

        let messageToSend = value;
        if (attachedFile) {
            messageToSend = `[Arquivo Anexado: ${attachedFile.name}] ${value}`;
            // Simulação de upload para o agente (o backend processaria isso na vida real)
        }

        onSend(messageToSend);
        setValue("");
        setAttachedFile(null);
        if (textareaRef.current) textareaRef.current.style.height = 'auto';
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setAttachedFile(e.target.files[0]);
        }
    };

    const isProcessing = isLoading || isTranscribing;

    return (
        <div className="relative w-full max-w-5xl mx-auto p-3 sm:p-4">
            {/* File Preview */}
            {attachedFile && (
                <div className="mb-2 mx-2 p-2 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-between animate-in fade-in slide-in-from-bottom-1">
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                        <Paperclip className="w-4 h-4" />
                        <span className="truncate max-w-[200px]">{attachedFile.name}</span>
                    </div>
                    <button
                        onClick={() => setAttachedFile(null)}
                        className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            )}

            {/* Audio Recording State */}
            {isRecording && (
                <div className="mb-2 mx-2 p-2 bg-red-50 dark:bg-red-900/20 text-red-600 rounded-lg flex items-center justify-between animate-pulse">
                    <span className="text-sm font-medium flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-red-600 animate-pulse" />
                        Gravando áudio...
                    </span>
                    <button
                        onClick={stopRecording}
                        className="text-xs bg-white dark:bg-black border border-red-200 px-2 py-1 rounded-md shadow-sm"
                    >
                        Parar
                    </button>
                </div>
            )}

            <div className="relative flex items-end gap-2 bg-white dark:bg-treq-gray-900 border border-gray-200 dark:border-gray-800 rounded-[28px] shadow-sm p-2 transition-all focus-within:ring-2 focus-within:ring-blue-100 dark:focus-within:ring-blue-900">

                {/* Actions (Left) */}
                <div className="flex items-center mb-1 pl-1 gap-1">
                    <Button
                        variant="ghost"
                        size="sm"
                        className="w-10 h-10 sm:w-11 sm:h-11 rounded-full p-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isProcessing || isRecording}
                    >
                        <Paperclip className="w-5 h-5" />
                    </Button>
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        onChange={handleFileSelect}
                    />
                </div>

                <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={isRecording ? "Ouvindo..." : placeholder}
                    disabled={disabled || isLoading || isTranscribing}
                    rows={1}
                    className="flex-1 max-h-[160px] min-h-[44px] sm:min-h-[52px] w-full resize-none bg-transparent border-0 focus:ring-0 text-sm sm:text-base py-3 px-2 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 disabled:opacity-50"
                    style={{ overflowY: value.length > 100 ? 'auto' : 'hidden' }}
                />

                <div className="mb-1 right-1 flex gap-2">
                    {/* Mic Button if empty input */}
                    {!value.trim() && !attachedFile && !isRecording ? (
                        <Button
                            onClick={startRecording}
                            disabled={isProcessing}
                            className="w-10 h-10 sm:w-11 sm:h-11 rounded-full flex items-center justify-center transition-all bg-treq-gray-100 text-treq-gray-600 hover:text-treq-yellow dark:bg-gray-800 dark:text-gray-400"
                        >
                            <Mic className="w-5 h-5" />
                        </Button>
                    ) : (
                        <Button
                            onClick={handleSend}
                            disabled={(!value.trim() && !attachedFile) || isProcessing}
                            className={`w-10 h-10 sm:w-11 sm:h-11 rounded-full flex items-center justify-center transition-all shadow-md active:scale-95 ${value.trim() || attachedFile
                                ? 'bg-treq-yellow hover:bg-treq-yellow-light text-treq-gray-900'
                                : 'bg-treq-gray-100 text-treq-gray-400 hover:bg-treq-gray-200 dark:bg-gray-800 dark:text-gray-500'
                                }`}
                        >
                            {isProcessing ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Send className="w-4 h-4 ml-0.5" />
                            )}
                        </Button>
                    )}
                </div>
            </div>

            {/* Disclaimer */}
            <div className="text-center mt-2">
                <p className="text-[10px] sm:text-xs text-gray-400 dark:text-gray-500">
                    Treq pode cometer erros. Verifique informações críticas.
                </p>
            </div>
        </div>
    );
}
