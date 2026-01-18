import { Ticket } from 'lucide-react';
import { ToolCard } from './ToolCard';
import { ToolOutput } from '../../types';

interface JiraCardProps {
    output: ToolOutput;
}

export function JiraCard({ output }: JiraCardProps) {
    const { ticket_id, url, message } = output.result;

    const footerContent = url ? (
        <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-xs inline-flex items-center gap-1">
            Abrir no Jira &rarr;
        </a>
    ) : null;

    return (
        <ToolCard
            icon={Ticket}
            title="Jira Ticket"
            status={output.result.status === 'success' ? 'success' : 'error'}
            footer={footerContent}
        >
            <div className="flex flex-col gap-1">
                <p className="font-medium text-gray-900 dark:text-white">
                    {message || 'Ticket processado'}
                </p>
                {ticket_id && (
                    <div className="flex items-center justify-between gap-2 mt-2">
                        <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500">ID:</span>
                            <code className="bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded text-xs font-mono text-treq-blue-600">
                                {ticket_id}
                            </code>
                        </div>
                        {url && (
                            <div className="flex gap-2">
                                <a
                                    href={url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="px-3 py-1 bg-treq-blue-600 hover:bg-treq-blue-700 text-white rounded-md text-[10px] font-medium transition-all shadow-sm active:scale-95"
                                >
                                    Ver no Jira
                                </a>
                                <button
                                    className="px-3 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md text-[10px] font-medium transition-all shadow-sm active:scale-95"
                                    onClick={() => alert('Abrir modal de comentário - Em breve')}
                                >
                                    Comentar
                                </button>
                                <button
                                    className="px-3 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md text-[10px] font-medium transition-all shadow-sm active:scale-95"
                                    onClick={() => alert('Criar subtarefa - Em breve')}
                                >
                                    + Subtarefa
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </ToolCard>
    );
}
