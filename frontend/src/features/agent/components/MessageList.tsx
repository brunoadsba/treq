import { useEffect, useRef, useState } from 'react';
import { AgentMessage } from '../types';
import { UserBubble } from './bubbles/UserBubble';
import { AgentBubble } from './bubbles/AgentBubble';
import { MessageSkeleton } from './bubbles/MessageSkeleton';

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

    // Auto-scroll to bottom only if allowed (Scroll Lock Awareness)
    useEffect(() => {
        if (shouldAutoScroll && containerRef.current) {
            containerRef.current.scrollTo({
                top: containerRef.current.scrollHeight,
                behavior: messages.length > 0 && messages[messages.length - 1].role === 'user' ? 'smooth' : 'auto'
            });
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
                    <div className="flex flex-col items-center justify-center h-[60vh] animate-in fade-in zoom-in duration-1000">
                        <div className="flex items-center gap-3">
                            <div className="w-5 h-5 bg-treq-yellow rounded-md flex items-center justify-center shadow-md shadow-treq-yellow/10 animate-subtle-sway">
                                <span className="text-treq-black text-[10px] font-black">T</span>
                            </div>
                            <span className="text-treq-gray-900 dark:text-white text-2xl font-serif italic tracking-tight">
                                {new Intl.DateTimeFormat('pt-BR', {
                                    weekday: 'long',
                                    day: 'numeric',
                                    month: 'long',
                                    year: 'numeric'
                                }).format(new Date()).replace(/^\w/, (c) => c.toUpperCase())}
                            </span>
                        </div>
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

                {/* Loading Indicator (Agent "Thinking" skeleton) */}
                {isLoading && (
                    <MessageSkeleton variant="text" />
                )}

                <div ref={bottomRef} className="h-1" />
            </div>
        </div>
    );
}
