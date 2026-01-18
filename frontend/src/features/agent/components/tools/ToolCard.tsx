import { LucideIcon } from 'lucide-react';

interface ToolCardProps {
    icon: LucideIcon;
    title: string;
    status?: 'success' | 'error' | 'pending';
    children: React.ReactNode;
    footer?: React.ReactNode;
}

export function ToolCard({ icon: Icon, title, status = 'success', children, footer }: ToolCardProps) {
    const statusConfig = {
        success: { color: 'border-l-green-500', bg: 'bg-green-50/50 dark:bg-green-900/10', iconColor: 'text-green-600 dark:text-green-400' },
        error: { color: 'border-l-red-500', bg: 'bg-red-50/50 dark:bg-red-900/10', iconColor: 'text-red-600 dark:text-red-400' },
        pending: { color: 'border-l-blue-500', bg: 'bg-blue-50/50 dark:bg-blue-900/10', iconColor: 'text-blue-600 dark:text-blue-400' },
    };

    const config = statusConfig[status];

    return (
        <div className={`rounded-md border border-gray-200 dark:border-gray-800 overflow-hidden shadow-sm my-3 ${config.color} border-l-4 animate-in fade-in slide-in-from-bottom-1`}>
            {/* Header */}
            <div className={`flex items-center gap-2 px-4 py-2.5 ${config.bg} border-b border-gray-100 dark:border-gray-800`}>
                <Icon className={`w-4 h-4 ${config.iconColor}`} />
                <span className="text-sm font-semibold text-gray-700 dark:text-gray-200 flex-1">
                    {title}
                </span>
                {status !== 'success' && (
                    <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider px-2 py-0.5 rounded border border-gray-200 dark:border-gray-700 bg-white dark:bg-black">
                        {status === 'error' ? 'Falha' : 'Info'}
                    </span>
                )}
            </div>

            {/* Body */}
            <div className="p-4 text-sm text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-900">
                {children}
            </div>

            {/* Footer */}
            {footer && (
                <div className="px-3 py-2 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-100 dark:border-gray-800 text-xs text-gray-500">
                    {footer}
                </div>
            )}
        </div>
    );
}
