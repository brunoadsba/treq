"use client";

import { Mic, AlertTriangle, FileText, BarChart3 } from "lucide-react";

interface QuickAction {
  id: string;
  label: string;
  icon: React.ReactNode;
  query: string;
}

const quickActions: QuickAction[] = [
  {
    id: "alertas",
    label: "Alertas Ativos",
    icon: <AlertTriangle className="w-5 h-5" />,
    query: "Quais alertas críticos estão ativos?",
  },
  {
    id: "status-recife",
    label: "Status Recife",
    icon: <BarChart3 className="w-5 h-5" />,
    query: "Qual o status operacional de Recife?",
  },
  {
    id: "status-salvador",
    label: "Status Salvador",
    icon: <BarChart3 className="w-5 h-5" />,
    query: "Qual o status operacional de Salvador?",
  },
  {
    id: "procedimentos",
    label: "Procedimentos",
    icon: <FileText className="w-5 h-5" />,
    query: "Quais são os procedimentos operacionais?",
  },
];

interface QuickActionsProps {
  onActionClick: (query: string) => void;
  disabled?: boolean;
}

export function QuickActions({ onActionClick, disabled = false }: QuickActionsProps) {
  return (
    <div className="px-4 py-3 border-b border-gray-200 bg-white">
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
        {quickActions.map((action) => (
          <button
            key={action.id}
            onClick={() => !disabled && onActionClick(action.query)}
            disabled={disabled}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium text-sm whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {action.icon}
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
}

