"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CheckCircle2, AlertTriangle, XCircle, Lightbulb, BarChart2 } from "lucide-react";
import { ReactNode } from "react";
import { useHighContrast } from "../hooks/useHighContrast";

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
// NOTA: O bloco <pensamento> é usado apenas para debug interno
// NUNCA deve ser exibido em produção conforme requisitos de UX
function parseChainOfThought(text: string): ParsedCoT {
  // SEMPRE remove tag <pensamento> completamente do texto (nunca exibir ao usuário)
  let content = text.replace(/<pensamento>[\s\S]*?<\/pensamento>/gi, '').trim();
  
  // Extrair conteúdo de dentro das tags <resposta> (pode haver múltiplas)
  // Se houver tags <resposta>, extrair todo o conteúdo de todas elas e juntar
  const respostaMatches = content.match(/<resposta>([\s\S]*?)<\/resposta>/gi);
  let answer: string;
  
  if (respostaMatches && respostaMatches.length > 0) {
    // Extrair conteúdo de todas as tags <resposta> e juntar
    answer = respostaMatches
      .map(match => {
        const innerMatch = match.match(/<resposta>([\s\S]*?)<\/resposta>/i);
        return innerMatch ? innerMatch[1].trim() : '';
      })
      .filter(text => text.length > 0)
      .join('\n\n')
      .trim();
    
    // Se não conseguiu extrair conteúdo válido, usar texto completo sem as tags
    if (!answer || answer.length === 0) {
      answer = content.replace(/<resposta>[\s\S]*?<\/resposta>/gi, '').trim();
    }
  } else {
    // Não há tags <resposta>, usar texto completo
    answer = content.trim();
  }
  
  // REMOVER TODAS as tags <resposta> e </resposta> que possam ter sobrado (segurança extra)
  answer = answer
    .replace(/<resposta>/gi, '')
    .replace(/<\/resposta>/gi, '')
    .replace(/<pensamento>[\s\S]*?<\/pensamento>/gi, '') // Remover pensamento novamente (segurança extra)
    .trim();
  
  // Remover avisos duplicados do markdown (o frontend já renderiza esses cards)
  answer = answer
    .replace(/⏱️\s*\*\*Processamento:\*\*[^\n]*\n?/gi, '')
    .replace(/⚠️\s*\*\*Aviso:\*\*[^\n]*\n?/gi, '')
    .replace(/Esta análise requer processamento[^\n]*precisão\.?\s*/gi, '')
    .replace(/A inteligência artificial pode cometer erros[^\n]*críticas\.?\s*/gi, '')
    .replace(/^\s*\n\s*\n/gm, '\n')  // Remover linhas vazias extras
    .trim();
  
  return {
    hasCoT: false,  // Sempre false - nunca exibir pensamento ao usuário
    thinking: undefined,  // Sempre undefined - nunca expor pensamento
    answer,
  };
}

// Componente para renderizar pensamento (collapsible)
// REMOVIDO: Este componente nunca deve ser renderizado em produção
// Informações de debug não devem ser expostas ao usuário final
// Se necessário para debug interno, usar console.log ou ferramentas de desenvolvimento do navegador

