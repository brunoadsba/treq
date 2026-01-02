"use client";

import { useState, useRef, useEffect } from "react";
import { MoreVertical, Plus, History, Download, X } from "lucide-react";
import { useHighContrast } from "@/hooks/useHighContrast";

interface ConversationMenuProps {
  hasMessages: boolean;
  onNewConversation: () => void;
  onShowHistory: () => void;
  onExportConversation: () => void;
}

export function ConversationMenu({
  hasMessages,
  onNewConversation,
  onShowHistory,
  onExportConversation,
}: ConversationMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const isHighContrast = useHighContrast();

  // Fechar menu ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }
  }, [isOpen]);

  // Fechar menu ao pressionar Escape
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      return () => {
        document.removeEventListener("keydown", handleEscape);
      };
    }
  }, [isOpen]);

  const menuItems = [
    {
      icon: Plus,
      label: "Nova Conversa",
      onClick: () => {
        onNewConversation();
        setIsOpen(false);
      },
      show: hasMessages,
    },
    {
      icon: History,
      label: "Ver Histórico",
      onClick: () => {
        onShowHistory();
        setIsOpen(false);
      },
      show: true,
    },
    {
      icon: Download,
      label: "Exportar Conversa",
      onClick: () => {
        onExportConversation();
        setIsOpen(false);
      },
      show: hasMessages,
    },
  ].filter((item) => item.show);

  if (menuItems.length === 0) return null;

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={() => setIsOpen(!isOpen)}
        className={`p-1.5 sm:p-2 rounded-lg hover:bg-treq-gray-800 transition-colors flex-shrink-0 min-w-[36px] min-h-[36px] sm:min-w-[40px] sm:min-h-[40px] md:min-w-[44px] md:min-h-[44px] flex items-center justify-center ${
          isOpen ? 'bg-treq-gray-800' : ''
        }`}
        aria-label="Menu de conversas"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <MoreVertical className="w-4 h-4 sm:w-5 sm:h-5" />
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />
          <div
            ref={menuRef}
            className={`absolute right-0 top-full mt-2 w-56 rounded-lg shadow-lg z-20 ${
              isHighContrast
                ? 'bg-black border border-white'
                : 'bg-white border border-treq-gray-200'
            }`}
            role="menu"
            aria-orientation="vertical"
          >
            {menuItems.map((item, index) => {
              const Icon = item.icon;
              return (
                <button
                  key={index}
                  onClick={item.onClick}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left text-sm transition-colors first:rounded-t-lg last:rounded-b-lg focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-inset ${
                    isHighContrast
                      ? 'text-white hover:bg-treq-gray-800'
                      : 'text-treq-gray-700 hover:bg-treq-gray-100'
                  }`}
                  role="menuitem"
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
