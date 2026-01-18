"use client";

import { useState, useEffect } from "react";

export type Theme = "light" | "dark";

/**
 * Hook para gerenciar tema claro/escuro
 * Implementação baseada em data attributes (padrão moderno)
 * Suporta:
 * - Preferência manual via localStorage
 * - Media query prefers-color-scheme
 * - Aplicação via data-theme no HTML
 */
export function useTheme(): [Theme, (theme: Theme) => void] {
  const [theme, setThemeState] = useState<Theme>("light");

  useEffect(() => {
    if (typeof window === "undefined" || typeof document === "undefined") return;

    // Função para aplicar/remover data attribute
    const applyTheme = (newTheme: Theme) => {
      document.documentElement.setAttribute("data-theme", newTheme);
      setThemeState(newTheme);
    };

    // Verificar preferência manual primeiro
    const manualPreference = localStorage.getItem("treq-theme") as Theme | null;
    if (manualPreference === "light" || manualPreference === "dark") {
      applyTheme(manualPreference);
    } else {
      // Verificar media query prefers-color-scheme se não houver preferência manual
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      applyTheme(mediaQuery.matches ? "dark" : "light");
    }

    // Listener para mudanças na preferência do sistema
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e: MediaQueryListEvent) => {
      // Só aplicar se não houver preferência manual
      if (localStorage.getItem("treq-theme") === null) {
        applyTheme(e.matches ? "dark" : "light");
      }
    };

    // Listener para eventos customizados de toggle
    const handleToggleTheme = (e: Event) => {
      const customEvent = e as CustomEvent<{ theme: Theme }>;
      if (customEvent.detail?.theme) {
        applyTheme(customEvent.detail.theme);
      }
    };

    // Adicionar listeners
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", handleChange);
    } else {
      // Fallback para navegadores antigos
      mediaQuery.addListener(handleChange);
    }
    
    window.addEventListener("toggleTheme", handleToggleTheme);
    window.addEventListener("themeChanged", handleToggleTheme);

    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener("change", handleChange);
      } else {
        mediaQuery.removeListener(handleChange);
      }
      window.removeEventListener("toggleTheme", handleToggleTheme);
      window.removeEventListener("themeChanged", handleToggleTheme);
    };
  }, []);

  const setTheme = (newTheme: Theme) => {
    if (typeof window === "undefined" || typeof document === "undefined") return;
    
    // Salvar preferência
    localStorage.setItem("treq-theme", newTheme);
    
    // Aplicar data attribute
    document.documentElement.setAttribute("data-theme", newTheme);
    setThemeState(newTheme);
    
    // Disparar evento customizado para atualizar componentes
    window.dispatchEvent(new CustomEvent("themeChanged", {
      detail: { theme: newTheme }
    }));
  };

  return [theme, setTheme];
}

/**
 * Função para alternar entre temas
 */
export function toggleTheme(): Theme {
  if (typeof window === "undefined") return "light";
  
  const current = localStorage.getItem("treq-theme") as Theme | null;
  const newTheme: Theme = current === "dark" ? "light" : "dark";
  
  // Usar o hook setTheme via evento
  window.dispatchEvent(new CustomEvent("toggleTheme", {
    detail: { theme: newTheme }
  }));
  
  return newTheme;
}
