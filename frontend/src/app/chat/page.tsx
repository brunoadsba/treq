"use client";

import { useChat } from "@/hooks/useChat";
import { Header } from "@/components/Header";
import { MessageList } from "@/components/MessageList";
import { InputArea } from "@/components/InputArea";
import { QuickActions } from "@/components/QuickActions";
import { Toast } from "@/components/Toast";
import { ConversationHistory } from "@/components/ConversationHistory";
import { useToast } from "@/hooks/useToast";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

export default function ChatPage() {
  const router = useRouter();
  const [isAuthChecked, setIsAuthChecked] = useState(false);

  // Guard de Autenticação
  useEffect(() => {
    const token = localStorage.getItem("treq_token");
    if (!token) {
      router.push("/login");
    } else {
      setIsAuthChecked(true);
    }
  }, [router]);

  if (!isAuthChecked) {
    return null;
  }

  return <ChatContent />;
}

function ChatContent() {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    currentConversationId,
    startNewConversation,
    loadConversation,
    deleteConversation,
    getSavedConversations,
    exportConversation,
  } = useChat();
  const { toasts, showToast, removeToast } = useToast();
  const [showHistory, setShowHistory] = useState(false);
  const [isFooterFocused, setIsFooterFocused] = useState(false);

  // Mostrar toast de erro
  useEffect(() => {
    if (error) {
      showToast(error, "error");
    }
  }, [error, showToast]);

  const handleSendMessage = useCallback(async (message: string, actionId?: string, imageUrl?: string) => {
    try {
      const isDashboardQuery = message.toLowerCase().includes("status detalhado de todas as unidades") ||
        message.toLowerCase().includes("status de todas as unidades");

      const supportsVisualization = actionId ?
        (actionId === "alertas" || actionId === "status-recife" || actionId === "status-salvador") :
        false;

      const visualization = supportsVisualization || isDashboardQuery;
      const finalActionId = isDashboardQuery ? "alertas" : actionId;

      await sendMessage(
        message,
        undefined,
        true,
        visualization,
        finalActionId,
        imageUrl
      );
    } catch (err) {
      console.error("Erro ao enviar mensagem:", err);
    }
  }, [sendMessage]);

  useEffect(() => {
    const handleNavigateDashboard = () => {
      handleSendMessage("Status detalhado de todas as unidades");
    };

    window.addEventListener("navigate-dashboard", handleNavigateDashboard);
    return () => {
      window.removeEventListener("navigate-dashboard", handleNavigateDashboard);
    };
  }, [handleSendMessage]);

  const handleNewConversation = () => {
    if (messages.length > 0) {
      startNewConversation();
      showToast("Nova conversa iniciada. Histórico anterior foi salvo.", "success");
    }
  };

  const handleShowHistory = () => {
    setShowHistory(true);
  };

  const handleSelectConversation = (id: string) => {
    loadConversation(id);
    setShowHistory(false);
    showToast("Conversa carregada", "success");
  };

  const handleDeleteConversation = (id: string) => {
    deleteConversation(id);
    showToast("Conversa excluída", "success");
    const conversations = getSavedConversations();
    if (conversations.length === 0) {
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

  return (
    <div
      className="fixed inset-0 flex flex-col overflow-hidden bg-treq-gray-50 animate-in fade-in duration-500"
      role="main"
      aria-label="Chat do Assistente Operacional Treq"
    >
      <Header
        hasMessages={messages.length > 0}
        onNewConversation={handleNewConversation}
        onShowHistory={handleShowHistory}
        onExportConversation={handleExportConversation}
      />

      <div className="mt-0 flex-shrink-0">
        <QuickActions
          onActionClick={(query, actionId) => handleSendMessage(query, actionId)}
          disabled={isLoading}
        />
      </div>

      <div className="flex-1 min-h-0 overflow-hidden">
        <MessageList
          messages={messages}
          isLoading={isLoading}
        />
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
          conversations={getSavedConversations()}
          currentConversationId={currentConversationId}
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

