"use client";

import { useEffect } from "react";
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react";

export type ToastType = "success" | "error" | "warning" | "info";

interface ToastProps {
  message: string;
  type?: ToastType;
  duration?: number;
  onClose: () => void;
}

// Duração padrão por tipo (em milissegundos)
const DEFAULT_DURATIONS: Record<ToastType, number> = {
  success: 5000,
  error: 7000,
  warning: 6000,
  info: 5000,
};

export function Toast({ message, type = "info", duration, onClose }: ToastProps) {
  // Usar duração padrão se não especificada
  const toastDuration = duration ?? DEFAULT_DURATIONS[type];

  useEffect(() => {
    if (toastDuration > 0) {
      const timer = setTimeout(onClose, toastDuration);
      return () => clearTimeout(timer);
    }
  }, [toastDuration, onClose]);

  const iconConfig = {
    success: { icon: CheckCircle, color: "text-treq-success" },
    error: { icon: AlertCircle, color: "text-treq-error" },
    warning: { icon: AlertTriangle, color: "text-treq-warning" },
    info: { icon: Info, color: "text-treq-info" },
  };

  const styleConfig = {
    success: "bg-treq-success-light border-treq-success text-treq-success-dark",
    error: "bg-treq-error-light border-treq-error text-treq-error-dark",
    warning: "bg-treq-warning-light border-treq-warning text-treq-warning-dark",
    info: "bg-treq-info-light border-treq-info text-treq-info-dark",
  };

  const { icon: IconComponent, color: iconColor } = iconConfig[type];

  return (
    <div
      className={`px-3 sm:px-4 py-2 sm:py-3 rounded-lg border shadow-lg flex items-center gap-2 sm:gap-3 min-w-[260px] sm:min-w-[280px] md:min-w-[300px] max-w-[calc(100vw-2rem)] sm:max-w-md animate-slide-in-right ${styleConfig[type]}`}
      role="alert"
      aria-live={type === "error" ? "assertive" : "polite"}
    >
      <IconComponent className={`w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0 ${iconColor}`} aria-hidden="true" />
      <p className="flex-1 text-sm font-medium break-words">{message}</p>
      <button
        onClick={onClose}
        className="text-treq-gray-400 hover:text-treq-gray-600 transition-colors p-1 rounded focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 flex-shrink-0 min-w-[28px] min-h-[28px] sm:min-w-[32px] sm:min-h-[32px] flex items-center justify-center"
        aria-label="Fechar notificação"
      >
        <X className="w-3 h-3 sm:w-4 sm:h-4" />
      </button>
    </div>
  );
}

