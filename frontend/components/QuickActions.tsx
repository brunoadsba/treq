"use client";

import { AlertTriangle, FileText, BarChart3, BrainCircuit } from "lucide-react";
import { Tooltip } from "./Tooltip";

interface QuickAction {
  id: string;
  label: string;
  shortLabel: string; // Texto abreviado para mobile
  icon: React.ReactNode;
  query: string;
  supportsVisualization?: boolean;
}

const quickActions: QuickAction[] = [
  {
    id: "alertas",
    label: "Alertas Ativos",
    shortLabel: "Alertas",
    icon: <AlertTriangle className="w-4 h-4 sm:w-5 sm:h-5" />,
    query: "Quais alertas críticos estão ativos?",
    supportsVisualization: true,
  },
  {
    id: "status-recife",
    label: "Status Recife",
    shortLabel: "Recife",
    icon: <BarChart3 className="w-4 h-4 sm:w-5 sm:h-5" />,
    query: "Qual o status operacional de Recife?",
    supportsVisualization: true,
  },
  {
    id: "status-salvador",
    label: "Status Salvador",
    shortLabel: "Salvador",
    icon: <BarChart3 className="w-4 h-4 sm:w-5 sm:h-5" />,
    query: "Qual o status operacional de Salvador?",
    supportsVisualization: true,
  },
  {
    id: "procedimentos",
    label: "Procedimentos",
    shortLabel: "Proced.",
    icon: <FileText className="w-4 h-4 sm:w-5 sm:h-5" />,
    query: "Quais são os procedimentos operacionais?",
    supportsVisualization: false,
  },
  {
    id: "consultoria",
    label: "Consultoria",
    shortLabel: "Consult.",
    icon: <BrainCircuit className="w-4 h-4 sm:w-5 sm:h-5" />,
    query: "consultoria:",
    supportsVisualization: false,
  },
];

interface QuickActionsProps {
  onActionClick: (query: string, actionId?: string) => void;
  disabled?: boolean;
}

export function QuickActions({ onActionClick, disabled = false }: QuickActionsProps) {
  const handleKeyDown = (e: React.KeyboardEvent, query: string, actionId?: string) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      if (!disabled) {
        onActionClick(query, actionId);
      }
    }
  };

  return (
    <div className="px-2 sm:px-3 md:px-4 lg:px-6 py-1.5 sm:py-2 md:py-2.5 border-b border-treq-gray-200 bg-white" role="toolbar" aria-label="Ações rápidas">
      <div className="flex gap-2 overflow-x-auto pb-1.5 scrollbar-hide -mx-2 px-4 justify-start sm:justify-center">
        {quickActions.map((action) => (
          <Tooltip key={action.id} content={action.label} position="bottom" delay={200}>
            <button
              onClick={() => !disabled && onActionClick(action.query, action.id)}
              onKeyDown={(e) => handleKeyDown(e, action.query, action.id)}
              disabled={disabled}
              className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 bg-treq-gray-100 hover:bg-treq-gray-200 text-treq-gray-700 rounded-lg font-medium text-xs sm:text-sm whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed transition-all focus:outline-none focus:ring-2 focus:ring-treq-yellow min-h-[40px] flex-shrink-0"
              aria-label={`Ação rápida: ${action.label}`}
              aria-disabled={disabled}
              title={action.label}
            >
              <span aria-hidden="true" className="flex-shrink-0 text-treq-gray-500">{action.icon}</span>
              <span className="md:hidden">{action.shortLabel}</span>
              <span className="hidden md:inline">{action.label}</span>
            </button>
          </Tooltip>
        ))}
      </div>
    </div>
  );
}

