"use client";

import React, { useState, useRef, useCallback, useEffect } from "react";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import { useAudioTranscription } from "@/hooks/useAudioTranscription";
import { useDocumentUpload } from "@/hooks/useDocumentUpload";
import { useHighContrast } from "@/hooks/useHighContrast";
import { CameraCapture } from "@/features/vision/components/CameraCapture";
import { base64ToFile, fileToBase64 } from "@/features/chat/utils/file-utils";
import { ManusInput } from "@/components/ManusInput";

interface InputAreaProps {
  onSend: (message: string, actionId?: string, imageUrl?: string) => void;
  isLoading: boolean;
  onDocumentUploaded?: (filename: string, chunks: number) => void;
  onDocumentUploadError?: (error: string) => void;
  onFocusChange?: (focused: boolean) => void;
}

export function InputArea({
  onSend,
  isLoading,
  onDocumentUploaded,
  onDocumentUploadError,
  onFocusChange,
}: InputAreaProps) {
  const [message, setMessage] = useState("");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);

  // Ref para rastrear URLs de Blob e evitar memory leaks
  const activeBlobUrls = useRef<Set<string>>(new Set());

  const { isRecording, audioBlob, startRecording, stopRecording, clearRecording } = useAudioRecorder();
  const { isTranscribing, transcribeAudio } = useAudioTranscription();
  const { isUploading, uploadDocument } = useDocumentUpload();
  const isHighContrast = useHighContrast();

  // Função para criar e registrar Blob URL
  const createSecureBlobUrl = useCallback((file: File) => {
    const url = URL.createObjectURL(file);
    activeBlobUrls.current.add(url);
    return url;
  }, []);

  // Cleanup de Blob URLs ao desmontar
  useEffect(() => {
    return () => {
      activeBlobUrls.current.forEach(url => URL.revokeObjectURL(url));
      activeBlobUrls.current.clear();
    };
  }, []);

  const handleTranscribe = useCallback(async () => {
    if (audioBlob) {
      try {
        const text = await transcribeAudio(audioBlob);
        if (text && text.trim()) {
          onSend(text);
          clearRecording();
        }
      } catch (error) {
        console.error("Erro na transcrição:", error);
      }
    }
  }, [audioBlob, transcribeAudio, clearRecording, onSend]);

  const handleSubmit = async (msgInput: string, fileInput?: File) => {
    const currentMessage = msgInput.trim();
    const currentFile = fileInput || null;

    const isProcessing = isLoading || isTranscribing || isUploading;

    if (isProcessing) return;

    try {
      let imageUrl: string | undefined = undefined;

      // 1. Prioridade: Upload de Documento/Imagem
      if (currentFile) {
        // Criar URL para visualização local imediata (UX)
        const localPreviewUrl = currentFile.type.startsWith('image/')
          ? createSecureBlobUrl(currentFile)
          : undefined;

        // Se for imagem, converter para base64 para o backend realmente "ver" o conteúdo
        if (currentFile.type.startsWith('image/')) {
          imageUrl = await fileToBase64(currentFile);
        }

        // Upload oficial para o RAG (Base de conhecimento)
        const result = await uploadDocument(currentFile, undefined, currentMessage || undefined);

        if (onDocumentUploaded) {
          onDocumentUploaded(currentFile.name, result.chunksIndexed);
        }

        const chatText = currentMessage || `[Arquivo: ${currentFile.name}]`;
        // Passamos o localPreviewUrl para a bolha do chat (eficiência) e o base64 real para o Hook/Backend
        onSend(chatText, undefined, imageUrl || localPreviewUrl);

        // O ManusInput limpará o estado via controlled props (quando passarmos "" e null nos useEffects ou render)
        // Mas como chamamos onSend do pai (ManusInput), ele limpa o estado interno dele.
        // Precisamos limpar o nosso estado controlado.
        return;
      }

      // 2. Transcrição pendente de áudio (se o usuário clicar em enviar com áudio gravado mas não transcrito)
      if (audioBlob && !currentMessage) {
        await handleTranscribe();
        return;
      }

      // 3. Envio normal de texto
      if (currentMessage) {
        onSend(currentMessage);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Erro no processamento";
      if (onDocumentUploadError) onDocumentUploadError(errorMessage);
    }
  };

  const handleCapturePhoto = (base64: string) => {
    const file = base64ToFile(base64, `capture-${Date.now()}.jpg`);
    setAttachedFile(file);
    setIsCameraOpen(false);
  };

  return (
    <div className="w-full">
      {/* Camera Capture Modal */}
      {isCameraOpen && (
        <CameraCapture
          onCapture={handleCapturePhoto}
          onClose={() => setIsCameraOpen(false)}
        />
      )}

      {/* Manus Unified Input */}
      <ManusInput
        value={message}
        onValueChange={setMessage}
        file={attachedFile}
        onFileChange={setAttachedFile}
        onSend={(msg, file) => handleSubmit(msg, file || undefined)}
        isLoading={isLoading || isUploading || isTranscribing}
        disabled={isLoading}
        isRecording={isRecording}
        onStartRecording={startRecording}
        onStopRecording={stopRecording}
        onCameraClick={() => setIsCameraOpen(true)}
        onFocusChange={onFocusChange}
        placeholder="Como posso ajudar hoje? (Fotos, Arquivos ou Texto)"
      />
    </div>
  );
}
