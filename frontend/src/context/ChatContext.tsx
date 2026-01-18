"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

// Shared types compliant with existing structures
export interface ChatMessage {
    id?: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp?: string | Date;
    toolsUsed?: any[];
    chartData?: any;
    reasoning?: any;
    isLoading?: boolean;
    runId?: string;
    isThinking?: boolean;
}

interface ChatContextType {
    messages: ChatMessage[];
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
    conversationId: string | null;
    setConversationId: (id: string | null) => void;
    isLoading: boolean;
    setIsLoading: (loading: boolean) => void;
    error: string | null;
    setError: (error: string | null) => void;
    clearSession: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

const STORAGE_KEYS = {
    MESSAGES: 'treq_active_messages',
    CONVERSATION_ID: 'treq_active_conversation_id',
};

export function ChatProvider({ children }: { children: ReactNode }) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [conversationId, setConversationId] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Initial restore from localStorage
    useEffect(() => {
        const savedMessages = localStorage.getItem(STORAGE_KEYS.MESSAGES);
        const savedId = localStorage.getItem(STORAGE_KEYS.CONVERSATION_ID);

        if (savedMessages) {
            try {
                setMessages(JSON.parse(savedMessages));
            } catch (e) {
                console.error("Failed to parse saved messages", e);
            }
        }
        if (savedId) {
            setConversationId(savedId);
        }
    }, []);

    // Persist on change
    useEffect(() => {
        if (messages.length > 0) {
            localStorage.setItem(STORAGE_KEYS.MESSAGES, JSON.stringify(messages));
        } else {
            localStorage.removeItem(STORAGE_KEYS.MESSAGES);
        }
    }, [messages]);

    useEffect(() => {
        if (conversationId) {
            localStorage.setItem(STORAGE_KEYS.CONVERSATION_ID, conversationId);
        } else {
            localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
        }
    }, [conversationId]);

    const clearSession = useCallback(() => {
        setMessages([]);
        setConversationId(null);
        setError(null);
        localStorage.removeItem(STORAGE_KEYS.MESSAGES);
        localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
    }, []);

    return (
        <ChatContext.Provider value={{
            messages,
            setMessages,
            conversationId,
            setConversationId,
            isLoading,
            setIsLoading,
            error,
            setError,
            clearSession
        }}>
            {children}
        </ChatContext.Provider>
    );
}

export function useChatContext() {
    const context = useContext(ChatContext);
    if (context === undefined) {
        throw new Error('useChatContext must be used within a ChatProvider');
    }
    return context;
}
