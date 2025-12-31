"use client";

import { useState, FormEvent, useRef, useEffect } from "react";
import { Mic, Send, Loader2, Paperclip } from "lucide-react";
import { useAudioRecorder } from "../hooks/useAudioRecorder";
import { useAudioTranscription } from "../hooks/useAudioTranscription";
import { useDocumentUpload } from "../hooks/useDocumentUpload";
import { useHighContrast } from "../hooks/useHighContrast";
import { useTheme } from "../hooks/useTheme";
import { ContextSuggestions } from "./ContextSuggestions";

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
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const { isRecording, audioBlob, startRecording, stopRecording, clearRecording } = useAudioRecorder();
  const { isTranscribing, transcribeAudio } = useAudioTranscription();
  const { isUploading, uploadDocument } = useDocumentUpload();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isHighContrast = useHighContrast();
  const [theme] = useTheme();
  
  // Listener para mudanças no modo alto contraste
  useEffect(() => {
    const handleHighContrastChange = () => {
      // Forçar re-render quando modo alto contraste mudar
      window.location.reload();
    };
    
    window.addEventListener("highContrastChanged", handleHighContrastChange);
    return () => {
      window.removeEventListener("highContrastChanged", handleHighContrastChange);
    };
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    // Se há arquivo anexado, enviar arquivo + mensagem
    if (attachedFile) {
      try {
        // Enviar arquivo com mensagem
        const result = await uploadDocument(attachedFile, undefined, message.trim() || undefined);
        
        // Se há mensagem, também enviar como mensagem de chat
        if (message.trim()) {
          // Enviar mensagem explicando o que fazer com o arquivo
          onSend(message.trim());
        }
        
        if (onDocumentUploaded) {
          onDocumentUploaded(attachedFile.name, result.chunksIndexed);
        }
        
        // Limpar estado
        setAttachedFile(null);
        setMessage("");
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Erro desconhecido ao fazer upload";
        if (onDocumentUploadError) {
          onDocumentUploadError(errorMessage);
        }
        console.error("Erro ao fazer upload:", error);
      }
      return;
    }
    
    // Comportamento normal: apenas enviar mensagem
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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Apenas anexar o arquivo, não enviar ainda
    setAttachedFile(file);
    
    // Limpar input para permitir selecionar o mesmo arquivo novamente
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleRemoveFile = () => {
    setAttachedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const isProcessing = isLoading || isTranscribing || isUploading;

  return (
    <div className={`border-t ${isHighContrast ? 'border-white bg-black' : 'border-treq-gray-200 bg-white'}`}>
      {/* Sugestões contextuais para gestores */}
      <ContextSuggestions 
        onSelectSuggestion={setMessage}
        userId={userId}
      />
      
      {/* Área de áudio gravado - melhorada */}
      {audioBlob && !isTranscribing && (
        <div className={`px-4 py-3 border-b flex items-center justify-between animate-fade-in ${
          isHighContrast 
            ? 'bg-treq-yellow-dark border-treq-yellow' 
            : 'bg-treq-info-light border-treq-info'
        }`}>
          <div className="flex items-center gap-2">
            <Mic className={`w-4 h-4 ${isHighContrast ? 'text-black' : 'text-treq-info'}`} />
            <span className={`text-sm font-medium ${
              isHighContrast ? 'text-black' : 'text-treq-info-dark'
            }`}>
              Áudio gravado e pronto para envio
            </span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={clearRecording}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 ${
                isHighContrast 
                  ? 'text-black hover:bg-treq-yellow-light' 
                  : 'text-treq-info-dark hover:bg-treq-info'
              }`}
              aria-label="Cancelar gravação de áudio"
            >
              Cancelar
            </button>
            <button
              onClick={handleAudioSend}
              disabled={isProcessing}
              className={`px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 ${
                isHighContrast
                  ? 'bg-treq-yellow text-black hover:bg-treq-yellow-light'
                  : 'bg-treq-info text-white hover:bg-treq-info-dark'
              }`}
              aria-label="Enviar áudio gravado"
            >
              Enviar Áudio
            </button>
          </div>
        </div>
      )}

      {/* Área de arquivo anexado */}
      {attachedFile && (
        <div className={`px-4 py-3 border-b flex items-center justify-between animate-fade-in ${
          isHighContrast 
            ? 'bg-treq-yellow-dark border-treq-yellow' 
            : 'bg-treq-info-light border-treq-info'
        }`}>
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${
              isHighContrast ? 'bg-treq-yellow' : 'bg-treq-info'
            }`}>
              <Paperclip className={`w-5 h-5 ${isHighContrast ? 'text-black' : 'text-white'}`} />
            </div>
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium truncate ${
                isHighContrast ? 'text-black' : 'text-treq-info-dark'
              }`}>
                {attachedFile.name}
              </p>
              <p className={`text-xs ${
                isHighContrast ? 'text-black/70' : 'text-treq-info-dark/70'
              }`}>
                {(attachedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>
          <button
            onClick={handleRemoveFile}
            className={`flex-shrink-0 ml-2 p-1.5 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 ${
              isHighContrast 
                ? 'text-black hover:bg-treq-yellow-light' 
                : 'text-treq-info-dark hover:bg-treq-info'
            }`}
            aria-label="Remover arquivo anexado"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Área de input */}
      <form onSubmit={handleSubmit} className="p-2 sm:p-3 md:p-4 lg:p-5">
        <div className="flex gap-1.5 sm:gap-2 md:gap-3">
          {/* Input de arquivo oculto */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.pptx,.xlsx,.xls,.jpg,.jpeg,.png,.gif,.bmp,.tiff,.tif,.webp"
            onChange={handleFileSelect}
            disabled={isProcessing}
            className="hidden"
            id="file-upload"
            aria-label="Selecionar arquivo para upload"
          />

          {/* Botão de anexar documento - Touch target 48px mínimo */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isProcessing || !!audioBlob}
            className={`min-w-[44px] min-h-[44px] sm:min-w-[48px] sm:min-h-[48px] px-2 sm:px-3 md:px-4 py-2 sm:py-3 rounded-lg sm:rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 hover:scale-105 active:scale-95 ${
              attachedFile
                ? isHighContrast
                  ? 'bg-treq-yellow text-black hover:bg-treq-yellow-light'
                  : 'bg-treq-info text-white hover:bg-treq-info-dark'
                : isHighContrast
                ? 'bg-treq-yellow text-black hover:bg-treq-yellow-light'
                : 'bg-treq-gray-100 hover:bg-treq-gray-200 text-treq-gray-700'
            }`}
            title={attachedFile ? "Arquivo anexado - Clique para trocar" : "Anexar documento"}
            aria-label={attachedFile ? "Arquivo anexado" : "Anexar documento"}
          >
            <Paperclip className={`w-5 h-5 sm:w-6 sm:h-6 transition-transform ${attachedFile ? 'rotate-45' : 'hover:rotate-12'}`} />
          </button>

          {/* Botão de gravação - Touch target 48px mínimo com feedback visual melhorado */}
          <button
            type="button"
            onClick={handleAudioRecord}
            disabled={isProcessing || !!audioBlob}
            className={`min-w-[44px] min-h-[44px] sm:min-w-[48px] sm:min-h-[48px] px-2 sm:px-3 md:px-4 py-2 sm:py-3 rounded-lg sm:rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 active:scale-95 ${
              isRecording
                ? "bg-treq-error text-white hover:bg-treq-error-dark animate-pulse shadow-lg shadow-treq-error/50"
                : isHighContrast
                ? "bg-treq-yellow text-black hover:bg-treq-yellow-light hover:scale-105"
                : "bg-treq-gray-100 hover:bg-treq-gray-200 text-treq-gray-700 hover:scale-105"
            }`}
            title={isRecording ? "Parar gravação" : "Gravar áudio"}
            aria-label={isRecording ? "Parar gravação" : "Iniciar gravação de áudio"}
            aria-pressed={isRecording}
          >
            <Mic className={`w-5 h-5 sm:w-6 sm:h-6 transition-transform ${isRecording ? 'animate-pulse scale-110' : ''}`} />
          </button>

          {/* Input de texto - Touch target 48px mínimo */}
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={
              attachedFile 
                ? "O que você quer fazer com este arquivo?" 
                : isTranscribing 
                ? "Transcrevendo..." 
                : isUploading 
                ? "Enviando..." 
                : "Digite sua mensagem..."
            }
            disabled={isProcessing || !!audioBlob}
            className={`flex-1 min-h-[44px] sm:min-h-[48px] px-3 sm:px-4 md:px-5 py-2 sm:py-3 rounded-lg sm:rounded-xl text-sm sm:text-base focus:outline-none focus:ring-2 disabled:opacity-50 transition-all ${
              isHighContrast
                ? 'border-white bg-black text-white focus:ring-treq-yellow placeholder:text-treq-gray-400'
                : 'border-treq-gray-300 bg-white text-treq-gray-900 focus:ring-treq-yellow focus:border-transparent placeholder:text-treq-gray-400'
            }`}
            style={{ 
              fontSize: isHighContrast ? '1.125rem' : undefined
            }}
            aria-label="Campo de entrada de mensagem"
            aria-describedby={isTranscribing ? "transcribing-status" : undefined}
          />
          {isTranscribing && (
            <span id="transcribing-status" className="sr-only">
              Transcrevendo áudio, aguarde...
            </span>
          )}

          {/* Botão de enviar - Touch target 48px mínimo */}
          <button
            type="submit"
            disabled={isProcessing || (!message.trim() && !audioBlob && !attachedFile)}
            className={`min-h-[44px] sm:min-h-[48px] px-3 sm:px-4 md:px-6 py-2 sm:py-3 rounded-lg sm:rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-1 sm:gap-2 focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 hover:scale-105 active:scale-95 disabled:hover:scale-100 ${
              theme === "dark"
                ? 'bg-treq-yellow hover:bg-treq-yellow-light shadow-md hover:shadow-lg'
                : isHighContrast
                ? 'bg-treq-yellow hover:bg-treq-yellow-light shadow-md hover:shadow-lg'
                : 'bg-treq-yellow hover:bg-treq-yellow-dark shadow-md hover:shadow-lg'
            }`}
            style={{
              color: "#000000", // Preto puro sempre para máximo contraste
              fontWeight: theme === "dark" ? 700 : 600, // Mais pesado no modo escuro
              WebkitFontSmoothing: "antialiased",
              MozOsxFontSmoothing: "grayscale",
            }}
            aria-label={isProcessing ? "Processando, aguarde..." : "Enviar mensagem"}
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
                <span className="hidden sm:inline">
                  {isUploading ? "Enviando..." : isTranscribing ? "Transcrevendo..." : "Enviando..."}
                </span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4 sm:w-5 sm:h-5" />
                <span className="hidden sm:inline">Enviar</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

