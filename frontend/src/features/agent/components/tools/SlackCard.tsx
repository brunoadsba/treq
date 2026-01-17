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
                    <div className="bg-gray-50 dark:bg-gray-800 p-2 rounded border-l-2 border-gray-300 dark:border-gray-600 text-xs italic text-gray-600 dark:text-gray-400">
                        "{message}"
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
