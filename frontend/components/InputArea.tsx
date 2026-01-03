"use client";

import React, { useState, useRef, FormEvent, useCallback, useEffect } from "react";
import { Send, Loader2, Mic } from "lucide-react";
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
    <div className={`relative transition-all duration-300 ${isHighContrast ? 'bg-black' : 'bg-treq-gray-50'}`}>
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

      <form onSubmit={handleSubmit} className="p-3 sm:p-4 max-w-5xl mx-auto">
        <div className={`relative flex items-end gap-2 p-2 rounded-[28px] border transition-all ${isHighContrast
          ? 'border-white bg-black'
          : 'border-treq-gray-200 bg-white shadow-sm focus-within:shadow-md focus-within:border-treq-yellow'
          }`}>
          {/* Menu de Anexos (Esquerda Style Grok) */}
          <div className="mb-1 ml-1">
            <InputActions
              onCameraClick={() => setIsCameraOpen(true)}
              onFileClick={() => fileInputRef.current?.click()}
              onMicClick={isRecording ? stopRecording : startRecording}
              isRecording={isRecording}
              disabled={isProcessing}
              hasFile={!!attachedFile}
            />
          </div>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept=".pdf,.docx,.pptx,.xlsx,.xls,image/*"
            aria-hidden="true"
          />

          <div className="flex-1 mb-1">
            {/* Área de Texto */}
            <ChatTextArea
              value={message}
              onChange={setMessage}
              onKeyDown={handleKeyDown}
              placeholder="Fazer uma pergunta..."
              disabled={isProcessing}
              isTranscribing={isTranscribing}
            />
          </div>

          {/* Ações de Envio / Mic */}
          <div className="flex items-center gap-2 mb-1 mr-1">
            {!message.trim() && !attachedFile ? (
              <button
                type="button"
                onClick={isRecording ? stopRecording : startRecording}
                className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${isRecording
                  ? 'bg-treq-error text-white animate-pulse'
                  : 'bg-treq-gray-100 text-treq-gray-600 hover:text-treq-yellow'
                  }`}
              >
                <Mic className="w-5 h-5" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={isProcessing}
                className="w-10 h-10 rounded-full bg-treq-yellow text-treq-gray-900 flex items-center justify-center hover:bg-treq-yellow-light transition-all shadow-md active:scale-95"
              >
                {isProcessing ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-4 h-4 ml-0.5" />
                )}
              </button>
            )}
          </div>
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
