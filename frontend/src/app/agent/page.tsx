"use client";

import { useEffect, useState } from 'react';
import { AgentChat } from '@/features/agent/components/AgentChat';
import { Header } from '@/components/Header';
import { ConversationHistory } from '@/components/ConversationHistory';
import { useAgentChat } from '@/features/agent/hooks/useAgentChat';
import { useToast } from '@/hooks/useToast';
import { useRouter } from 'next/navigation';
import { Toast } from '@/components/Toast';

export default function AgentPage() {
    const router = useRouter();

    // Guard de Autenticação
    useEffect(() => {
        const token = localStorage.getItem("treq_token");
        if (!token) {
            router.push("/login");
        }
    }, [router]);

    const [showHistory, setShowHistory] = useState(false);
    const { toasts, showToast, removeToast } = useToast();

    const {
        messages,
        isLoading,
        error,
        sendMessage,
        retryLastMessage,
        conversationId,
        savedConversations,
        startNewConversation,
        loadConversation,
        deleteConversation
    } = useAgentChat();

    const handleNewConversation = () => {
        if (messages.length > 0) {
            startNewConversation();
            showToast("Nova conversa iniciada", "success");
        }
    };

    const handleSelectConversation = (id: string) => {
        loadConversation(id);
        setShowHistory(false);
        showToast("Conversa carregada", "success");
    };

    const handleDeleteConversation = (id: string) => {
        deleteConversation(id);
        showToast("Conversa excluída", "success");
        if (savedConversations.length <= 1) { // Lógica simplificada, o hook atualiza o estado
            // se era a última, pode querer fechar, mas o estado reactivo cuida disso no componente
        }
    };

    return (
        <div className="flex flex-col h-screen overflow-hidden animate-in fade-in duration-500">
            <Header
                title="Agente Operacional"
                hasMessages={messages.length > 0}
                onNewConversation={handleNewConversation}
                onShowHistory={() => setShowHistory(true)}
            />

            <div className="flex-1 overflow-hidden">
                <AgentChat
                    messages={messages}
                    isLoading={isLoading}
                    error={error}
                    onSend={sendMessage}
                    onRetry={retryLastMessage}
                />
            </div>

            {/* Histórico de Conversas */}
            {showHistory && (
                <ConversationHistory
                    conversations={savedConversations}
                    currentConversationId={conversationId}
                    onSelectConversation={handleSelectConversation}
                    onDeleteConversation={handleDeleteConversation}
                    onClose={() => setShowHistory(false)}
                />
            )}

            {/* Toasts */}
            <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 items-end">
                {toasts.map((toast) => (
                    <Toast
                        key={toast.id}
                        message={toast.message}
                        type={toast.type}
                        onClose={() => removeToast(toast.id)}
                    />
                ))}
            </div>
        </div>
    );
}
