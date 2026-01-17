import { useEffect, useRef, useState } from 'react';
import { AgentMessage } from '../types';
import { UserBubble } from './bubbles/UserBubble';
import { AgentBubble } from './bubbles/AgentBubble';
import { TypingIndicator } from './bubbles/TypingIndicator';

interface MessageListProps {
    messages: AgentMessage[];
    isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
    const bottomRef = useRef<HTMLDivElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [shouldAutoScroll, setShouldAutoScroll] = useState(true);

    // Monitor scroll position to toggle auto-scroll
    const handleScroll = () => {
        if (!containerRef.current) return;
        const { scrollTop, scrollHeight, clientHeight } = containerRef.current;

        // If user is close to bottom (within 100px), enable auto-scroll
        const isCloseToBottom = scrollHeight - scrollTop - clientHeight < 100;
        setShouldAutoScroll(isCloseToBottom);
    };

    // Auto-scroll to bottom only if allowed
    useEffect(() => {
        if (shouldAutoScroll) {
            bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isLoading, shouldAutoScroll]);

    return (
        <div
            ref={containerRef}
            onScroll={handleScroll}
            className="flex-1 overflow-y-auto px-4 py-6 scrollbar-thin scrollbar-thumb-gray-200 dark:scrollbar-thumb-gray-800"
        >
            <div className="max-w-5xl mx-auto space-y-6 w-full">
                {/* Welcome Message if empty */}
                {messages.length === 0 && !isLoading && (
                    <div className="text-center py-20 opacity-50">
                        <h3 className="text-xl font-semibold mb-2">Treq Enterprise Agent</h3>
                        <p>Como posso ajudar você nas operações hoje?</p>
                    </div>
                )}

                {/* Messages */}
                {messages.map((msg) => (
                    msg.role === 'user' ? (
                        <UserBubble key={msg.id} content={msg.content} />
                    ) : (
                        <AgentBubble
                            key={msg.id}
                            content={msg.content}
                            toolsUsed={msg.toolsUsed}
                        />
                    )
                ))}

                {/* Loading Indicator (Agent "Thinking" bubble) */}
                {isLoading && (
                    <TypingIndicator />
                )}

                <div ref={bottomRef} className="h-1" />
            </div>
        </div>
    );
}
