'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Clock, CheckCircle2, XCircle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import {
    parseExecutionTrace,
    formatDuration,
    getNodeColor,
    getNodeIcon,
    type ParsedTrace
} from '@/lib/thought-parser';
import { useDebugMode } from '@/contexts/DebugContext';

interface ThoughtTimelineProps {
    executionTrace: any[];
}

export function ThoughtTimeline({ executionTrace }: ThoughtTimelineProps) {
    const { expandedNodes, toggleNode } = useDebugMode();

    const parsed: ParsedTrace = useMemo(
        () => parseExecutionTrace(executionTrace),
        [executionTrace]
    );

    if (parsed.nodes.length === 0) {
        return null;
    }

    return (
        <div className="mt-4 p-4 rounded-xl bg-gray-50/50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-800 shadow-inner">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <span className="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-tight">
                        Trace de Execução
                    </span>
                </div>

                <div className="flex items-center gap-4 text-[10px] font-mono text-gray-500 uppercase">
                    <span>{parsed.nodes.length} ETAPAS</span>
                    <span>{formatDuration(parsed.totalDuration)}</span>
                    {parsed.hasErrors && (
                        <span className="text-red-500 flex items-center gap-1 font-bold">
                            <AlertCircle className="w-3 h-3" />
                            ERROS
                        </span>
                    )}
                </div>
            </div>

            {/* Timeline */}
            <div className="space-y-4">
                {parsed.nodes.map((node, index) => (
                    <motion.div
                        key={node.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="relative"
                    >
                        {/* Linha conectora */}
                        {index < parsed.nodes.length - 1 && (
                            <div className="absolute left-6 top-12 w-0.5 h-6 bg-gray-200 dark:bg-gray-800" />
                        )}

                        {/* Nó */}
                        <div
                            onClick={() => toggleNode(node.id)}
                            className={`
                flex items-start gap-4 p-3 rounded-xl border-2
                transition-all cursor-pointer select-none
                ${expandedNodes.has(node.id)
                                    ? 'bg-white dark:bg-gray-800 shadow-lg scale-[1.02] border-yellow-500/30'
                                    : 'hover:bg-white dark:hover:bg-gray-800 border-transparent'
                                }
                ${getNodeColor(node.node)}
              `}
                        >
                            {/* Ícone do nó */}
                            <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-white dark:bg-gray-900 flex items-center justify-center text-xl shadow-sm border border-gray-100 dark:border-gray-800">
                                {getNodeIcon(node.node)}
                            </div>

                            {/* Conteúdo */}
                            <div className="flex-1 min-w-0 py-1">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="font-bold text-sm capitalize tracking-tight">
                                        Node: {node.node}
                                    </span>

                                    <div className="flex items-center gap-2">
                                        {node.duration !== undefined && (
                                            <span className="text-[10px] font-mono opacity-50 px-1.5 py-0.5 bg-black/5 dark:bg-white/5 rounded">
                                                {formatDuration(node.duration)}
                                            </span>
                                        )}

                                        {node.status === 'success' ? (
                                            <CheckCircle2 className="w-4 h-4 text-green-500" />
                                        ) : (
                                            <XCircle className="w-4 h-4 text-red-500" />
                                        )}

                                        {expandedNodes.has(node.id) ? (
                                            <ChevronUp className="w-4 h-4 opacity-30" />
                                        ) : (
                                            <ChevronDown className="w-4 h-4 opacity-30" />
                                        )}
                                    </div>
                                </div>

                                {/* Thought (preview) */}
                                {node.thought && !expandedNodes.has(node.id) && (
                                    <p className="text-xs opacity-60 line-clamp-1 italic italic">
                                        {node.thought}
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* Detalhes expandidos */}
                        {expandedNodes.has(node.id) && (
                            <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                className="ml-16 mt-3 p-4 rounded-xl bg-white dark:bg-gray-800 border-2 border-gray-100 dark:border-gray-700 shadow-sm"
                            >
                                {node.thought && (
                                    <div className="mb-4">
                                        <p className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-2">
                                            Raciocínio Interno
                                        </p>
                                        <p className="text-sm text-gray-800 dark:text-gray-200 italic leading-relaxed bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg border-l-4 border-yellow-500">
                                            {node.thought}
                                        </p>
                                    </div>
                                )}

                                {/* Metadata */}
                                {node.metadata && Object.keys(node.metadata).length > 0 && (
                                    <div>
                                        <p className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-2">
                                            Dados do Node
                                        </p>
                                        <div className="bg-gray-900 dark:bg-black p-3 rounded-lg overflow-x-auto">
                                            <pre className="text-[10px] font-mono text-green-400 leading-tight">
                                                {JSON.stringify(node.metadata, null, 2)}
                                            </pre>
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        )}
                    </motion.div>
                ))}
            </div>

            {/* Footer */}
            <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between text-[10px] font-mono text-gray-400 uppercase">
                    <span className="truncate max-w-[70%]">
                        Fluxo: {parsed.nodeSequence.join(' ➜ ')}
                    </span>
                    <span className="font-bold text-gray-500">
                        FIM DO RASTRO
                    </span>
                </div>
            </div>
        </div>
    );
}
