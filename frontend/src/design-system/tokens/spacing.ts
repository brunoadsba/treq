/**
 * Tokens de Espaçamento - Treq Design System
 * Manual de Identidade Visual v1.0
 * 
 * Sistema de espaçamento baseado em múltiplos de 4px.
 * Garante consistência visual em toda a aplicação.
 */

/**
 * Espaçamentos base (múltiplos de 4px)
 */
export const treqSpacing = {
  1: "4px",    // 0.25rem
  2: "8px",    // 0.5rem
  3: "12px",   // 0.75rem
  4: "16px",   // 1rem - Base
  5: "20px",   // 1.25rem
  6: "24px",   // 1.5rem
  8: "32px",   // 2rem
  10: "40px",  // 2.5rem
  12: "48px",  // 3rem - Touch target mínimo industrial
  16: "64px",  // 4rem
} as const;

/**
 * Espaçamentos em rem (para uso em Tailwind)
 */
export const treqSpacingRem = {
  1: "0.25rem",
  2: "0.5rem",
  3: "0.75rem",
  4: "1rem",
  5: "1.25rem",
  6: "1.5rem",
  8: "2rem",
  10: "2.5rem",
  12: "3rem",
  16: "4rem",
} as const;

/**
 * Espaçamentos por Contexto
 */
export const contextualSpacing = {
  // Componentes
  component: {
    padding: treqSpacing[4],      // 16px
    gap: treqSpacing[2],          // 8px
    margin: treqSpacing[6],       // 24px
  },
  
  // Chat
  chat: {
    messageGap: treqSpacing[6],   // 24px entre mensagens
    messagePadding: treqSpacing[4], // 16px padding interno
    containerPadding: treqSpacing[4], // 16px padding do container
  },
  
  // Input Area
  input: {
    containerPadding: treqSpacing[4], // 16px
    buttonGap: treqSpacing[2],       // 8px entre botões
    buttonPadding: treqSpacing[3],   // 12px padding dos botões
    minHeight: treqSpacing[12],      // 48px touch target mínimo
  },
  
  // Header
  header: {
    padding: treqSpacing[4],         // 16px
    height: treqSpacing[16],         // 64px (desktop)
    heightMobile: "56px",           // 56px (mobile)
    gap: treqSpacing[4],             // 16px entre elementos
  },
  
  // Toast
  toast: {
    padding: treqSpacing[3],         // 12px
    gap: treqSpacing[2],             // 8px entre toasts
    margin: treqSpacing[4],          // 16px da borda
  },
} as const;

/**
 * Breakpoints Responsivos
 */
export const breakpoints = {
  sm: "640px",   // Mobile grande
  md: "768px",   // Tablet
  lg: "1024px",  // Desktop
  xl: "1280px",  // Desktop grande
  "2xl": "1536px", // Desktop extra grande
} as const;

/**
 * Grid System
 */
export const grid = {
  container: {
    maxWidth: "1200px",
    padding: {
      mobile: treqSpacing[4],   // 16px
      desktop: treqSpacing[6],  // 24px
    },
  },
  message: {
    maxWidth: "85%", // Máximo 85% da largura disponível
  },
} as const;
