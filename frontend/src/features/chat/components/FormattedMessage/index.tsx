"use client";

import React, { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { CheckCircle2, AlertTriangle, XCircle, BarChart2, Lightbulb } from "lucide-react";
import { useHighContrast } from "@/hooks/useHighContrast";
import {
    sanitizeTechnicalTerms,
    parseChainOfThought,
    formatActionBlocks,
    repairMarkdown
} from "../../utils/message-parser";
import { getMarkdownComponents } from "./MarkdownComponents";

interface FormattedMessageProps {
    content: string;
}

/**
 * Componente principal para renderização de mensagens formatadas.
 * Suporta MD, Chain of Thought, e layouts especializados para Operações.
 */
export function FormattedMessage({ content }: FormattedMessageProps) {
    const isHighContrast = useHighContrast();

    // 1. Pipeline de Transformação de Texto
    const formattedContent = useMemo(() => {
        let text = sanitizeTechnicalTerms(content);

        // Remove blocos de pensamento/resposta (CoT)
        const parsed = parseChainOfThought(text);
        text = parsed.answer;

        // Corrige blocos de ação colados ou quebrados
        // e fecha tags markdown pendentes
        text = formatActionBlocks(text);
        text = repairMarkdown(text);

        // Forçar quebras de linha antes de bullets para evitar blocos compactos
        return text
            .replace(/([^\n])\s*•/g, "$1\n\n•")
            .replace(/([^\n])\s*\-\s/g, "$1\n\n- ");
    }, [content]);

    // 2. Detecção de Layout Especializado (Status Operacional)
    const isOperationStatus = useMemo(() => {
        const hasStatusWord = formattedContent.includes("Status:") || formattedContent.includes("**Status:");
        const hasLevels = formattedContent.includes("Nível 1") || formattedContent.includes("Nível 2");
        const isConsultancy = formattedContent.toLowerCase().includes("consultoria:");

        return (hasStatusWord || hasLevels) && !isConsultancy;
    }, [formattedContent]);

    // 3. Divisão de blocos (Normal vs Ação)
    const blocks = useMemo(() => {
        // Encontrar o divisor "Ação:"
        const actionMatch = formattedContent.match(/💡\s*\*\*?Ação:\*\*?/i);
        if (!actionMatch) return { main: formattedContent, action: null };

        const index = actionMatch.index!;
        return {
            main: formattedContent.substring(0, index).trim(),
            action: formattedContent.substring(index).trim()
        };
    }, [formattedContent]);

    const components = useMemo(() =>
        getMarkdownComponents({ isHighContrast }),
        [isHighContrast]);

    // Layout de Status Operacional (Card Azul/Especial)
    if (isOperationStatus) {
        const lines = formattedContent.split('\n').filter(line => line.trim());
        const statusLine = lines.find(line => line.includes('✅') || line.includes('⚠️') || line.includes('🔴'));

        return (
            <div className={`${isHighContrast ? 'bg-black text-white' : 'bg-blue-50 text-treq-black'} border-l-4 ${isHighContrast ? 'border-yellow-400' : 'border-blue-600'} rounded-r-lg p-3 sm:p-4 mt-2`}>
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
                        <div className="flex items-start gap-2 mb-1">
                            {statusLine.includes('✅') && <CheckCircle2 className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isHighContrast ? 'text-yellow-400' : 'text-green-600'}`} />}
                            {statusLine.includes('⚠️') && <AlertTriangle className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isHighContrast ? 'text-yellow-400' : 'text-yellow-600'}`} />}
                            {statusLine.includes('🔴') && <XCircle className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isHighContrast ? 'text-yellow-400' : 'text-red-600'}`} />}
                            <span className={`text-sm sm:text-base ${isHighContrast ? 'text-yellow-200' : 'text-blue-800'}`}>
                                {statusLine.replace(/^(✅|⚠️|🔴|•\s*(✅|⚠️|🔴))\s*/, '')}
                            </span>
                        </div>
                    </div>
                )}

                {/* Renderizar o resto via Markdown normal dentro do card */}
                <div className="prose prose-sm max-w-none prose-p:my-1 prose-headings:text-blue-900 mb-4">
                    <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} components={components}>
                        {formattedContent.replace(statusLine || "", "")}
                    </ReactMarkdown>
                </div>

                {/* Legenda de Níveis - Mobile First & Dark Mode Support */}
                <div className={`${isHighContrast ? 'bg-black border border-yellow-400' : 'bg-blue-100/40 dark:bg-blue-900/20 border border-blue-200/50 dark:border-blue-800/30'} rounded-md p-2 sm:p-2.5 text-[10px] sm:text-xs`}>
                    <div className="flex flex-wrap items-center justify-between gap-y-2">
                        <div className="flex gap-x-3 sm:gap-x-4">
                            <div className="flex items-center gap-1.5 font-medium">
                                <div className="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]"></div>
                                <span className={isHighContrast ? 'text-yellow-200' : 'text-blue-800 dark:text-blue-200'}>Normal</span>
                            </div>
                            <div className="flex items-center gap-1.5 font-medium">
                                <div className="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-yellow-400 shadow-[0_0_8px_rgba(250,204,21,0.4)]"></div>
                                <span className={isHighContrast ? 'text-yellow-200' : 'text-blue-800 dark:text-blue-200'}>Nível 1: Atenção</span>
                            </div>
                            <div className="flex items-center gap-1.5 font-medium">
                                <div className="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]"></div>
                                <span className={isHighContrast ? 'text-yellow-200' : 'text-blue-800 dark:text-blue-200'}>Nível 2: Crítico</span>
                            </div>
                        </div>
                        <div className="italic font-medium opacity-60 dark:text-blue-300">
                            Fonte: Manual Treq
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Layout Padrão com Ação ISOLADA
    return (
        <div className={`prose prose-sm max-w-none prose-headings:mt-0 prose-headings:mb-0 prose-p:my-0 px-1 sm:px-4 md:px-5 lg:px-6 py-1 sm:py-2 ${isHighContrast ? 'prose-headings:text-yellow-200 prose-p:text-yellow-200 prose-strong:text-yellow-300' : ''
            }`}>
            {/* Parte Principal */}
            {blocks.main && (
                <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} components={components}>
                    {blocks.main}
                </ReactMarkdown>
            )}

            {/* Bloco de Ação (Garante que nunca seja splitado por parágrafos) */}
            {blocks.action && (
                <div className="bg-treq-warning-light border-l-4 border-treq-yellow pl-3 sm:pl-4 pr-3 sm:pr-4 py-3 sm:py-4 rounded-r-md mt-4 shadow-sm text-treq-black" role="alert">
                    <div className="flex items-start gap-2">
                        <Lightbulb className="w-4 h-4 sm:w-5 sm:h-5 text-treq-yellow-dark flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                            <div className="text-base sm:text-lg font-bold mb-2">Ação:</div>
                            <div className="text-[15px] sm:text-base md:text-[16px] leading-relaxed text-justify prose-p:my-1">
                                <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                                    {blocks.action.replace(/💡\s*\*\*?Ação:\*\*?\s*/i, "").trim()}
                                </ReactMarkdown>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Legenda de Níveis Global - Mobile Optimized */}
            {!isOperationStatus && (formattedContent.includes("Nível 1") || formattedContent.includes("Nível 2")) && (
                <div className={`mt-4 border-t pt-2 ${isHighContrast ? 'border-yellow-400 text-yellow-200' : 'border-gray-100 dark:border-gray-800 text-gray-400 dark:text-gray-500'} text-[10px] sm:text-[11px] italic font-medium flex flex-wrap justify-between items-center gap-y-2`}>
                    <div className="flex gap-x-3 sm:gap-x-4">
                        <span className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-green-500"></div> Normal</span>
                        <span className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-yellow-400"></div> Nível 1: Atenção</span>
                        <span className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-red-500"></div> Nível 2: Crítico</span>
                    </div>
                    <span>Fonte: Manual de Procedimentos</span>
                </div>
            )}
        </div>
    );
}