// Função para filtrar termos técnicos no frontend (última camada de proteção)
function sanitizeTechnicalTerms(text: string): string {
  if (!text || typeof text !== 'string') return text;
  
  let result = text;
  
  // Padrões regex para substituir termos técnicos (mesmos do backend)
  // Ordem: mais específicos primeiro
  const patterns = [
    // SLA com preposição antes e adjetivo
    [/\b(com|do|da|no|na|em|para|por)\s+SLA\b\s+([a-záàâãéêíóôõúç]+)/gi, '$1 prazo $2'],
    // SLA com preposição antes
    [/\b(com|do|da|no|na|em|para|por)\s+SLA\b/gi, '$1 prazo'],
    // SLA com preposição depois e número
    [/\bSLA\b\s+(de|da|do)\s+(\d+\s*\w+)/gi, 'prazo $1 $2'],
    // SLA com número sem preposição
    [/\bSLA\b\s+(\d+\s*\w+)/gi, 'prazo de $1'],
    // SLA com adjetivo
    [/\bSLA\b\s+([a-záàâãéêíóôõúç]+(?:\s+[a-záàâãéêíóôõúç]+)?)/gi, 'prazo $1'],
    // SLazo e variações (erros de digitação)
    [/\bSLazo\b\s+(de|da|do)\s+(\d+\w*)/gi, 'prazo $1 $2'],
    [/\bSLazo\b\s+([a-záàâãéêíóôõúç]+)/gi, 'prazo $1'],
    [/\bSLazo\b/gi, 'prazo'],
    [/\bSLazos\b/gi, 'prazos'],
    // SLA com dois pontos
    [/\bSLA\b\s*:\s*/gi, 'prazo: '],
    // SLA's (plural com apóstrofe)
    [/\bSLA's\b/gi, 'prazos'],
    // SLAs (plural)
    [/\bSLAs\b/gi, 'prazos'],
    // SLA sozinho (último padrão - mais genérico)
    [/\bSLA'?s?\b/gi, 'prazo'],
    // Threshold
    [/\bthreshold\b/gi, 'limite'],
    // KPI
    [/\bKPI\b|\bKPIs\b/gi, 'indicador de performance'],
    // Sigma e desvio padrão
    [/\bsigma\b|\bdesvio padrão\b/gi, 'desvio acima do normal'],
  ];
  
  // Aplicar todas as substituições
  for (const [pattern, replacement] of patterns) {
    result = result.replace(pattern, replacement as string);
  }
  
  return result;
}

export function FormattedMessage({ content }: FormattedMessageProps) {
  // Filtrar termos técnicos no frontend (última camada de proteção)
  const cleanContent = sanitizeTechnicalTerms(content);
  
  // Parsear Chain of Thought
  const parsed = parseChainOfThought(cleanContent);
  const isHighContrast = useHighContrast();
  
  // Detectar se é resposta de status operacional estruturada (detecção mais robusta)
  const isOperationStatus = (
    (parsed.answer.includes("Status:") || 
     parsed.answer.includes("**Status:") ||
     parsed.answer.match(/Status:\s*\w+/i)) &&
    !parsed.answer.toLowerCase().includes("consultoria:")
  );
  
  // Detectar avisos de Consultoria
  const hasConsultoriaProcessing = content.includes("⏱️ **Processamento:**") || 
                                   content.includes("Esta análise requer processamento");
  const hasConsultoriaDisclaimer = content.includes("⚠️ **Aviso:**") || 
                                   content.includes("A inteligência artificial pode cometer erros");
  
  const components = {
    // Títulos (h2, h3)
    h2: ({ children, ...props }: any) => {
      const text = extractText(children);
      if (text.includes("Status:")) {
        return (
          <h2 className="text-base sm:text-lg md:text-xl font-bold mb-4 sm:mb-5 md:mb-6 text-gray-900 flex items-center gap-2 pb-3 sm:pb-4 border-b-2 border-gray-300 leading-tight">
            {children}
          </h2>
        );
      }
      return (
        <h2 className="text-base sm:text-lg md:text-xl font-bold mb-4 sm:mb-5 md:mb-6 mt-6 sm:mt-7 md:mt-8 text-gray-900 first:mt-0 leading-tight">
          {children}
        </h2>
      );
    },
    h3: ({ children, ...props }: any) => (
      <h3 className="text-[15px] sm:text-base md:text-lg font-semibold mb-3 sm:mb-4 md:mb-5 mt-5 sm:mt-6 md:mt-7 text-gray-900 leading-tight">
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
          <div className={`inline-flex items-center gap-2 px-2 sm:px-3 py-1 sm:py-1.5 rounded-md font-semibold text-sm sm:text-base mb-3 sm:mb-4 md:mb-5 ${
            isOK 
              ? "bg-green-50 text-green-700 border border-green-300" 
              : isWarning
              ? "bg-yellow-50 text-yellow-700 border border-yellow-300"
              : isCritical
              ? "bg-red-50 text-red-700 border border-red-300"
              : "bg-gray-50 text-gray-700 border border-gray-300"
          }`}>
            {isOK && <CheckCircle2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-green-600" />}
            {isWarning && <AlertTriangle className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-yellow-600" />}
            {isCritical && <XCircle className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-red-600" />}
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
          <div 
            className="bg-treq-warning-light border-l-4 border-treq-yellow pl-3 sm:pl-4 pr-3 sm:pr-4 py-3 sm:py-4 rounded-r-md mt-4 sm:mt-5 mb-4 sm:mb-5 shadow-sm"
            role="alert"
            aria-label="Ação recomendada"
          >
            <div className="flex items-start gap-2">
              <Lightbulb className="w-4 h-4 sm:w-5 sm:h-5 text-treq-yellow-dark flex-shrink-0 mt-0.5" aria-hidden="true" />
              <div className="flex-1">
                <div className="text-base sm:text-lg font-bold text-treq-gray-900 mb-2 sm:mb-3">Ação:</div>
                <div className="text-[15px] sm:text-base md:text-[16px] text-treq-gray-700 leading-[1.75] sm:leading-[1.8] text-justify">
                  {actionText || children}
                </div>
              </div>
            </div>
          </div>
        );
      }
      
      return (
        <p className="text-[15px] sm:text-base md:text-[16px] lg:text-[17px] text-gray-800 leading-[1.75] sm:leading-[1.8] md:leading-[1.85] mb-4 sm:mb-5 md:mb-6 last:mb-0 tracking-tight sm:tracking-normal text-justify">
          {children}
        </p>
      );
    },
    
    // Listas
    ul: ({ children, ...props }: any) => {
      // Converter children para array
      const childrenArray = Array.isArray(children) ? children : (children ? [children] : []);
      
      // Agrupar itens por tópicos (detectar padrões de agrupamento)
      const groupedItems: { topic?: string; items: any[] }[] = [];
      let currentGroup: any[] = [];
      let currentTopic: string | undefined = undefined;
      
      childrenArray.forEach((child: any) => {
        const text = extractText(child);
        
        // Detectar início de novo tópico (padrões comuns em análises operacionais)
        const topicMatch = text.match(/^(Vendas|Logística|Administrativo|Operacional|NE|BA|Recife|Salvador|Indicador|Métrica|Área|Unidade|Pedidos|Tempo|Ticket|Cancelamento|Atraso|Aprovação|Entrega):/i);
        const isTopicHeader = topicMatch !== null;
        
        if (isTopicHeader) {
          // Salvar grupo anterior se houver
          if (currentGroup.length > 0) {
            groupedItems.push({ topic: currentTopic, items: currentGroup });
          }
          // Iniciar novo grupo
          currentTopic = topicMatch[1];
          currentGroup = [child];
        } else {
          currentGroup.push(child);
        }
      });
      
      // Adicionar último grupo
      if (currentGroup.length > 0) {
        groupedItems.push({ topic: currentTopic, items: currentGroup });
      }
      
      // Se não há tópicos detectados, retornar lista normal (com texto justificado)
      if (groupedItems.length === 0 || (groupedItems.length === 1 && !groupedItems[0].topic)) {
        return (
          <ul className="list-none space-y-3 sm:space-y-4 md:space-y-4 my-5 sm:my-6 md:my-7">
            {children}
          </ul>
        );
      }
      
      return (
        <ul className="list-none my-5 sm:my-6 md:my-7">
          {groupedItems.map((group, groupIndex) => (
            <div key={groupIndex} className={groupIndex > 0 ? 'mt-6 sm:mt-7 md:mt-8' : ''}>
              {group.topic && (
                <div className="text-base sm:text-lg md:text-xl font-bold text-gray-900 mb-3 sm:mb-4 md:mb-5 pb-2 border-b-2 border-gray-300">
                  {group.topic}
                </div>
              )}
              <div className="space-y-3 sm:space-y-4 md:space-y-4">
                {group.items}
              </div>
            </div>
          ))}
        </ul>
      );
    },
    ol: ({ children, ...props }: any) => (
      <ol className="list-decimal list-inside space-y-3 sm:space-y-4 md:space-y-4 my-5 sm:my-6 md:my-7 ml-4 sm:ml-5 md:ml-6 text-justify">
        {children}
      </ol>
    ),
    li: ({ children, ...props }: any) => {
      const text = extractText(children);
      const hasBullet = text.startsWith("•") || text.match(/^\*\*/);
      
      if (hasBullet) {
        const cleanedText = text.replace(/^•\s*/, "").trim();
        return (
          <li className="flex items-start gap-3 sm:gap-3.5 md:gap-4 text-[15px] sm:text-base md:text-[16px] lg:text-[17px] text-gray-800 leading-[1.75] sm:leading-[1.8] md:leading-[1.85] mb-3 sm:mb-4 md:mb-4">
            <span className="text-treq-yellow-dark mt-[2px] sm:mt-[3px] flex-shrink-0 font-bold text-lg sm:text-xl md:text-xl">•</span>
            <span className="flex-1 text-justify">{cleanedText || children}</span>
          </li>
        );
      }
      return (
        <li className="text-[15px] sm:text-base md:text-[16px] lg:text-[17px] text-gray-800 leading-[1.75] sm:leading-[1.8] md:leading-[1.85] pl-3 sm:pl-4 md:pl-5 mb-3 sm:mb-4 md:mb-4 text-justify">
          {children}
        </li>
      );
    },
    
    // Negrito
    strong: ({ children, ...props }: any) => (
      <strong className="font-bold text-gray-900">
        {children}
      </strong>
    ),
    
    // Código inline
    code: ({ children, ...props }: any) => (
      <code className="bg-gray-100 px-1 sm:px-1.5 py-0.5 rounded text-xs font-mono text-gray-800">
        {children}
      </code>
    ),
    
    // Blocos de código
    pre: ({ children, ...props }: any) => (
      <pre className="bg-gray-100 p-2 sm:p-3 rounded-lg overflow-x-auto my-2 sm:my-3 text-xs sm:text-sm font-mono">
        {children}
      </pre>
    ),
    
    // Divisores horizontais
    hr: ({ ...props }: any) => (
      <hr className="my-6 sm:my-8 md:my-10 border-gray-300" />
    ),
  };

  // Renderizar resposta estruturada para gestores operacionais
  if (isOperationStatus) {
    const lines = parsed.answer.split('\n').filter(line => line.trim());
    const statusLine = lines.find(line => line.includes('✅') || line.includes('⚠️') || line.includes('🔴'));
    const problemsSection = lines.filter(line => 
      line.includes('•') && (line.includes('✅') || line.includes('⚠️') || line.includes('🔴'))
    );
    const summarySection = lines.filter(line => 
      line.includes('**') && (line.includes('Resumo:') || line.includes('Tendência:'))
    );
    const actionSection = lines.find(line => line.includes('💡') || line.includes('Ação:'));

    return (
      <div className={`${isHighContrast ? 'bg-black text-white' : 'bg-blue-50'} border-l-4 ${isHighContrast ? 'border-yellow-400' : 'border-blue-600'} rounded-r-lg p-3 sm:p-4 mt-2`}>
        <div className="flex items-start mb-2">
          <div className={`${isHighContrast ? 'bg-yellow-400 text-black' : 'bg-blue-600 text-white'} p-1.5 rounded-full mr-2 mt-0.5`}>
            <CheckCircle2 size={16} />
          </div>
          <h3 className={`font-medium text-sm sm:text-base ${isHighContrast ? 'text-yellow-300' : 'text-blue-900'}`}>
            Status Operacional
          </h3>
        </div>
        
        {statusLine && (
          <div className="mb-3">
            {statusLine.includes('✅') && (
              <div className="flex items-start gap-2 mb-1">
                <CheckCircle2 className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isHighContrast ? 'text-yellow-400' : 'text-green-600'}`} />
                <span className={`text-sm sm:text-base ${isHighContrast ? 'text-yellow-200' : 'text-green-800'}`}>
                  {statusLine.replace(/✅\s*/, '')}
                </span>
              </div>
            )}
            {statusLine.includes('⚠️') && (
              <div className="flex items-start gap-2 mb-1">
                <AlertTriangle className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isHighContrast ? 'text-yellow-400' : 'text-yellow-600'}`} />
                <span className={`text-sm sm:text-base ${isHighContrast ? 'text-yellow-200' : 'text-yellow-800'}`}>
                  {statusLine.replace(/⚠️\s*/, '')}
                </span>
              </div>
            )}
            {statusLine.includes('🔴') && (
              <div className="flex items-start gap-2 mb-1">
                <XCircle className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isHighContrast ? 'text-yellow-400' : 'text-red-600'}`} />
                <span className={`text-sm sm:text-base ${isHighContrast ? 'text-yellow-200' : 'text-red-800'}`}>
                  {statusLine.replace(/🔴\s*/, '')}
                </span>
              </div>
            )}
          </div>
        )}
        
        {problemsSection.length > 0 && (
          <div className="mb-3">
            {problemsSection.map((line, i) => {
              if (line.includes('✅')) {
                return (
                  <div key={i} className="flex items-start gap-2 mb-1">
                    <CheckCircle2 className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isHighContrast ? 'text-yellow-400' : 'text-green-600'}`} />
                    <span className={`text-sm sm:text-base ${isHighContrast ? 'text-yellow-200' : 'text-green-800'}`}>
                      {line.replace(/•\s*✅\s*/, '')}
                    </span>
                  </div>
                );
              }
              if (line.includes('⚠️')) {
                return (
                  <div key={i} className="flex items-start gap-2 mb-1">
                    <AlertTriangle className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isHighContrast ? 'text-yellow-400' : 'text-yellow-600'}`} />
                    <span className={`text-sm sm:text-base ${isHighContrast ? 'text-yellow-200' : 'text-yellow-800'}`}>
                      {line.replace(/•\s*⚠️\s*/, '')}
                    </span>
                  </div>
                );
              }
              if (line.includes('🔴')) {
                return (
                  <div key={i} className="flex items-start gap-2 mb-1">
                    <XCircle className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isHighContrast ? 'text-yellow-400' : 'text-red-600'}`} />
                    <span className={`text-sm sm:text-base ${isHighContrast ? 'text-yellow-200' : 'text-red-800'}`}>
                      {line.replace(/•\s*🔴\s*/, '')}
                    </span>
                  </div>
                );
              }
              return null;
            })}
          </div>
        )}
        
        {actionSection && (
          <div className={`mt-3 pt-3 border-t ${isHighContrast ? 'border-yellow-700' : 'border-blue-100'} flex justify-end`}>
            <button 
              className={`text-sm sm:text-base font-medium flex items-center gap-1 ${
                isHighContrast 
                  ? 'text-yellow-400 hover:text-yellow-200' 
                  : 'text-blue-700 hover:text-blue-900'
              }`}
              onClick={() => {
                // Disparar evento para navegação ao dashboard (implementar conforme necessário)
                window.dispatchEvent(new CustomEvent('navigate-dashboard'));
              }}
            >
              <BarChart2 size={14} /> Ver Dashboard Completo
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`prose prose-sm max-w-none prose-headings:mt-0 prose-headings:mb-0 prose-p:my-0 px-3 sm:px-4 md:px-5 lg:px-6 py-1 sm:py-2 ${
      isHighContrast ? 'prose-headings:text-yellow-200 prose-p:text-yellow-200 prose-strong:text-yellow-300' : ''
    }`}>
      {/* Renderizar aviso de processamento se for Consultoria (apenas uma vez) */}
      {hasConsultoriaProcessing && (
        <div className={`mb-3 sm:mb-4 p-3 sm:p-4 border-l-4 rounded-lg ${
          isHighContrast 
            ? 'bg-blue-900 border-blue-400' 
            : 'bg-blue-50 border-blue-400'
        }`}>
          <p className={`text-sm sm:text-base font-medium ${
            isHighContrast ? 'text-blue-200' : 'text-blue-800'
          }`}>
            ⏱️ <strong>Processamento:</strong> Esta análise requer processamento de todas as informações disponíveis. 
            A resposta pode levar alguns segundos adicionais para garantir máxima qualidade e precisão.
          </p>
        </div>
      )}
      
      {/* Renderizar disclaimer se for Consultoria (apenas uma vez) */}
      {hasConsultoriaDisclaimer && (
        <div className={`mb-3 sm:mb-4 p-3 sm:p-4 border-l-4 rounded-lg ${
          isHighContrast 
            ? 'bg-yellow-900 border-yellow-400' 
            : 'bg-yellow-50 border-yellow-400'
        }`}>
          <p className={`text-sm sm:text-base font-medium ${
            isHighContrast ? 'text-yellow-200' : 'text-yellow-800'
          }`}>
            ⚠️ <strong>Aviso:</strong> A inteligência artificial pode cometer erros. 
            Analise as sugestões com atenção e consulte fontes oficiais quando necessário para decisões críticas.
          </p>
        </div>
      )}
      
      {/* REMOVIDO: Renderização de pensamento/debug - nunca exibir ao usuário */}
      
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
