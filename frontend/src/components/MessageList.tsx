"use client";

import { ChatMessage } from "@/hooks/useChat";
import { MessageBubble } from "./MessageBubble";
import { Loader2 } from "lucide-react";
import { useRef, useEffect } from "react";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export function MessageList({ messages, isLoading = false }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  const lastMessagesLength = useRef(messages.length);

  // Smart Scroll Logic
  useEffect(() => {
    const scrollContainer = scrollRef.current;
    if (!scrollContainer) return;

    const { scrollHeight, clientHeight, scrollTop } = scrollContainer;
    // Threshold de 150px para considerar que o usuário está "no fundo"
    const isNearBottom = scrollHeight - clientHeight - scrollTop < 150;

    // Verificar se a última mensagem é do usuário (forçar scroll)
    const lastMessageIsUser = messages.length > 0 && messages[messages.length - 1].role === "user";
    const hasNewMessage = messages.length > lastMessagesLength.current;

    if (isNearBottom || (hasNewMessage && lastMessageIsUser)) {
      scrollContainer.scrollTo({
        top: scrollHeight - clientHeight,
        behavior: lastMessageIsUser ? "smooth" : "auto",
      });
    }

    lastMessagesLength.current = messages.length;
  }, [messages, isLoading]);
  if (messages.length === 0) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center p-6 sm:p-12 overflow-hidden">
        <div className="flex flex-col items-center max-w-lg w-full text-center animate-fade-in translate-y-[-10%]">
          {/* Logo Minimalista Pulsante */}
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-treq-yellow to-yellow-300 rounded-full blur opacity-25 animate-pulse"></div>
            <div className="relative w-24 h-24 sm:w-28 sm:h-28 bg-white rounded-full flex items-center justify-center shadow-2xl border border-treq-gray-100 transform transition-transform group-hover:scale-105">
              <span className="text-5xl sm:text-6xl font-black text-treq-gray-900 italic select-none">T</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={scrollRef}
      className="h-full w-full overflow-y-auto overflow-x-hidden p-2 sm:p-3 md:p-3 lg:p-4 space-y-2 sm:space-y-3 md:space-y-4 bg-treq-gray-50"
      style={{
        maxHeight: '100%',
        overscrollBehavior: 'contain'
      }}
    >
      {messages.map((message, index) => (
        <MessageBubble
          key={index}
          message={message}
          isLoading={isLoading}
        />
      ))}

      {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
        <div className="flex items-center gap-2 sm:gap-3 text-treq-gray-600 px-2 sm:px-3 md:px-2 lg:px-3 py-3 sm:py-4 animate-fade-in">
          <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 animate-spin text-treq-yellow flex-shrink-0" />
          <span className="text-sm sm:text-base font-medium">Assistente está pensando...</span>
        </div>
      )}
    </div>
  );
}

