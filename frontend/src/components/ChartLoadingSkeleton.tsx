"use client";

import { useTheme } from "@/hooks/useTheme";

export function ChartLoadingSkeleton() {
  const [theme] = useTheme();
  
  return (
    <div className={`rounded-lg border p-4 sm:p-6 mb-4 sm:mb-6 ${
      theme === "dark"
        ? "bg-treq-gray-800 border-treq-gray-700"
        : "bg-white border-treq-gray-200"
    } shadow-sm animate-pulse`}>
      <div className="mb-4">
        <div className={`h-6 w-3/4 rounded mb-2 ${
          theme === "dark" ? "bg-treq-gray-700" : "bg-treq-gray-200"
        }`}></div>
        <div className={`h-4 w-1/2 rounded ${
          theme === "dark" ? "bg-treq-gray-700" : "bg-treq-gray-200"
        }`}></div>
      </div>
      
      <div className={`w-full h-96 rounded ${
        theme === "dark" ? "bg-treq-gray-700" : "bg-treq-gray-100"
      }`}>
        <div className={`flex items-center justify-center h-full ${
          theme === "dark" ? "text-treq-gray-400" : "text-treq-gray-400"
        }`}>
          Carregando gráfico...
        </div>
      </div>
      
      <div className={`mt-4 pt-4 border-t ${
        theme === "dark" ? "border-treq-gray-700" : "border-treq-gray-200"
      }`}>
        <div className={`h-4 w-1/3 rounded ${
          theme === "dark" ? "bg-treq-gray-700" : "bg-treq-gray-200"
        }`}></div>
      </div>
    </div>
  );
}
