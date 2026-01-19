"use client";

import { useState, useCallback, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useUnifiedChat } from '@/hooks/useUnifiedChat';
import { useToast } from '@/hooks/useToast';
import { Header } from '@/components/Header';
import { MessageList } from '@/components/MessageList';
import { InputArea } from '@/components/InputArea';
import { QuickActions } from '@/components/QuickActions';
import { ConversationHistory } from '@/components/ConversationHistory';
import { Toast } from '@/components/Toast';
import { cn } from '@/lib/utils';

/**
 * Treq Assistant - Experiência unificada otimizada
 * Combina RAG + Agent + Consultoria com performance otimizada
 */
function UnifiedChatPage() {
  const router = useRouter();
  const [isAuthChecked, setIsAuthChecked] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [isFooterFocused, setIsFooterFocused] = useState(false);

  // Refs para auto-scroll
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Guard de Autenticação
  useEffect(() => {
    const token = localStorage.getItem("treq_token");
    if (!token) {
      router.push("/login");
    } else {
      setIsAuthChecked(true);
    }
  }, [router]);

  // Hook unificado
  const {
    messages,
    isLoading,
    error,
    currentMode,
    sendMessage,
    conversationId,
    startNewConversation,
    loadConversation,
    deleteConversation,
    savedConversations,
    exportConversation
  } = useUnifiedChat({ 
    mode: 'auto', 
    enableStreaming: true,
    enableVisualization: true,
    enableTools: true
  });

  const { toasts, showToast, removeToast } = useToast();

  // Auto-scroll para última mensagem
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      // Scroll instantâneo mais confiável
      messagesEndRef.current.scrollIntoView({ 
        behavior: 'auto',  // Mudado de 'smooth' para 'auto'
        block: 'nearest',
        inline: 'nearest'
      });
    }
  };

  // Scroll quando mensagens mudam - delay menor
  useEffect(() => {
    const timer = setTimeout(() => {
      scrollToBottom();
    }, 50);  // Reduzido de 100ms para 50ms
    return () => clearTimeout(timer);
  }, [messages]);

  // Scroll quando loading termina - delay menor
  useEffect(() => {
    if (!isLoading) {
      const timer = setTimeout(() => {
        scrollToBottom();
      }, 100);  // Reduzido de 200ms para 100ms
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  // Mostrar toast de erro
  useEffect(() => {
    if (error) {
      showToast(error, "error");
    }
  }, [error, showToast]);

  const handleSendMessage = useCallback(async (message: string, actionId?: string, imageUrl?: string) => {
    try {
      await sendMessage(message, { actionId, imageUrl });
    } catch (err) {
      console.error("Erro ao enviar mensagem:", err);
    }
  }, [sendMessage]);

  const handleNewConversation = () => {
    if (messages.length > 0) {
      startNewConversation();
      showToast("Nova conversa iniciada. Histórico anterior foi salvo.", "success");
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
    if (savedConversations.length === 0) {
      setShowHistory(false);
    }
  };

  const handleExportConversation = () => {
    try {
      const exportData = exportConversation();
      if (!exportData) {
        showToast("Nenhuma conversa para exportar", "warning");
        return;
      }

      const blob = new Blob([exportData], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `treq-conversa-${new Date().toISOString().split("T")[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showToast("Conversa exportada com sucesso", "success");
    } catch (error) {
      console.error("Erro ao exportar conversa:", error);
      showToast("Erro ao exportar conversa", "error");
    }
  };

  if (!isAuthChecked) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 flex flex-col overflow-hidden bg-treq-gray-50 animate-in fade-in duration-500"
      role="main"
      aria-label="Chat Unificado Treq - RAG + Agent"
    >
      {/* Header com indicador de modo */}
      <div className="flex-shrink-0">
        <Header
          hasMessages={messages.length > 0}
          onNewConversation={handleNewConversation}
          onShowHistory={() => setShowHistory(true)}
          onExportConversation={handleExportConversation}
        />
        
      </div>

      <div className="mt-0 flex-shrink-0">
        <QuickActions
          onActionClick={(query, actionId) => handleSendMessage(query, actionId)}
          disabled={isLoading}
        />
      </div>

      <div className="flex-1 min-h-0 overflow-hidden">
        <div className="h-full overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
          <MessageList
            messages={messages}
            isLoading={isLoading}
          />
          {/* Elemento invisível para auto-scroll */}
          <div 
            ref={messagesEndRef} 
            style={{ height: '1px', width: '100%' }}
          />
        </div>
      </div>

      <div className={cn(
        "flex-shrink-0 w-full transition-all duration-500 ease-in-out border-t",
        "bg-white dark:bg-black",
        isFooterFocused
          ? "border-treq-yellow shadow-[0_-4px_20px_rgba(255,221,0,0.08)]"
          : "border-treq-gray-100 dark:border-white/5 shadow-none"
      )}>
        <InputArea
          onSend={handleSendMessage}
          isLoading={isLoading}
          onFocusChange={setIsFooterFocused}
          onDocumentUploaded={(fileName, chunksIndexed) => {
            showToast(
              `Documento "${fileName}" enviado com sucesso! ${chunksIndexed} chunks indexados.`,
              "success"
            );
          }}
          onDocumentUploadError={(error) => {
            showToast(`Erro ao enviar documento: ${error}`, "error");
          }}
        />
      </div>

      {showHistory && (
        <ConversationHistory
          conversations={savedConversations}
          currentConversationId={conversationId}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
          onClose={() => setShowHistory(false)}
        />
      )}

      <div className="fixed bottom-2 right-2 sm:bottom-4 sm:right-4 md:bottom-6 md:right-6 z-50 flex flex-col gap-1.5 sm:gap-2 items-end max-w-[calc(100vw-1rem)]" aria-live="polite" aria-atomic="false">
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

export default function ChatPage() {
  return <UnifiedChatPage />;
}
