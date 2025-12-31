"use client";

import * as React from "react";
import { useHighContrast } from "../../app/hooks/useHighContrast";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

/**
 * Componente Input base do Design System Treq
 * 
 * Características:
 * - Touch target mínimo 48px (ambiente industrial)
 * - Suporte a modo alto contraste
 * - Validação e feedback de erro
 * - Acessibilidade WCAG 2.1 AA
 */
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className = "",
    label,
    error,
    helperText,
    id,
    ...props 
  }, ref) => {
    const isHighContrast = useHighContrast();
    const inputId = id || `input-${Math.random().toString(36).substring(7)}`;
    const errorId = error ? `${inputId}-error` : undefined;
    const helperId = helperText ? `${inputId}-helper` : undefined;
    const describedBy = [errorId, helperId].filter(Boolean).join(" ") || undefined;

    return (
      <div className="w-full">
        {label && (
          <label 
            htmlFor={inputId}
            className="block text-sm font-medium text-treq-gray-700 mb-2"
          >
            {label}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          className={`
            w-full min-h-[48px] px-5 py-3 rounded-xl
            border transition-all
            focus:outline-none focus:ring-2 focus:ring-offset-2
            disabled:opacity-50 disabled:cursor-not-allowed
            ${error 
              ? "border-treq-error focus:ring-treq-error" 
              : "border-treq-gray-300 focus:ring-treq-yellow focus:border-transparent"
            }
            ${isHighContrast
              ? "bg-black text-white border-white placeholder:text-treq-gray-400"
              : "bg-white text-treq-gray-900 placeholder:text-treq-gray-400"
            }
            ${className}
          `}
          style={{
            fontSize: isHighContrast ? "1.125rem" : "1rem"
          }}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={describedBy}
          {...props}
        />
        {error && (
          <p 
            id={errorId}
            className="mt-2 text-sm text-treq-error"
            role="alert"
          >
            {error}
          </p>
        )}
        {helperText && !error && (
          <p 
            id={helperId}
            className="mt-2 text-sm text-treq-gray-500"
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);
Input.displayName = "Input";

export { Input };
