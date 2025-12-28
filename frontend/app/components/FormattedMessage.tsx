"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CheckCircle2, AlertTriangle, XCircle, Lightbulb, ChevronDown, ChevronUp, Brain } from "lucide-react";
import { ReactNode, useState } from "react";

interface FormattedMessageProps {
  content: string;
}

// Helper para extrair texto de elementos React
function extractText(node: ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) {
    return node.map(extractText).join("");
  }
  if (node && typeof node === "object" && "props" in node) {
    return extractText((node as any).props?.children || "");
  }
  return "";
}

// Interface para conteúdo parseado do Chain of Thought
interface ParsedCoT {
  hasCoT: boolean;
  thinking?: string;
  answer: string;
}

// Parser para Chain of Thought - extrai <pensamento> e <resposta>
function parseChainOfThought(text: string): ParsedCoT {
  // Buscar tags <pensamento>
  const thinkingMatch = text.match(/<pensamento>([\s\S]*?)<\/pensamento>/i);
  const thinking = thinkingMatch ? thinkingMatch[1].trim() : undefined;
  
  // Buscar tags <resposta>
  const answerMatch = text.match(/<resposta>([\s\S]*?)<\/resposta>/i);
  const answer = answerMatch ? answerMatch[1].trim() : text.trim();
  
  return {
    hasCoT: !!(thinking || answerMatch),
    thinking,
    answer,
  };
}

// Componente para renderizar pensamento (collapsible)
function ThinkingSection({ thinking }: { thinking: string }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div className="mb-4 border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-left hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Brain className="w-4 h-4 text-gray-500" />
          <span className="font-medium">Raciocínio do Assistente</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-4 pb-3 pt-2 border-t border-gray-200">
          <p className="text-sm text-gray-600 italic leading-relaxed whitespace-pre-wrap">
            {thinking}
          </p>
        </div>
      )}
    </div>
  );
}

export function FormattedMessage({ content }: FormattedMessageProps) {
  // Parsear Chain of Thought
  const parsed = parseChainOfThought(content);
  
  const components = {
    // Títulos (h2, h3)
    h2: ({ children, ...props }: any) => {
      const text = extractText(children);
      if (text.includes("Status:")) {
        return (
          <h2 className="text-lg font-bold mb-4 text-gray-900 flex items-center gap-2 pb-2 border-b border-gray-200">
            {children}
          </h2>
        );
      }
      return (
        <h2 className="text-base font-semibold mb-3 mt-5 text-gray-900 first:mt-0">
          {children}
        </h2>
      );
    },
    h3: ({ children, ...props }: any) => (
      <h3 className="text-sm font-semibold mb-2.5 mt-4 text-gray-900">
        {children}
      </h3>
    ),
    
    // Parágrafos
    p: ({ children, ...props }: any) => {
      const text = extractText(children);
      
      // Detectar status badges (✅ OK, ⚠️ ATENÇÃO, 🔴 CRÍTICO)
      if (text.match(/^(✅|⚠️|🔴)/)) {
        const isOK = text.includes("✅");
        const isWarning = text.includes("⚠️");
        const isCritical = text.includes("🔴");
        
        return (
          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md font-semibold text-sm mb-4 ${
            isOK 
              ? "bg-green-50 text-green-700 border border-green-300" 
              : isWarning
              ? "bg-yellow-50 text-yellow-700 border border-yellow-300"
              : isCritical
              ? "bg-red-50 text-red-700 border border-red-300"
              : "bg-gray-50 text-gray-700 border border-gray-300"
          }`}>
            {isOK && <CheckCircle2 className="w-4 h-4 text-green-600" />}
            {isWarning && <AlertTriangle className="w-4 h-4 text-yellow-600" />}
            {isCritical && <XCircle className="w-4 h-4 text-red-600" />}
            <span>{text.replace(/^(✅|⚠️|🔴)\s*/, "")}</span>
          </div>
        );
      }
      
      // Detectar "Ação:" com 💡
      if (text.match(/💡/i) || text.match(/ação:/i)) {
        const actionText = text
          .replace(/💡\s*\*\*?Ação:\*\*?\s*/i, "")
          .replace(/💡\s*[Aa]ção:\s*/i, "")
          .trim();
        
        return (
          <div className="bg-yellow-50 border-l-4 border-sotreq-yellow pl-4 pr-4 py-3 rounded-r-md mt-4 shadow-sm">
            <div className="flex items-start gap-2">
              <Lightbulb className="w-5 h-5 text-sotreq-yellow-dark flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-semibold text-gray-900 mb-1.5">Ação:</div>
                <div className="text-sm text-gray-700 leading-relaxed">
                  {actionText || children}
                </div>
              </div>
            </div>
          </div>
        );
      }
      
      return (
        <p className="text-sm text-gray-800 leading-relaxed mb-2.5 last:mb-0">
          {children}
        </p>
      );
    },
    
    // Listas
    ul: ({ children, ...props }: any) => (
      <ul className="list-none space-y-2.5 my-3">
        {children}
      </ul>
    ),
    ol: ({ children, ...props }: any) => (
      <ol className="list-decimal list-inside space-y-2 my-3 ml-2">
        {children}
      </ol>
    ),
    li: ({ children, ...props }: any) => {
      const text = extractText(children);
      const hasBullet = text.startsWith("•") || text.match(/^\*\*/);
      
      if (hasBullet) {
        const cleanedText = text.replace(/^•\s*/, "").trim();
        return (
          <li className="flex items-start gap-3 text-sm text-gray-800 leading-relaxed">
            <span className="text-sotreq-yellow-dark mt-1.5 flex-shrink-0 font-bold">•</span>
            <span className="flex-1">{cleanedText || children}</span>
          </li>
        );
      }
      return (
        <li className="text-sm text-gray-800 leading-relaxed pl-2">
          {children}
        </li>
      );
    },
    
    // Negrito
    strong: ({ children, ...props }: any) => (
      <strong className="font-semibold text-gray-900">
        {children}
      </strong>
    ),
    
    // Código inline
    code: ({ children, ...props }: any) => (
      <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono text-gray-800">
        {children}
      </code>
    ),
    
    // Blocos de código
    pre: ({ children, ...props }: any) => (
      <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto my-3">
        {children}
      </pre>
    ),
    
    // Divisores horizontais
    hr: ({ ...props }: any) => (
      <hr className="my-5 border-gray-200" />
    ),
  };

  return (
    <div className="prose prose-sm max-w-none prose-headings:mt-0 prose-headings:mb-0 prose-p:my-0">
      {/* Renderizar pensamento se existir */}
      {parsed.hasCoT && parsed.thinking && (
        <ThinkingSection thinking={parsed.thinking} />
      )}
      
      {/* Renderizar resposta */}
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={components}
      >
        {parsed.answer}
      </ReactMarkdown>
    </div>
  );
}
