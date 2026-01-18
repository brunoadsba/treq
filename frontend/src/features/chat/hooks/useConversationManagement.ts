import { useCallback } from "react";
import { ChatMessage, SavedConversation } from "../types";

export function useConversationManagement(userId: string) {
    const getSavedConversations = useCallback((): SavedConversation[] => {
        if (typeof window === "undefined") return [];
        try {
            const conversations = JSON.parse(
                localStorage.getItem(`chat_conversations_${userId}`) || "[]"
            ) as SavedConversation[];
            return conversations;
        } catch (error) {
            console.error("Erro ao carregar conversas salvas:", error);
            return [];
        }
    }, [userId]);

    const saveConversation = useCallback((
        messages: ChatMessage[],
        conversationId: string | null,
        currentConversationId: string | null
    ) => {
        if (typeof window === "undefined" || messages.length === 0) return null;

        const conversations = getSavedConversations();
        const firstUserMessage = messages.find((m) => m.role === "user");
        const title = firstUserMessage?.content.substring(0, 50) || "Nova conversa";

        const conversationIdToUse = currentConversationId || `conv_${Date.now()}`;
        const existingIndex = conversations.findIndex((c) => c.id === conversationIdToUse);

        const conversation: SavedConversation = {
            id: conversationIdToUse,
            title,
            messages: [...messages],
            conversationId,
            createdAt: messages[0]?.timestamp?.toString() || new Date().toISOString(),
            updatedAt: new Date().toISOString(),
        };

        if (existingIndex >= 0) {
            conversations[existingIndex] = conversation;
        } else {
            conversations.unshift(conversation);
        }

        const limitedConversations = conversations.slice(0, 50);
        localStorage.setItem(`chat_conversations_${userId}`, JSON.stringify(limitedConversations));

        return conversationIdToUse;
    }, [userId, getSavedConversations]);

    const deleteConversationFromStorage = useCallback((id: string) => {
        if (typeof window === "undefined") return;
        const conversations = getSavedConversations();
        const filtered = conversations.filter(c => c.id !== id);
        localStorage.setItem(`chat_conversations_${userId}`, JSON.stringify(filtered));
    }, [userId, getSavedConversations]);

    return {
        getSavedConversations,
        saveConversation,
        deleteConversationFromStorage
    };
}
