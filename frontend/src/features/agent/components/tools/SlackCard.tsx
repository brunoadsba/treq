import { MessageSquare } from 'lucide-react';
import { ToolCard } from './ToolCard';
import { ToolOutput } from '../../types';

interface SlackCardProps {
    output: ToolOutput;
}

export function SlackCard({ output }: SlackCardProps) {
    const { channel, timestamp, message } = output.result;

    return (
        <ToolCard icon={MessageSquare} title="Slack Notification" status="success">
            <div className="flex flex-col gap-2">
                <p className="text-sm text-gray-600 dark:text-gray-300">
                    Enviado para <span className="font-semibold text-gray-900 dark:text-white">#{channel}</span>
                </p>

                {message && (
                    <div className="flex flex-col gap-2">
                        <div className="bg-gray-50 dark:bg-gray-800 p-2 rounded border-l-2 border-gray-300 dark:border-gray-600 text-xs italic text-gray-600 dark:text-gray-400">
                            "{message}"
                        </div>
                        <div className="flex justify-between items-center mt-1">
                            <span className="text-[10px] text-green-600 dark:text-green-400 font-medium flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                                Mensagem enviada
                            </span>
                            <button
                                className="px-3 py-1 bg-treq-gray-100 dark:bg-gray-800 hover:bg-treq-gray-200 dark:hover:bg-gray-700 text-treq-gray-700 dark:text-gray-300 rounded-md text-[10px] font-medium transition-all border border-treq-gray-200 dark:border-gray-700 shadow-sm active:scale-95"
                                onClick={() => window.open(`slack://channel?id=${channel}`, '_blank')}
                            >
                                Abrir Canal
                            </button>
                        </div>
                    </div>
                )}

                {timestamp && (
                    <div className="flex justify-end">
                        <span className="text-[10px] text-gray-400">
                            {new Date(Number(timestamp) * 1000).toLocaleString('pt-BR')}
                        </span>
                    </div>
                )}
            </div>
        </ToolCard>
    );
}
