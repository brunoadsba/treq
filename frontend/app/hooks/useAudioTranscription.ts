"use client";

import { useState, useCallback } from "react";

interface UseAudioTranscriptionReturn {
  isTranscribing: boolean;
  transcript: string | null;
  error: string | null;
  transcribeAudio: (audioBlob: Blob, userId?: string, conversationId?: string) => Promise<string>;
}

export function useAudioTranscription(): UseAudioTranscriptionReturn {
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcript, setTranscript] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const transcribeAudio = useCallback(
    async (audioBlob: Blob, userId: string = "default-user", conversationId?: string): Promise<string> => {
      setIsTranscribing(true);
      setError(null);
      setTranscript(null);

      try {
        const formData = new FormData();
        formData.append("audio_file", audioBlob, "audio.webm");

        const params = new URLSearchParams();
        params.append("user_id", userId);
        if (conversationId) {
          params.append("conversation_id", conversationId);
        }
        params.append("language", "pt");

        const response = await fetch(`${apiUrl}/audio/transcribe?${params.toString()}`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: response.statusText }));
          throw new Error(errorData.detail || "Erro ao transcrever áudio");
        }

        const data = await response.json();
        setTranscript(data.text);
        return data.text;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Erro desconhecido";
        setError(errorMessage);
        throw err;
      } finally {
        setIsTranscribing(false);
      }
    },
    [apiUrl]
  );

  return {
    isTranscribing,
    transcript,
    error,
    transcribeAudio,
  };
}

