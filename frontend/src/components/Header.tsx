"use client";

import { Logo } from "./Logo";
import { NavigationTabs } from "./NavigationTabs";
import { useHighContrast, toggleHighContrast } from "@/hooks/useHighContrast";
import { useTheme } from "@/hooks/useTheme";
import { Contrast, Sun, Moon, LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
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
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("treq_token");
    localStorage.removeItem("treq_user_id");
    router.push("/login");
  };

  return (
    <header className="bg-treq-black text-white p-2 sm:p-2.5 md:p-3 lg:p-3.5 shadow-md z-50 relative">
      <div className="flex items-center justify-between gap-2 sm:gap-3">
        {/* Lado Esquerdo: Ícone T */}
        <div className="flex items-center min-w-0">
          <Logo variant="icon" size="md" className="text-white" />
        </div>

        {/* Centro: Nome Treq Centralizado */}
        <div className="flex-1 flex justify-center">
          <span className="text-2xl font-bold tracking-tight text-white">
            Treq
          </span>
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

          {/* Botão de Logout */}
          <button
            onClick={handleLogout}
            className="p-1.5 sm:p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors flex items-center justify-center min-w-[36px] min-h-[36px]"
            aria-label="Sair"
            title="Sair"
          >
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </header>
  );
}

