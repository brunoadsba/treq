/**
 * Tokens de Cores - Treq Design System
 * Manual de Identidade Visual v1.0
 * 
 * Cores centralizadas para uso em todo o sistema.
 * Importar e usar em componentes para garantir consistência.
 */

export const treqColors = {
  // Cores Principais
  yellow: {
    DEFAULT: "#FFCD00",
    dark: "#E6B800",
    light: "#FFE066",
  },
  black: "#000000",
  
  // Escala de Cinzas
  gray: {
    50: "#F9FAFB",
    100: "#F3F4F6",
    200: "#E5E7EB",
    300: "#D1D5DB",
    400: "#9CA3AF",
    500: "#6B7280",
    600: "#4B5563",
    700: "#374151",
    800: "#1F2937",
    900: "#111827",
  },
  
  // Cores Funcionais
  success: {
    DEFAULT: "#10B981",
    dark: "#059669",
    light: "#D1FAE5",
  },
  error: {
    DEFAULT: "#EF4444",
    dark: "#DC2626",
    light: "#FEE2E2",
  },
  warning: {
    DEFAULT: "#F59E0B",
    dark: "#D97706",
    light: "#FEF3C7",
  },
  info: {
    DEFAULT: "#3B82F6",
    dark: "#2563EB",
    light: "#DBEAFE",
  },
  
  // Cores de Áudio e Mídia
  recording: {
    DEFAULT: "#EF4444",
    hover: "#DC2626",
  },
  audioProcessing: "#3B82F6",
  
  // Modo Alto Contraste
  highContrast: {
    bg: "#000000",
    text: "#FFFFFF",
    accent: "#FFCD00",
    border: "#FFFFFF",
  },
} as const;

/**
 * Helper para obter cor com fallback
 */
export function getColor(path: string): string {
  const keys = path.split(".");
  let value: any = treqColors;
  
  for (const key of keys) {
    value = value?.[key];
    if (value === undefined) {
      console.warn(`Color path "${path}" not found`);
      return "#000000"; // Fallback preto
    }
  }
  
  return typeof value === "string" ? value : value.DEFAULT || value;
}

/**
 * Exportar como objeto plano para uso em CSS/JSON
 */
export const treqColorsFlat = {
  "treq-yellow": treqColors.yellow.DEFAULT,
  "treq-yellow-dark": treqColors.yellow.dark,
  "treq-yellow-light": treqColors.yellow.light,
  "treq-black": treqColors.black,
  "treq-success": treqColors.success.DEFAULT,
  "treq-success-dark": treqColors.success.dark,
  "treq-success-light": treqColors.success.light,
  "treq-error": treqColors.error.DEFAULT,
  "treq-error-dark": treqColors.error.dark,
  "treq-error-light": treqColors.error.light,
  "treq-warning": treqColors.warning.DEFAULT,
  "treq-warning-dark": treqColors.warning.dark,
  "treq-warning-light": treqColors.warning.light,
  "treq-info": treqColors.info.DEFAULT,
  "treq-info-dark": treqColors.info.dark,
  "treq-info-light": treqColors.info.light,
} as const;
