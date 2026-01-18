export function TypingIndicator() {
    return (
        <div data-testid="agent-bubble-loading" className="flex justify-start mb-6 animate-in fade-in slide-in-from-bottom-2 px-2 sm:px-2 md:px-1 lg:px-2">
            <div className="bg-white dark:bg-gray-900 rounded-lg px-4 py-3 sm:px-5 sm:py-4 border border-treq-gray-200 dark:border-gray-800 shadow-sm transition-all duration-300 w-fit">
                <div className="flex space-x-1.5 items-center h-5">
                    <div className="w-2 h-2 bg-treq-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-2 h-2 bg-treq-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-2 h-2 bg-treq-gray-400 rounded-full animate-bounce"></div>
                </div>
            </div>
        </div>
    );
}
