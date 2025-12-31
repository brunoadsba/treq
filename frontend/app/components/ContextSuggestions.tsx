"use client";

import { useHighContrast } from "../hooks/useHighContrast";

interface ContextSuggestionsProps {
  onSelectSuggestion: (text: string) => void;
  userId?: string;
}

/**
 * Componente de sugestões contextuais para gestores operacionais
 * Baseado no histórico e contexto operacional da Sotreq
 */
export function ContextSuggestions({ onSelectSuggestion, userId = "default-user" }: ContextSuggestionsProps) {
  const isHighContrast = useHighContrast();

  // Sugestões baseadas no contexto operacional da Sotreq
  const contextSuggestions = [
    { 
      text: "Status de todas as unidades", 
      context: { type: "status", scope: "all_units" }
    },
    { 
      text: "Salvador vs Recife", 
      context: { type: "comparison", units: ["Salvador", "Recife"] }
    },
    { 
      text: "Alertas críticos", 
      context: { type: "alerts", priority: "critical" }
    },
    {
      text: "Métricas de cancelamentos",
      context: { type: "metrics", metric: "cancelamentos" }
    },
    {
      text: "Contenção operacional",
      context: { type: "procedure", name: "contenção" }
    }
  ];

  const handleSuggestionClick = (suggestion: typeof contextSuggestions[0]) => {
    onSelectSuggestion(suggestion.text);
    // Focar no input após selecionar sugestão
    setTimeout(() => {
      const input = document.querySelector('input[type="text"]') as HTMLInputElement;
      input?.focus();
    }, 100);
  };

  const handleKeyDown = (e: React.KeyboardEvent, suggestion: typeof contextSuggestions[0]) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleSuggestionClick(suggestion);
    }
  };

  return (
    <div 
      className={`hidden md:block border-b p-2 sm:p-3 ${
        isHighContrast 
          ? 'bg-black border-treq-yellow' 
          : 'bg-treq-gray-50 border-treq-gray-200'
      }`}
      role="region"
      aria-label="Sugestões contextuais"
    >
      <div className="flex gap-1.5 sm:gap-2 overflow-x-auto pb-1 scrollbar-hide -mx-2 px-2 sm:mx-0 sm:px-0 justify-center">
        {contextSuggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => handleSuggestionClick(suggestion)}
            onKeyDown={(e) => handleKeyDown(e, suggestion)}
            className={`text-xs sm:text-sm px-2 sm:px-2.5 py-1 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 whitespace-nowrap flex-shrink-0 min-h-[28px] sm:min-h-[32px] ${
              isHighContrast
                ? 'bg-treq-yellow-dark border border-treq-yellow text-black hover:bg-treq-yellow'
                : 'bg-white border border-treq-gray-300 hover:bg-treq-gray-100 text-treq-gray-700'
            }`}
            aria-label={`Sugestão: ${suggestion.text}`}
          >
            {suggestion.text}
          </button>
        ))}
      </div>
    </div>
  );
}
