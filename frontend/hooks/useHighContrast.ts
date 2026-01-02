"use client";

import { useState, useEffect } from "react";

/**
 * Hook para gerenciar modo alto contraste
 * Implementação baseada em data attributes (padrão moderno)
 * Suporta:
 * - Media query prefers-contrast: high
 * - Preferência manual via localStorage
 * - Aplicação via data-high-contrast no HTML
 */
export function useHighContrast(): boolean {
  const [isHighContrast, setIsHighContrast] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined" || typeof document === "undefined") return;

    // Função para aplicar/remover data attribute
    const applyHighContrast = (enabled: boolean) => {
      if (enabled) {
        document.documentElement.setAttribute("data-high-contrast", "true");
      } else {
        document.documentElement.removeAttribute("data-high-contrast");
      }
      setIsHighContrast(enabled);
    };

    // Verificar preferência manual primeiro
    const manualPreference = localStorage.getItem("treq-high-contrast");
    if (manualPreference === "true") {
      applyHighContrast(true);
      return;
    }

    // Verificar media query prefers-contrast
    const mediaQuery = window.matchMedia("(prefers-contrast: high)");
    applyHighContrast(mediaQuery.matches);

    // Listener para mudanças na preferência do sistema
    const handleChange = (e: MediaQueryListEvent) => {
      // Só aplicar se não houver preferência manual
      if (localStorage.getItem("treq-high-contrast") === null) {
        applyHighContrast(e.matches);
      }
    };

    // Adicionar listener
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", handleChange);
      return () => mediaQuery.removeEventListener("change", handleChange);
    } else {
      // Fallback para navegadores antigos
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  return isHighContrast;
}

/**
 * Função para alternar modo alto contraste manualmente
 * Usa data-high-contrast no HTML (melhor prática)
 */
export function toggleHighContrast(): void {
  if (typeof window === "undefined" || typeof document === "undefined") return;
  
  const current = localStorage.getItem("treq-high-contrast") === "true";
  const newValue = !current;
  
  // Salvar preferência
  localStorage.setItem("treq-high-contrast", newValue.toString());
  
  // Aplicar data attribute
  if (newValue) {
    document.documentElement.setAttribute("data-high-contrast", "true");
  } else {
    document.documentElement.removeAttribute("data-high-contrast");
  }
  
  // Disparar evento customizado para atualizar componentes
  window.dispatchEvent(new CustomEvent("highContrastChanged", {
    detail: { enabled: newValue }
  }));
}
