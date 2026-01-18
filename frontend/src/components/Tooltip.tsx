"use client";

import { ReactNode, useState, useRef, useEffect } from "react";

interface TooltipProps {
  content: string;
  children: ReactNode;
  position?: "top" | "bottom" | "left" | "right";
  delay?: number;
}

export function Tooltip({ 
  content, 
  children, 
  position = "top",
  delay = 300 
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  // Detectar mobile/touch
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768 || 'ontouchstart' in window);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const showTooltip = () => {
    // Limpar timeouts anteriores
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
    
    // Em mobile, mostrar após delay (long press)
    // Em desktop, mostrar após delay normal
    const tooltipDelay = isMobile ? 500 : delay; // 500ms para long press em mobile
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, tooltipDelay);
  };

  const hideTooltip = () => {
    // Limpar timeout de mostrar
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    
    // Se já estava visível, esconder com delay em mobile para leitura
    if (isVisible) {
      if (hideTimeoutRef.current) {
        clearTimeout(hideTimeoutRef.current);
      }
      hideTimeoutRef.current = setTimeout(() => {
        setIsVisible(false);
      }, isMobile ? 2000 : 0); // 2 segundos em mobile para leitura
    }
  };

  // Posicionamento do tooltip
  const positionClasses = {
    top: "bottom-full left-1/2 transform -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 transform -translate-x-1/2 mt-2",
    left: "right-full top-1/2 transform -translate-y-1/2 mr-2",
    right: "left-full top-1/2 transform -translate-y-1/2 ml-2",
  };

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (hideTimeoutRef.current) {
        clearTimeout(hideTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onTouchStart={showTooltip}
      onTouchEnd={hideTooltip}
      onTouchCancel={hideTooltip}
      onFocus={showTooltip}
      onBlur={hideTooltip}
    >
      {children}
      {isVisible && (
        <div
          ref={tooltipRef}
          className={`absolute z-50 px-2.5 py-1.5 bg-treq-black text-white text-xs font-medium rounded-md shadow-lg whitespace-nowrap pointer-events-none animate-fade-in ${positionClasses[position]}`}
          role="tooltip"
          aria-live="polite"
        >
          {content}
          {/* Seta do tooltip */}
          <div className={`absolute w-0 h-0 ${
            position === "top" ? "top-full left-1/2 transform -translate-x-1/2 border-t-4 border-t-treq-black border-x-4 border-x-transparent" :
            position === "bottom" ? "bottom-full left-1/2 transform -translate-x-1/2 border-b-4 border-b-treq-black border-x-4 border-x-transparent" :
            position === "left" ? "left-full top-1/2 transform -translate-y-1/2 border-l-4 border-l-treq-black border-y-4 border-y-transparent" :
            "right-full top-1/2 transform -translate-y-1/2 border-r-4 border-r-treq-black border-y-4 border-y-transparent"
          }`} />
        </div>
      )}
    </div>
  );
}
