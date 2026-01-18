import { AgentMessage } from '../types';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { MessageSkeleton } from './bubbles/MessageSkeleton';
import { StreamingError } from './bubbles/StreamingError';

interface AgentChatProps {
    messages: AgentMessage[];
    isLoading: boolean;
    error: string | null;
    onSend: (message: string) => void;
    onRetry?: () => void;
}

export function AgentChat({ messages, isLoading, error, onSend, onRetry }: AgentChatProps) {
    return (
        <div className="flex flex-col h-full bg-treq-gray-50 dark:bg-treq-gray-900">
            {/* Messages Area */}
            <div className="flex-1 overflow-hidden relative flex flex-col">
                <MessageList messages={messages} isLoading={isLoading} />

                {/* Floating Skeleton during initial load if no messages */}
                {isLoading && messages.length === 0 && (
                    <div className="absolute inset-0 p-4">
                        <MessageSkeleton variant="text" />
                    </div>
                )}
            </div>

            {/* Error Message in Timeline */}
            {error && (
                <StreamingError
                    message={error}
                    onRetry={onRetry}
                />
            )}

            {/* Input Area - Floating & Transparent */}
            <div className="absolute bottom-0 left-0 right-0 z-20 pointer-events-none">
                <div className="pointer-events-auto">
                    <ChatInput
                        onSend={onSend}
                        isLoading={isLoading}
                        disabled={isLoading}
                        placeholder="Pergunte ao Agente Operacional..."
                    />
                </div>
            </div>
        </div>
    );
}
