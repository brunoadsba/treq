'use client';

import { Brain, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDebugMode } from '@/contexts/DebugContext';

interface ThinkingIndicatorProps {
    thought?: string;
    currentNode?: string;
    isVisible: boolean;
}

export function ThinkingIndicator({
    thought,
    currentNode,
    isVisible
}: ThinkingIndicatorProps) {
    const { isDebugMode } = useDebugMode();

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-start gap-3 p-4 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 shadow-sm mb-4"
                >
                    {/* Ícone animado */}
                    <div className="flex-shrink-0 mt-1">
                        <Brain className="w-5 h-5 text-yellow-600 dark:text-yellow-400 animate-pulse" />
                    </div>

                    <div className="flex-1 min-w-0">
                        {/* Texto padrão */}
                        {!isDebugMode && (
                            <p className="text-sm text-yellow-800 dark:text-yellow-200 font-medium">
                                Treq está analisando e preparando sua resposta...
                            </p>
                        )}

                        {/* Modo debug: detalhes completos */}
                        {isDebugMode && (
                            <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                    <Loader2 className="w-3.5 h-3.5 animate-spin text-yellow-600 dark:text-yellow-400" />
                                    <span className="text-xs font-mono font-bold text-yellow-700 dark:text-yellow-300 uppercase tracking-tight">
                                        Node Atual: {currentNode || 'PROCESSANDO'}
                                    </span>
                                </div>

                                {thought && (
                                    <div className="mt-2 p-3 rounded bg-yellow-100/50 dark:bg-yellow-900/40 border-l-4 border-yellow-500">
                                        <p className="text-[10px] font-bold text-yellow-900 dark:text-yellow-100 uppercase tracking-widest mb-1">
                                            Raciocínio Interno
                                        </p>
                                        <p className="text-sm text-yellow-800 dark:text-yellow-200 italic leading-relaxed">
                                            {thought}
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
