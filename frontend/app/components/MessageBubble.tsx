"use client";

import { ChatMessage } from "../hooks/useChat";
import { Volume2, Loader2, Pause, Play } from "lucide-react";
import { useTTS } from "../hooks/useTTS";
import { FormattedMessage } from "./FormattedMessage";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const { speak, pause, resume, stop, isSpeaking, isPaused, isLoading } = useTTS();

  const handleAudioControl = async () => {
    if (!isUser && message.content) {
      if (isLoading) {
        // Não fazer nada enquanto carrega
        return;
      }
      
      if (isPaused) {
        // Retomar reprodução
        await resume();
      } else if (isSpeaking) {
        // Pausar reprodução
        pause();
      } else {
        // Iniciar reprodução
        await speak(message.content);
      }
    }
  };

  // Determinar ícone e título baseado no estado
  const getIconAndTitle = () => {
    if (isLoading) {
      return {
        icon: <Loader2 className="w-4 h-4 animate-spin" />,
        title: "Carregando áudio...",
      };
    }
    
    if (isPaused) {
      return {
        icon: <Play className="w-4 h-4" />,
        title: "Retomar reprodução",
      };
    }
    
    if (isSpeaking) {
      return {
        icon: <Pause className="w-4 h-4" />,
        title: "Pausar reprodução",
      };
    }
    
    return {
      icon: <Volume2 className="w-4 h-4" />,
      title: "Ouvir resposta",
    };
  };

  const { icon, title } = getIconAndTitle();

  return (
    <div
      className={`flex w-full ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-[85%] rounded-lg ${
          isUser
            ? "bg-sotreq-yellow text-gray-900 px-4 py-3"
            : "bg-white border border-gray-200 shadow-sm px-5 py-4"
        }`}
      >
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
        ) : (
          <FormattedMessage content={message.content} />
        )}
        
        {!isUser && message.content && (
          <div className="flex items-center gap-2 mt-4 pt-3 border-t border-gray-100">
            <button
              onClick={handleAudioControl}
              disabled={isLoading}
              className={`p-1 transition-colors ${
                isSpeaking || isPaused
                  ? "text-blue-600 hover:text-blue-700"
                  : "text-gray-500 hover:text-gray-700"
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              title={title}
            >
              {icon}
            </button>
            
            {(isSpeaking || isPaused) && (
              <button
                onClick={stop}
                className="p-1 text-gray-400 hover:text-gray-600 transition-colors text-xs"
                title="Parar reprodução"
              >
                Parar
              </button>
            )}
          </div>
        )}
        
        {message.timestamp && (
          <p className="text-xs mt-1 opacity-60">
            {new Date(message.timestamp).toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        )}
      </div>
    </div>
  );
}
