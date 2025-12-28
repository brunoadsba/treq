"use client";

import { useState, FormEvent, useRef } from "react";
import { Mic, Send, Loader2, Paperclip } from "lucide-react";
import { useAudioRecorder } from "../hooks/useAudioRecorder";
import { useAudioTranscription } from "../hooks/useAudioTranscription";
import { useDocumentUpload } from "../hooks/useDocumentUpload";

interface InputAreaProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  userId?: string;
  conversationId?: string;
  onDocumentUploaded?: (fileName: string, chunksIndexed: number) => void;
  onDocumentUploadError?: (error: string) => void;
}

export function InputArea({
  onSend,
  isLoading = false,
  placeholder = "Digite sua mensagem...",
  userId = "default-user",
  conversationId,
  onDocumentUploaded,
  onDocumentUploadError,
}: InputAreaProps) {
  const [message, setMessage] = useState("");
  const { isRecording, audioBlob, startRecording, stopRecording, clearRecording } = useAudioRecorder();
  const { isTranscribing, transcribeAudio } = useAudioTranscription();
  const { isUploading, uploadDocument } = useDocumentUpload();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !isTranscribing) {
      onSend(message);
      setMessage("");
    }
  };

  const handleAudioRecord = async () => {
    if (isRecording) {
      stopRecording();
    } else {
      try {
        await startRecording();
      } catch (error) {
        console.error("Erro ao iniciar gravação:", error);
      }
    }
  };

  const handleAudioSend = async () => {
    if (!audioBlob) return;

    try {
      const transcript = await transcribeAudio(audioBlob, userId, conversationId);
      if (transcript) {
        onSend(transcript);
        clearRecording();
      }
    } catch (error) {
      console.error("Erro ao transcrever áudio:", error);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const result = await uploadDocument(file);
      if (onDocumentUploaded) {
        onDocumentUploaded(file.name, result.chunksIndexed);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Erro desconhecido ao fazer upload";
      if (onDocumentUploadError) {
        onDocumentUploadError(errorMessage);
      }
      console.error("Erro ao fazer upload:", error);
    } finally {
      // Limpar input para permitir selecionar o mesmo arquivo novamente
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const isProcessing = isLoading || isTranscribing || isUploading;

  return (
    <div className="border-t border-gray-200 bg-white">
      {/* Área de áudio gravado */}
      {audioBlob && !isTranscribing && (
        <div className="px-4 py-2 bg-blue-50 border-b border-blue-200 flex items-center justify-between">
          <span className="text-sm text-blue-700">Áudio gravado</span>
          <div className="flex gap-2">
            <button
              onClick={clearRecording}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Cancelar
            </button>
            <button
              onClick={handleAudioSend}
              disabled={isProcessing}
              className="text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Enviar
            </button>
          </div>
        </div>
      )}

      {/* Área de input */}
      <form onSubmit={handleSubmit} className="p-4">
        <div className="flex gap-2">
          {/* Input de arquivo oculto */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.pptx,.xlsx,.xls"
            onChange={handleFileSelect}
            disabled={isProcessing}
            className="hidden"
            id="file-upload"
          />

          {/* Botão de anexar documento */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isProcessing || !!audioBlob}
            className="px-4 py-2 rounded-lg font-medium transition-colors bg-gray-100 hover:bg-gray-200 text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Anexar documento (PDF, DOCX, PPTX, Excel)"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          {/* Botão de gravação */}
          <button
            type="button"
            onClick={handleAudioRecord}
            disabled={isProcessing || !!audioBlob}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isRecording
                ? "bg-red-500 hover:bg-red-600 text-white"
                : "bg-gray-100 hover:bg-gray-200 text-gray-700"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
            title={isRecording ? "Parar gravação" : "Gravar áudio"}
          >
            <Mic className="w-5 h-5" />
          </button>

          {/* Input de texto */}
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={isTranscribing ? "Transcrevendo áudio..." : placeholder}
            disabled={isProcessing || !!audioBlob}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sotreq-yellow focus:border-transparent disabled:opacity-50"
          />

          {/* Botão de enviar */}
          <button
            type="submit"
            disabled={isProcessing || (!message.trim() && !audioBlob)}
            className="px-6 py-2 bg-sotreq-yellow hover:bg-sotreq-yellow-dark text-gray-900 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                {isUploading ? "Enviando..." : isTranscribing ? "Transcrevendo..." : "Enviando..."}
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Enviar
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

