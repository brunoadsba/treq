"use client";

import { Logo } from "./Logo";
import { useHighContrast, toggleHighContrast } from "../hooks/useHighContrast";
import { useTheme } from "../hooks/useTheme";
import { Contrast, Sun, Moon } from "lucide-react";
import { ConversationMenu } from "./ConversationMenu";

interface HeaderProps {
  title?: string;
  hasMessages?: boolean;
  onNewConversation?: () => void;
  onShowHistory?: () => void;
  onExportConversation?: () => void;
}

export function Header({ 
  title = "Assistente Operacional",
  hasMessages = false,
  onNewConversation,
  onShowHistory,
  onExportConversation,
}: HeaderProps) {
  const isHighContrast = useHighContrast();
  const [theme, setTheme] = useTheme();

  return (
    <header className="bg-treq-black text-white p-2 sm:p-2.5 md:p-3 lg:p-3.5 shadow-md">
      <div className="flex items-center justify-between gap-2 sm:gap-3">
        {/* Mobile: [Ícone T] Treq (esquerda) + Assistente Operacional (centro) */}
        <div className="flex items-center min-w-0 flex-1 sm:hidden">
          {/* Ícone T + Treq (esquerda) */}
          <div className="flex items-center gap-1 flex-shrink-0">
            <Logo variant="icon" size="sm" className="text-white" />
            {/* Nome Treq - mesmo tamanho visual do ícone (24px) */}
            <span className="text-white font-bold tracking-tight flex-shrink-0" style={{ fontSize: '24px', lineHeight: '24px' }}>Treq</span>
          </div>
          {/* Assistente Operacional - centralizado, ocupando espaço restante, 80% do tamanho de Treq */}
          <h1 className="flex-1 text-center font-semibold truncate ml-6" style={{ fontSize: '19.2px', lineHeight: '19.2px' }}>
            {title}
          </h1>
        </div>
        
        {/* Desktop: Layout melhorado - Logo maior + título centralizado */}
        <div className="hidden sm:flex items-center min-w-0 flex-1">
          {/* Logo + Treq (esquerda) - tamanho maior no desktop */}
          <div className="flex items-center gap-2 md:gap-3 flex-shrink-0">
            <Logo variant="horizontal" size="md" className="text-white" />
          </div>
          {/* Assistente Operacional - centralizado no espaço restante */}
          <h1 className="flex-1 text-center text-base md:text-lg lg:text-xl xl:text-2xl font-semibold truncate ml-6">
            {title}
          </h1>
        </div>
        <div className="flex items-center gap-2 sm:gap-2.5 md:gap-3 flex-shrink-0">
          {/* Menu de Conversas */}
          {(onNewConversation || onShowHistory || onExportConversation) && (
            <ConversationMenu
              hasMessages={hasMessages}
              onNewConversation={onNewConversation || (() => {})}
              onShowHistory={onShowHistory || (() => {})}
              onExportConversation={onExportConversation || (() => {})}
            />
          )}
          
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="p-1.5 sm:p-2 rounded-lg hover:bg-treq-gray-800 transition-colors flex-shrink-0 min-w-[36px] min-h-[36px] sm:min-w-[40px] sm:min-h-[40px] md:min-w-[44px] md:min-h-[44px] flex items-center justify-center"
            aria-label={theme === "dark" ? "Alternar para tema claro" : "Alternar para tema escuro"}
            title={theme === "dark" ? "Tema claro" : "Tema escuro"}
          >
            {theme === "dark" ? (
              <Sun className="w-4 h-4 sm:w-5 sm:h-5" />
            ) : (
              <Moon className="w-4 h-4 sm:w-5 sm:h-5" />
            )}
          </button>
          <button
            onClick={toggleHighContrast}
            className="p-1.5 sm:p-2 rounded-lg hover:bg-treq-gray-800 transition-colors flex-shrink-0 min-w-[36px] min-h-[36px] sm:min-w-[40px] sm:min-h-[40px] md:min-w-[44px] md:min-h-[44px] flex items-center justify-center"
            aria-label={isHighContrast ? "Desativar alto contraste" : "Ativar alto contraste"}
            title={isHighContrast ? "Desativar alto contraste" : "Ativar alto contraste"}
          >
            <Contrast className="w-4 h-4 sm:w-5 sm:h-5" />
          </button>
        </div>
      </div>
    </header>
  );
}

