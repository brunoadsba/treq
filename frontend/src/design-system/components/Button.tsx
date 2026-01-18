"use client";

import * as React from "react";
import { treqColors } from "../tokens/colors";
import { componentTypography } from "../tokens/typography";
import { contextualSpacing } from "../tokens/spacing";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

/**
 * Componente Button base do Design System Treq
 * 
 * Características:
 * - Touch target mínimo 48px (ambiente industrial)
 * - Suporte a modo alto contraste
 * - Estados de loading
 * - Acessibilidade WCAG 2.1 AA
 */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className = "", 
    variant = "primary", 
    size = "md",
    isLoading = false,
    disabled,
    children,
    ...props 
  }, ref) => {
    const baseStyles = "inline-flex items-center justify-center rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50";
    
    const variants = {
      primary: "bg-treq-yellow text-treq-black hover:bg-treq-yellow-dark",
      secondary: "bg-treq-gray-100 text-treq-gray-700 hover:bg-treq-gray-200",
      outline: "border border-treq-gray-300 bg-transparent hover:bg-treq-gray-50 text-treq-gray-700",
      ghost: "hover:bg-treq-gray-100 text-treq-gray-700",
      danger: "bg-treq-error text-white hover:bg-treq-error-dark",
    };
    
    const sizes = {
      sm: "h-10 px-4 py-2 text-sm",
      md: "min-h-[48px] px-6 py-3 text-base", // Touch target mínimo industrial
      lg: "min-h-[56px] px-8 py-4 text-lg",
    };

    return (
      <button
        className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
        ref={ref}
        disabled={disabled || isLoading}
        aria-busy={isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Carregando...</span>
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);
Button.displayName = "Button";

export { Button };
