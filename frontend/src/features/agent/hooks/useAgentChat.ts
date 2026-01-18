import { useState, useCallback, useEffect } from 'react';
// import { v4 as uuidv4 } from 'uuid'; // Removed to avoid dependency
import { AgentMessage, ToolOutput } from '../types';
import { agentService } from '../api/agentService';
import { SavedConversation } from '@/hooks/useChat';

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
    const [messages, setMessages] = useState<AgentMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [conversationId, setConversationId] = useState<string>("");
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
    }, []);

    // Save current conversation to history whenever messages change
    useEffect(() => {
        if (messages.length === 0) return;

        setSavedConversations(prev => {
            const now = new Date().toISOString();
            const existingIndex = prev.findIndex(c => c.id === conversationId);

            // Generate title from first user message
            const firstUserMsg = messages.find(m => m.role === 'user');
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
        setMessages([]);
        setError(null);
    }, []);

    const startNewConversation = useCallback(() => {
        setMessages([]);
        setError(null);
        setConversationId(crypto.randomUUID());
    }, []);

    const loadConversation = useCallback((id: string) => {
        const conv = savedConversations.find(c => c.id === id);
        if (conv) {
            setMessages(conv.messages as any);
            setConversationId(id);
            setError(null);
        }
    }, [savedConversations]);

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

        setMessages((prev) => [...prev, newUserMsg]);

        try {
            // 2. Call API
            // Pass conversationId as thread_id if supported by backend, otherwise consistent user context
            const response = await agentService.sendMessage(query, conversationId || userId);

            // 3. Add Agent Response
            const agentMsg: AgentMessage = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: response.response,
                timestamp: new Date(),
                toolsUsed: response.tool_outputs,
            };

            setMessages((prev) => [...prev, agentMsg]);
        } catch (err: any) {
            console.error("Agent interaction failed:", err);
            setError(err.message || "Erro desconhecido ao comunicar com o agente.");
        } finally {
            setIsLoading(false);
        }
    }, [userId, conversationId]);

    const retryLastMessage = useCallback(async () => {
        const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
        if (lastUserMsg) {
            // Remove the error and try again
            setError(null);
            await sendMessage(lastUserMsg.content);
        }
    }, [messages, sendMessage]);

    return {
        messages,
        isLoading,
        error,
        sendMessage,
        retryLastMessage,
        clearMessages,

        conversationId,
        savedConversations,
        startNewConversation,
        loadConversation,
        deleteConversation
    };
}
