import React, { useState } from 'react';
import { ReasoningPlan } from '@/hooks/useChat';
import { ChevronDown, ChevronUp, BrainCircuit, Lightbulb, Target, AlertTriangle, BarChart } from 'lucide-react';
import { cn } from '../lib/utils';

const STRATEGY_MAP: Record<string, string> = {
    "DIRECT": "RESPOSTA DIRETA",
    "RAG": "CONSULTA DOCUMENTAL",
    "COMPLEX": "ANÁLISE COMPLEXA",
    "TOOL": "USO DE FERRAMENTAS",
    "ROUTINE": "ROTINA",
    "ANALYTICAL": "ANÁLISE DETALHADA",
    "VISUAL": "VISUALIZAÇÃO",
    "REPORT": "RELATÓRIO",
    "CLARIFICATION": "ESCLARECIMENTO",
};

const VIZ_MAP: Record<string, string> = {
    "bar_chart": "Gráfico de Barras",
    "line_chart": "Gráfico de Linha",
    "pie_chart": "Gráfico de Pizza",
    "general": "Geral"
};

interface ReasoningDisplayProps {
    plan: ReasoningPlan;
    className?: string;
    defaultOpen?: boolean;
}

export const ReasoningDisplay: React.FC<ReasoningDisplayProps> = ({
    plan,
    className,
    defaultOpen = false
}) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    if (!plan) return null;

    return (
        <div className={cn("mt-2 mb-4 rounded-lg border border-purple-200 dark:border-purple-500/20 bg-purple-50/50 dark:bg-purple-500/5 overflow-hidden shadow-sm", className)}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-3 text-sm font-semibold text-purple-700 dark:text-purple-300 hover:bg-purple-100 dark:hover:bg-purple-500/10 active:bg-purple-200 dark:active:bg-purple-500/15 transition-all focus:outline-none rounded-t-lg"
            >
                <div className="flex items-center gap-2">
                    <BrainCircuit className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                    <span>Raciocínio</span>
                </div>
                {isOpen ? <ChevronUp className="w-4 h-4 text-purple-600 dark:text-purple-400" /> : <ChevronDown className="w-4 h-4 text-purple-700 dark:text-purple-500" />}
            </button>

            {isOpen && (
                <div className="p-3 sm:p-4 pt-0 text-sm space-y-4 animate-in fade-in slide-in-from-top-2 border-t border-purple-200 dark:border-purple-500/10 mt-1 pt-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="bg-purple-100/50 dark:bg-purple-900/20 p-3 rounded-md border border-purple-200/50 dark:border-purple-500/10">
                            <div className="text-[10px] sm:text-xs text-purple-700 dark:text-purple-400 flex items-center gap-1 mb-1.5 font-bold uppercase tracking-wider">
                                <Target className="w-3 h-3" /> Intenção
                            </div>
                            <div className="text-black dark:text-white font-semibold leading-relaxed">{plan.intent}</div>
                        </div>
                        <div className="bg-purple-100/50 dark:bg-purple-900/20 p-3 rounded-md border border-purple-200/50 dark:border-purple-500/10">
                            <div className="text-[10px] sm:text-xs text-purple-700 dark:text-purple-400 flex items-center gap-1 mb-1.5 font-bold uppercase tracking-wider">
                                <Lightbulb className="w-3 h-3" /> Estratégia
                            </div>
                            <div className="text-black dark:text-white font-semibold leading-relaxed">{STRATEGY_MAP[plan.strategy] || plan.strategy}</div>
                        </div>
                    </div>

                    <div className="space-y-2 mt-2">
                        <div className="text-[10px] sm:text-xs text-purple-700 dark:text-purple-400 font-bold uppercase tracking-wider mb-2">Passos de Análise</div>
                        <ul className="space-y-2 text-black dark:text-white">
                            {plan.reasoning_steps?.map((step, idx) => (
                                <li key={idx} className="flex items-start gap-2 leading-relaxed">
                                    <span className="text-purple-500 font-bold mt-0.5">•</span>
                                    <span>{step}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {plan.needs_visualization && (
                        <div className="bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 p-2.5 rounded-md mt-2 flex items-center gap-2">
                            <BarChart className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                            <span className="text-blue-700 dark:text-blue-200 text-xs font-medium">Visualização Gráfica Recomendada ({VIZ_MAP[plan.visualization_type || ""] || plan.visualization_type || "Geral"})</span>
                        </div>
                    )}

                    {plan.missing_info && plan.missing_info.length > 0 && (
                        <div className="bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/20 p-2.5 rounded-md mt-2">
                            <div className="text-xs text-yellow-700 dark:text-yellow-400 flex items-center gap-1 mb-2 font-bold uppercase">
                                <AlertTriangle className="w-3 h-3" /> Informações Faltantes
                            </div>
                            <ul className="space-y-1 text-black dark:text-white text-xs">
                                {plan.missing_info.map((info, idx) => (
                                    <li key={idx} className="flex items-start gap-2">
                                        <span className="text-yellow-600 font-bold">•</span>
                                        <span>{info}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
