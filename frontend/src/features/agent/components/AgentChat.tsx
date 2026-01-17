import { AgentMessage } from '../types';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

interface AgentChatProps {
    messages: AgentMessage[];
    isLoading: boolean;
    error: string | null;
    onSend: (message: string) => void;
}

export function AgentChat({ messages, isLoading, error, onSend }: AgentChatProps) {
    return (
        <div className="flex flex-col h-full bg-treq-gray-50 dark:bg-treq-gray-900">
            {/* Messages Area */}
            <MessageList messages={messages} isLoading={isLoading} />

            {/* Error Toast/Banner */}
            {error && (
                <div className="px-4 py-2 bg-red-50 text-red-600 text-sm border-t border-red-100 text-center animate-in slide-in-from-bottom">
                    ⚠️ {error}
                </div>
            )}

            {/* Input Area */}
            <div className="flex-shrink-0 w-full backdrop-blur-sm bg-treq-gray-50/90 dark:bg-treq-gray-900/90">
                <ChatInput
                    onSend={onSend}
                    isLoading={isLoading}
                    disabled={isLoading}
                    placeholder="Pergunte ao Agente Operacional..."
                />
            </div>
        </div>
    );
}
