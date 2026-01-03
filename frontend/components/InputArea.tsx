"use client";

import React, { useState, useRef, FormEvent, useCallback, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";
import { useAudioTranscription } from "@/hooks/useAudioTranscription";
import { useDocumentUpload } from "@/hooks/useDocumentUpload";
import { useHighContrast } from "@/hooks/useHighContrast";
import { CameraCapture } from "@/src/features/vision/components/CameraCapture";
import { base64ToFile, fileToBase64 } from "@/src/features/chat/utils/file-utils";

// Novos subcomponentes modulares (Regra 5: Split files)
import { ChatTextArea } from "@/src/features/chat/components/InputArea/subcomponents/ChatTextArea";
import { FilePreviewSection } from "@/src/features/chat/components/InputArea/subcomponents/FilePreviewSection";
import { AudioRecorderSection } from "@/src/features/chat/components/InputArea/subcomponents/AudioRecorderSection";
import { InputActions } from "@/src/features/chat/components/InputArea/subcomponents/InputActions";

interface InputAreaProps {
  onSend: (message: string, actionId?: string, imageUrl?: string) => void;
  isLoading: boolean;
  onDocumentUploaded?: (filename: string, chunks: number) => void;
  onDocumentUploadError?: (error: string) => void;
}

export function InputArea({
  onSend,
  isLoading,
  onDocumentUploaded,
  onDocumentUploadError,
}: InputAreaProps) {
  const [message, setMessage] = useState("");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [cameraPreview, setCameraPreview] = useState<string | null>(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleSubmit = async (e?: FormEvent) => {
    if (e) e.preventDefault();

    const currentMessage = message.trim();
    const isProcessing = isLoading || isTranscribing || isUploading;

    if (isProcessing) return;

    try {
      let imageUrl: string | undefined = undefined;

      // 1. Prioridade: Upload de Documento/Imagem
      if (attachedFile) {
        // Criar URL para visualização local imediata (UX)
        const localPreviewUrl = attachedFile.type.startsWith('image/')
          ? createSecureBlobUrl(attachedFile)
          : undefined;

        // Se for imagem, converter para base64 para o backend realmente "ver" o conteúdo
        if (attachedFile.type.startsWith('image/')) {
          imageUrl = await fileToBase64(attachedFile);
        }

        // Upload oficial para o RAG (Base de conhecimento)
        const result = await uploadDocument(attachedFile, undefined, currentMessage || undefined);

        if (onDocumentUploaded) {
          onDocumentUploaded(attachedFile.name, result.chunksIndexed);
        }

        const chatText = currentMessage || `[Arquivo: ${attachedFile.name}]`;
        // Passamos o localPreviewUrl para a bolha do chat (eficiência) e o base64 real para o Hook/Backend
        onSend(chatText, undefined, imageUrl || localPreviewUrl);

        // Limpar estado de anexo
        setAttachedFile(null);
        setCameraPreview(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
        setMessage("");
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
        setMessage("");
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Erro no processamento";
      if (onDocumentUploadError) onDocumentUploadError(errorMessage);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAttachedFile(file);
      setCameraPreview(null);
    }
  };

  const handleCapturePhoto = (base64: string) => {
    const file = base64ToFile(base64, `capture-${Date.now()}.jpg`);
    setAttachedFile(file);
    setCameraPreview(base64);
    setIsCameraOpen(false);
  };

  const handleRemoveFile = useCallback(() => {
    setAttachedFile(null);
    setCameraPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
      if (!isMobile) {
        e.preventDefault();
        handleSubmit();
      }
    }
  };

  const isProcessing = isLoading || isTranscribing || isUploading;

  return (
    <div className={`relative transition-all duration-300 ${isHighContrast ? 'bg-black' : 'bg-treq-gray-50'
      }`}>
      {/* Seção de Preview de Arquivo */}
      <FilePreviewSection
        attachedFile={attachedFile}
        cameraPreview={cameraPreview}
        onRemove={handleRemoveFile}
      />

      {/* Seção de Áudio Gravado */}
      <AudioRecorderSection
        audioBlob={audioBlob}
        isTranscribing={isTranscribing}
        onClear={clearRecording}
        onSend={handleTranscribe}
        isProcessing={isProcessing}
      />

      <form onSubmit={handleSubmit} className="p-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] sm:p-3 md:p-4 lg:p-5">
        <div className="flex items-center gap-2 max-w-5xl mx-auto">
          {/* Botões de Ação */}
          <InputActions
            onCameraClick={() => setIsCameraOpen(true)}
            onFileClick={() => fileInputRef.current?.click()}
            onMicClick={isRecording ? stopRecording : startRecording}
            isRecording={isRecording}
            disabled={isProcessing}
            hasFile={!!attachedFile}
          />

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept=".pdf,.docx,.pptx,.xlsx,.xls,image/*"
            aria-hidden="true"
          />

          {/* Área de Texto com Auto-resize */}
          <ChatTextArea
            value={message}
            onChange={setMessage}
            onKeyDown={handleKeyDown}
            placeholder={
              attachedFile ? "O que deseja fazer com este arquivo?" :
                isTranscribing ? "Transcrevendo..." :
                  isUploading ? "Enviando..." : "Digite sua mensagem..."
            }
            disabled={isProcessing}
            isTranscribing={isTranscribing}
          />

          {/* Botão de Enviar */}
          <button
            type="submit"
            disabled={isProcessing || (!message.trim() && !attachedFile)}
            className={`min-w-[44px] min-h-[44px] sm:min-w-[52px] sm:min-h-[52px] rounded-xl font-semibold transition-all duration-300 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 ${isProcessing || (!message.trim() && !attachedFile)
              ? 'bg-treq-gray-200 text-treq-gray-400 cursor-not-allowed translate-y-0 shadow-none'
              : isHighContrast
                ? 'bg-treq-yellow text-black hover:bg-treq-yellow-light shadow-lg hover:shadow-treq-yellow/30'
                : 'bg-treq-yellow text-treq-black hover:bg-treq-yellow-light shadow-lg hover:shadow-treq-yellow/20 hover:-translate-y-0.5 active:translate-y-0'
              }`}
            aria-label="Enviar mensagem"
          >
            {isProcessing ? (
              <Loader2 className="w-5 h-5 sm:w-6 sm:h-6 animate-spin" />
            ) : (
              <Send className="w-5 h-5 sm:w-6 sm:h-6 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            )}
          </button>
        </div>
      </form>

      {/* Modal de Câmera */}
      {isCameraOpen && (
        <CameraCapture
          onCapture={handleCapturePhoto}
          onClose={() => setIsCameraOpen(false)}
        />
      )}
    </div>
  );
}
