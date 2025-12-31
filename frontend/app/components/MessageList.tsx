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
      <div className="h-full w-full flex flex-col items-center justify-center text-treq-gray-500 bg-treq-gray-50 p-4 sm:p-6 md:p-8 lg:p-10 overflow-hidden">
        <div className="w-full max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-md p-6 sm:p-8 md:p-10 lg:p-12 text-left">
            {/* Título */}
            <h2 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl mb-4 sm:mb-5 md:mb-6 font-bold text-treq-gray-900 leading-tight">
              Bem-vindo ao Assistente Operacional
            </h2>
            
            {/* Descrição */}
            <p className="text-[15px] sm:text-base md:text-lg lg:text-xl text-treq-gray-700 mb-6 sm:mb-7 md:mb-8 leading-[1.75] sm:leading-[1.8] md:leading-[1.85] text-justify">
              Faça uma pergunta para começar a conversa ou use as ações rápidas acima para acessar informações operacionais rapidamente.
            </p>
            
            {/* Divisor */}
            <div className="mt-8 sm:mt-9 md:mt-10 pt-6 sm:pt-7 md:pt-8 border-t-2 border-treq-gray-200">
              {/* Título da seção */}
              <p className="text-sm sm:text-base md:text-lg font-semibold mb-4 sm:mb-5 md:mb-6 text-treq-gray-900">
                Sugestões de uso:
              </p>
              
              {/* Lista de sugestões */}
              <ul className="space-y-3 sm:space-y-4 md:space-y-5">
                <li className="flex items-start gap-3 sm:gap-3.5 md:gap-4">
                  <span className="text-treq-yellow-dark mt-[2px] sm:mt-[3px] flex-shrink-0 font-bold text-lg sm:text-xl md:text-2xl">•</span>
                  <span className="text-[15px] sm:text-base md:text-lg text-treq-gray-700 leading-[1.75] sm:leading-[1.8] md:leading-[1.85] text-justify flex-1">
                    Consulte alertas críticos e status operacional das unidades
                  </span>
                </li>
                <li className="flex items-start gap-3 sm:gap-3.5 md:gap-4">
                  <span className="text-treq-yellow-dark mt-[2px] sm:mt-[3px] flex-shrink-0 font-bold text-lg sm:text-xl md:text-2xl">•</span>
                  <span className="text-[15px] sm:text-base md:text-lg text-treq-gray-700 leading-[1.75] sm:leading-[1.8] md:leading-[1.85] text-justify flex-1">
                    Obtenha informações sobre procedimentos e métricas
                  </span>
                </li>
                <li className="flex items-start gap-3 sm:gap-3.5 md:gap-4">
                  <span className="text-treq-yellow-dark mt-[2px] sm:mt-[3px] flex-shrink-0 font-bold text-lg sm:text-xl md:text-2xl">•</span>
                  <span className="text-[15px] sm:text-base md:text-lg text-treq-gray-700 leading-[1.75] sm:leading-[1.8] md:leading-[1.85] text-justify flex-1">
                    Faça perguntas em linguagem natural sobre operações
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="h-full w-full overflow-y-auto overflow-x-hidden p-2 sm:p-3 md:p-3 lg:p-4 space-y-2 sm:space-y-3 md:space-y-4 bg-treq-gray-50"
      style={{ 
        maxHeight: '100%',
        overscrollBehavior: 'contain'
      }}
    >
      {messages.map((message, index) => (
        <MessageBubble key={index} message={message} />
      ))}
      
      {isLoading && (
        <div className="flex items-center gap-2 sm:gap-3 text-treq-gray-600 px-2 sm:px-3 md:px-2 lg:px-3 py-3 sm:py-4 animate-fade-in">
          <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 animate-spin text-treq-yellow flex-shrink-0" />
          <span className="text-sm sm:text-base font-medium">Assistente está pensando...</span>
        </div>
      )}
    </div>
  );
}

