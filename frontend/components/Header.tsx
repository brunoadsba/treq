"use client";

import { Logo } from "./Logo";
import { useHighContrast, toggleHighContrast } from "@/hooks/useHighContrast";
import { useTheme } from "@/hooks/useTheme";
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
        {/* Lado Esquerdo: Logo e Título */}
        <div className="flex items-center min-w-0 flex-1">
          <div className="flex items-center gap-2 md:gap-3 flex-shrink-0">
            <Logo variant="horizontal" size="md" className="text-white" />
          </div>
          <h1 className="flex-1 text-center text-base md:text-lg lg:text-xl xl:text-2xl font-semibold truncate ml-6">
            {title}
          </h1>
        </div>

        {/* Lado Direito: Controles Funcionais */}
        <div className="flex items-center gap-2 sm:gap-2.5 md:gap-3 flex-shrink-0">
          {/* Menu de Conversas */}
          {(onNewConversation || onShowHistory || onExportConversation) && (
            <ConversationMenu
              hasMessages={hasMessages}
              onNewConversation={onNewConversation || (() => { })}
              onShowHistory={onShowHistory || (() => { })}
              onExportConversation={onExportConversation || (() => { })}
            />
          )}

          {/* Toggle de Tema Light/Dark */}
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="p-1.5 sm:p-2 rounded-lg hover:bg-white/10 transition-colors flex items-center justify-center min-w-[36px] min-h-[36px]"
            aria-label={theme === "dark" ? "Modo Claro" : "Modo Escuro"}
          >
            {theme === "dark" ? <Sun size={20} /> : <Moon size={20} />}
          </button>

          {/* Toggle de Alto Contraste */}
          <button
            onClick={toggleHighContrast}
            className="p-1.5 sm:p-2 rounded-lg hover:bg-white/10 transition-colors flex items-center justify-center min-w-[36px] min-h-[36px]"
            aria-label="Alto Contraste"
          >
            <Contrast size={20} />
          </button>
        </div>
      </div>
    </header>
  );
}

