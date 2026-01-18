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

interface FeatureState {
    messages: ChatMessage[];
    conversationId: string | null;
    isLoading: boolean;
    error: string | null;
}

interface ChatContextType {
    chatState: FeatureState;
    setChatState: React.Dispatch<React.SetStateAction<FeatureState>>;
    agentState: FeatureState;
    setAgentState: React.Dispatch<React.SetStateAction<FeatureState>>;
    clearChatSession: () => void;
    clearAgentSession: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

const STORAGE_KEYS = {
    CHAT_MESSAGES: 'treq_chat_active_messages',
    CHAT_CONV_ID: 'treq_chat_active_conversation_id',
    AGENT_MESSAGES: 'treq_agent_active_messages',
    AGENT_CONV_ID: 'treq_agent_active_conversation_id',
};

const DEFAULT_STATE: FeatureState = {
    messages: [],
    conversationId: null,
    isLoading: false,
    error: null,
};

export function ChatProvider({ children }: { children: ReactNode }) {
    const [chatState, setChatState] = useState<FeatureState>(DEFAULT_STATE);
    const [agentState, setAgentState] = useState<FeatureState>(DEFAULT_STATE);

    // Initial restore from localStorage
    useEffect(() => {
        const savedChatMessages = localStorage.getItem(STORAGE_KEYS.CHAT_MESSAGES);
        const savedChatId = localStorage.getItem(STORAGE_KEYS.CHAT_CONV_ID);
        const savedAgentMessages = localStorage.getItem(STORAGE_KEYS.AGENT_MESSAGES);
        const savedAgentId = localStorage.getItem(STORAGE_KEYS.AGENT_CONV_ID);

        if (savedChatMessages) {
            try {
                setChatState(prev => ({
                    ...prev,
                    messages: JSON.parse(savedChatMessages),
                    conversationId: savedChatId
                }));
            } catch (e) { console.error("Failed to parse chat messages", e); }
        } else if (savedChatId) {
            setChatState(prev => ({ ...prev, conversationId: savedChatId }));
        }

        if (savedAgentMessages) {
            try {
                setAgentState(prev => ({
                    ...prev,
                    messages: JSON.parse(savedAgentMessages),
                    conversationId: savedAgentId
                }));
            } catch (e) { console.error("Failed to parse agent messages", e); }
        } else if (savedAgentId) {
            setAgentState(prev => ({ ...prev, conversationId: savedAgentId }));
        }
    }, []);

    // Persist Chat State
    useEffect(() => {
        if (chatState.messages.length > 0) {
            localStorage.setItem(STORAGE_KEYS.CHAT_MESSAGES, JSON.stringify(chatState.messages));
        } else {
            localStorage.removeItem(STORAGE_KEYS.CHAT_MESSAGES);
        }
        if (chatState.conversationId) {
            localStorage.setItem(STORAGE_KEYS.CHAT_CONV_ID, chatState.conversationId);
        } else {
            localStorage.removeItem(STORAGE_KEYS.CHAT_CONV_ID);
        }
    }, [chatState.messages, chatState.conversationId]);

    // Persist Agent State
    useEffect(() => {
        if (agentState.messages.length > 0) {
            localStorage.setItem(STORAGE_KEYS.AGENT_MESSAGES, JSON.stringify(agentState.messages));
        } else {
            localStorage.removeItem(STORAGE_KEYS.AGENT_MESSAGES);
        }
        if (agentState.conversationId) {
            localStorage.setItem(STORAGE_KEYS.AGENT_CONV_ID, agentState.conversationId);
        } else {
            localStorage.removeItem(STORAGE_KEYS.AGENT_CONV_ID);
        }
    }, [agentState.messages, agentState.conversationId]);

    const clearChatSession = useCallback(() => {
        setChatState(DEFAULT_STATE);
        localStorage.removeItem(STORAGE_KEYS.CHAT_MESSAGES);
        localStorage.removeItem(STORAGE_KEYS.CHAT_CONV_ID);
    }, []);

    const clearAgentSession = useCallback(() => {
        setAgentState(DEFAULT_STATE);
        localStorage.removeItem(STORAGE_KEYS.AGENT_MESSAGES);
        localStorage.removeItem(STORAGE_KEYS.AGENT_CONV_ID);
    }, []);

    return (
        <ChatContext.Provider value={{
            chatState,
            setChatState,
            agentState,
            setAgentState,
            clearChatSession,
            clearAgentSession
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
