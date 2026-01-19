import { useState, useCallback, useEffect } from 'react';
// import { v4 as uuidv4 } from 'uuid'; // Removed to avoid dependency
import { AgentMessage, ToolOutput } from '../types';
import { agentService } from '../api/agentService';
import { SavedConversation } from '@/hooks/useChat';
import { useChatContext } from '@/context/ChatContext';

interface UseAgentChatReturn {
    messages: AgentMessage[];
    isLoading: boolean;
    error: string | null;
    sendMessage: (query: string) => Promise<void>;
    retryLastMessage: () => Promise<void>;
    clearMessages: () => void;

    // History specific
    conversationId: string;
    savedConversations: SavedConversation[];
    startNewConversation: () => void;
    loadConversation: (id: string) => void;
    deleteConversation: (id: string) => void;
}

const STORAGE_KEY = 'treq-agent-history';

export function useAgentChat(userId: string = "default-user"): UseAgentChatReturn {
    const {
        agentState,
        setAgentState,
        clearAgentSession
    } = useChatContext();

    const { messages, conversationId, isLoading, error } = agentState;

    // Helper setters for compatibility
    const setMessages = useCallback((updater: AgentMessage[] | ((prev: AgentMessage[]) => AgentMessage[])) => {
        setAgentState(prev => ({
            ...prev,
            messages: (typeof updater === 'function' ? updater(prev.messages as any) : updater) as any
        }));
    }, [setAgentState]);

    const setConversationId = useCallback((id: string | null) => {
        setAgentState(prev => ({ ...prev, conversationId: id }));
    }, [setAgentState]);

    const setIsLoading = useCallback((loading: boolean) => {
        setAgentState(prev => ({ ...prev, isLoading: loading }));
    }, [setAgentState]);

    const setError = useCallback((err: string | null) => {
        setAgentState(prev => ({ ...prev, error: err }));
    }, [setAgentState]);

    const [savedConversations, setSavedConversations] = useState<SavedConversation[]>([]);

    // Load saved conversations on mount
    useEffect(() => {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                setSavedConversations(JSON.parse(saved));
            }
        } catch (e) {
            console.error("Failed to load agent history", e);
        }

        // Init a new conversation ID if needed
        if (!conversationId) {
            setConversationId(crypto.randomUUID());
        }
    }, [conversationId, setConversationId]);

    // Save current conversation to history whenever messages change
    useEffect(() => {
        if (messages.length === 0 || !conversationId) return;

        setSavedConversations((prev: SavedConversation[]) => {
            const now = new Date().toISOString();
            const existingIndex = prev.findIndex((c: SavedConversation) => c.id === conversationId);

            // Generate title from first user message
            const firstUserMsg = messages.find((m: any) => m.role === 'user');
            const title = firstUserMsg
                ? (firstUserMsg.content.length > 30 ? firstUserMsg.content.substring(0, 30) + '...' : firstUserMsg.content)
                : 'Nova Conversa';

            const updatedConv: SavedConversation = {
                id: conversationId,
                title: title,
                messages: messages as any, // Cast to any to fit SavedConversation structure broadly
                conversationId: conversationId,
                createdAt: existingIndex >= 0 ? prev[existingIndex].createdAt : now,
                updatedAt: now
            };

            let newHistory;
            if (existingIndex >= 0) {
                newHistory = [...prev];
                newHistory[existingIndex] = updatedConv;
            } else {
                newHistory = [updatedConv, ...prev];
            }

            // Persist to storage
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(newHistory));
            } catch (e) {
                console.error("Failed to save agent history", e);
            }

            return newHistory;
        });
    }, [messages, conversationId]);

    const clearMessages = useCallback(() => {
        clearAgentSession();
    }, [clearAgentSession]);

    const startNewConversation = useCallback(() => {
        clearAgentSession();
        setConversationId(crypto.randomUUID());
    }, [clearAgentSession, setConversationId]);

    const loadConversation = useCallback((id: string) => {
        const conv = savedConversations.find(c => c.id === id);
        if (conv) {
            setMessages(conv.messages as any);
            setConversationId(id);
            setError(null);
        }
    }, [savedConversations, setMessages, setConversationId, setError]);

    const deleteConversation = useCallback((id: string) => {
        setSavedConversations(prev => {
            const newHistory = prev.filter(c => c.id !== id);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(newHistory));
            return newHistory;
        });

        if (id === conversationId) {
            startNewConversation();
        }
    }, [conversationId, startNewConversation]);

    const sendMessage = useCallback(async (query: string) => {
        if (!query.trim()) return;

        setIsLoading(true);
        setError(null);

        // 1. Optimistic UI: Add User Message immediately
        const userMsgId = crypto.randomUUID();
        const newUserMsg: AgentMessage = {
            id: userMsgId,
            role: 'user',
            content: query,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, newUserMsg as any]);

        try {
            // 2. Call API
            const response = await agentService.sendMessage(query, conversationId || userId);

            // 3. Add Agent Response
            const agentMsg: AgentMessage = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: response.response,
                timestamp: new Date(),
                toolsUsed: response.tool_outputs,
            };

            setMessages((prev) => [...prev, agentMsg as any]);
        } catch (err: any) {
            console.error("Agent interaction failed:", err);
            setError(err.message || "Erro desconhecido ao comunicar com o agente.");
        } finally {
            setIsLoading(false);
        }
    }, [userId, conversationId, setMessages, setIsLoading, setError]);

    const retryLastMessage = useCallback(async () => {
        const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
        if (lastUserMsg) {
            // Remove the error and try again
            setError(null);
            await sendMessage(lastUserMsg.content);
        }
    }, [messages, sendMessage, setError]);

    return {
        messages: messages as any[],
        isLoading,
        error,
        sendMessage,
        retryLastMessage,
        clearMessages,

        conversationId: conversationId || "",
        savedConversations,
        startNewConversation,
        loadConversation,
        deleteConversation
    };
}
