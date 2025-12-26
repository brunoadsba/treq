"use client";

import { ChatMessage } from "../hooks/useChat";
import { MessageBubble } from "./MessageBubble";
import { Loader2 } from "lucide-react";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export function MessageList({ messages, isLoading = false }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p className="text-lg mb-2 font-semibold">Bem-vindo ao Assistente Operacional</p>
          <p className="text-sm">
            Faça uma pergunta para começar a conversa
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message, index) => (
        <MessageBubble key={index} message={message} />
      ))}
      
      {isLoading && (
        <div className="flex items-center gap-2 text-gray-500 px-4 py-3">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Assistente está pensando...</span>
        </div>
      )}
    </div>
  );
}

