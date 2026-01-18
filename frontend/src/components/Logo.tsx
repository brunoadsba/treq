"use client";

import React, { useEffect, useState } from "react";

interface LogoProps {
  variant?: "horizontal" | "vertical" | "icon";
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeMap = {
  sm: { icon: 24, text: "text-lg" },
  md: { icon: 32, text: "text-2xl" }, // Aumentado de text-xl para text-2xl
  lg: { icon: 40, text: "text-3xl" },
};

export function Logo({ 
  variant = "horizontal", 
  size = "md",
  className = "" 
}: LogoProps) {
  const { icon: iconSize, text: textSize } = sizeMap[size];
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Detectar tema escuro
  useEffect(() => {
    if (typeof window === "undefined") return;
    
    const checkTheme = () => {
      const theme = document.documentElement.getAttribute("data-theme");
      setIsDarkMode(theme === "dark");
    };

    checkTheme();
    
    // Listener para mudanças de tema
    window.addEventListener("themeChanged", checkTheme);
    window.addEventListener("toggleTheme", checkTheme);
    
    // Observer para mudanças no data-theme
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });

    return () => {
      window.removeEventListener("themeChanged", checkTheme);
      window.removeEventListener("toggleTheme", checkTheme);
      observer.disconnect();
    };
  }, []);

  // Símbolo T estilizado com elemento geométrico industrial
  const Symbol = () => (
    <svg 
      width={iconSize} 
      height={iconSize} 
      viewBox="0 0 40 40" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className="flex-shrink-0"
      aria-hidden="true"
    >
      {/* Fundo amarelo com bordas arredondadas */}
      <rect width="40" height="40" rx="4" fill="currentColor" className="text-treq-yellow" />
      
      {/* Letra T principal - preto puro para máximo contraste no amarelo */}
      <path 
        d="M10 12H30V16H22V30H18V16H10V12Z" 
        fill="#000000"
        style={{ 
          opacity: 1,
          filter: "none"
        }}
      />
      
      {/* Elemento geométrico sutil (engrenagem parcial) - removido para visual mais limpo */}
    </svg>
  );

  if (variant === "icon") {
    return (
      <div className={`flex items-center ${className}`}>
        <Symbol />
      </div>
    );
  }

  if (variant === "vertical") {
    return (
      <div className={`flex flex-col items-center gap-2 ${className}`}>
        <Symbol />
        <span className={`${textSize} font-bold tracking-tight text-current`}>
          Treq
        </span>
      </div>
    );
  }

  // Horizontal (padrão)
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Symbol />
      <span className={`${textSize} font-bold tracking-tight text-current`}>
        Treq
      </span>
    </div>
  );
}
