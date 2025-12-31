import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cores Treq (Manual de Identidade Visual v1.0)
        "treq-yellow": {
          DEFAULT: "#FFCD00",
          dark: "#E6B800",
          light: "#FFE066",
        },
        "treq-black": "#000000",
        "treq-gray": {
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
        "treq-success": {
          DEFAULT: "#10B981",
          dark: "#059669",
          light: "#D1FAE5",
        },
        "treq-error": {
          DEFAULT: "#EF4444",
          dark: "#DC2626",
          light: "#FEE2E2",
        },
        "treq-warning": {
          DEFAULT: "#F59E0B",
          dark: "#D97706",
          light: "#FEF3C7",
        },
        "treq-info": {
          DEFAULT: "#3B82F6",
          dark: "#2563EB",
          light: "#DBEAFE",
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['"Courier New"', 'Courier', 'monospace'],
      },
    },
  },
  plugins: [],
};
export default config;

