/**
 * Tokens de Tipografia - Treq Design System
 * Manual de Identidade Visual v1.0
 * 
 * Escala tipográfica e configurações de fonte centralizadas.
 */

export const treqTypography = {
  // Família de Fontes
  fontFamily: {
    sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
    mono: ['"Courier New"', 'Courier', 'monospace'],
  },
  
  // Escala Tipográfica (em rem)
  fontSize: {
    h1: "2rem",      // 32px
    h2: "1.5rem",    // 24px
    h3: "1.25rem",   // 20px
    base: "1rem",    // 16px
    lg: "1.125rem",  // 18px
    sm: "0.875rem",  // 14px
    xs: "0.75rem",   // 12px
  },
  
  // Pesos de Fonte
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  
  // Line Heights
  lineHeight: {
    tight: 1.25,     // Títulos
    normal: 1.5,     // Corpo padrão
    relaxed: 1.75,  // Texto longo, mensagens
  },
  
  // Letter Spacing
  letterSpacing: {
    tight: "-0.025em",
    normal: "0",
    wide: "0.025em",
  },
} as const;

/**
 * Configurações por Componente
 */
export const componentTypography = {
  header: {
    title: {
      fontSize: treqTypography.fontSize.h2,
      fontWeight: treqTypography.fontWeight.semibold,
      lineHeight: treqTypography.lineHeight.tight,
    },
  },
  chat: {
    userMessage: {
      fontSize: treqTypography.fontSize.sm,
      fontWeight: treqTypography.fontWeight.normal,
      lineHeight: treqTypography.lineHeight.relaxed,
    },
    assistantMessage: {
      fontSize: treqTypography.fontSize.base,
      fontWeight: treqTypography.fontWeight.normal,
      lineHeight: treqTypography.lineHeight.relaxed,
    },
    timestamp: {
      fontSize: treqTypography.fontSize.xs,
      fontWeight: treqTypography.fontWeight.normal,
      opacity: 0.75,
    },
  },
  input: {
    placeholder: {
      fontSize: treqTypography.fontSize.base,
      fontWeight: treqTypography.fontWeight.normal,
    },
    text: {
      fontSize: treqTypography.fontSize.base,
      fontWeight: treqTypography.fontWeight.normal,
    },
    highContrast: {
      fontSize: treqTypography.fontSize.lg,
      fontWeight: treqTypography.fontWeight.normal,
    },
  },
  button: {
    primary: {
      fontSize: treqTypography.fontSize.base,
      fontWeight: treqTypography.fontWeight.medium,
    },
    secondary: {
      fontSize: treqTypography.fontSize.base,
      fontWeight: treqTypography.fontWeight.medium,
    },
    quickAction: {
      fontSize: treqTypography.fontSize.sm,
      fontWeight: treqTypography.fontWeight.medium,
    },
  },
} as const;
