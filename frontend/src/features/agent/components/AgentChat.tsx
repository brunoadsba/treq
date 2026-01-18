import { useState } from 'react';
import { cn } from '@/lib/utils';
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
    const [isFooterFocused, setIsFooterFocused] = useState(false);

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

            {/* Input Area - High Contrast Foundation with Active State */}
            <div className={cn(
                "flex-shrink-0 w-full transition-all duration-500 ease-in-out border-t",
                "bg-white dark:bg-black",
                isFooterFocused
                    ? "border-treq-yellow shadow-[0_-4px_20px_rgba(255,221,0,0.08)]"
                    : "border-treq-gray-100 dark:border-white/5 shadow-none"
            )}>
                <ChatInput
                    onSend={onSend}
                    isLoading={isLoading}
                    disabled={isLoading}
                    onFocusChange={setIsFooterFocused}
                    placeholder="Pergunte ao Agente Operacional..."
                />
            </div>
        </div>
    );
}
