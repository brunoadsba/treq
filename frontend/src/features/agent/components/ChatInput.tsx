import { useEffect } from 'react';
import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import { useAudioTranscription } from "@/hooks/useAudioTranscription";
import { useToast } from "@/hooks/useToast";
import { ManusInput } from '@/components/ManusInput';

interface ChatInputProps {
    onSend: (message: string) => void;
    isLoading?: boolean;
    disabled?: boolean;
    placeholder?: string;
    onFocusChange?: (focused: boolean) => void;
}

export function ChatInput({ onSend, isLoading, disabled, placeholder = "Como posso ajudar?", onFocusChange }: ChatInputProps) {
    // Audio hooks
    const { isRecording, audioBlob, startRecording, stopRecording, clearRecording } = useAudioRecorder();
    const { isTranscribing, transcribeAudio } = useAudioTranscription();
    const { showToast } = useToast();

    // Handle transcription when audio is ready
    useEffect(() => {
        const handleTranscription = async () => {
            if (audioBlob) {
                try {
                    const text = await transcribeAudio(audioBlob);
                    if (text) {
                        onSend(text);
                        clearRecording();
                    }
                } catch (error) {
                    console.error("Transcription error:", error);
                    showToast("Erro ao transcrever áudio", "error");
                }
            }
        };
        handleTranscription();
    }, [audioBlob, transcribeAudio, clearRecording, showToast, onSend]);

    const handleManusSend = (message: string, file?: File) => {
        let messageToSend = message;

        if (file) {
            messageToSend = `[Arquivo Anexado: ${file.name}] ${message}`;
        }

        onSend(messageToSend);
    };

    return (
        <ManusInput
            onSend={handleManusSend}
            isLoading={isLoading || isTranscribing}
            disabled={disabled}
            placeholder={placeholder}
            isRecording={isRecording}
            onStartRecording={startRecording}
            onStopRecording={stopRecording}
            onFocusChange={onFocusChange}
        />
    );
}
