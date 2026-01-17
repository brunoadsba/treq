import { AlertCircle, RefreshCw } from 'lucide-react';

interface StreamingErrorProps {
    message: string;
    onRetry?: () => void;
}

export function StreamingError({ message, onRetry }: StreamingErrorProps) {
    return (
        <div className="flex justify-start mb-6 animate-in fade-in slide-in-from-bottom-2 px-2 sm:px-2 md:px-1 lg:px-2">
            <div className="bg-red-50 dark:bg-red-900/10 rounded-lg px-4 py-3 sm:px-5 sm:py-4 border border-red-100 dark:border-red-900/20 shadow-sm transition-all duration-300 w-full max-w-lg">
                <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                        <p className="text-sm font-medium text-red-800 dark:text-red-300">
                            Ocorreu um erro no processamento
                        </p>
                        <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                            {message}
                        </p>
                        {onRetry && (
                            <button
                                onClick={onRetry}
                                className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-red-700 dark:text-red-300 hover:text-red-800 dark:hover:text-red-100 transition-colors"
                            >
                                <RefreshCw className="w-3.5 h-3.5" />
                                Tentar novamente
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
