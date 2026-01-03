"use client";

import { useChat } from "@/hooks/useChat";
import { Header } from "@/components/Header";
import { MessageList } from "@/components/MessageList";
import { InputArea } from "@/components/InputArea";
import { QuickActions } from "@/components/QuickActions";
import { Toast } from "@/components/Toast";
import { ConversationHistory } from "@/components/ConversationHistory";
import { useToast } from "@/hooks/useToast";
import { useEffect, useState } from "react";

export default function ChatPage() {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    conversationId,
    currentConversationId,
    startNewConversation,
    loadConversation,
    deleteConversation,
    getSavedConversations,
    exportConversation,
  } = useChat();
  const { toasts, showToast, removeToast } = useToast();
  const [showHistory, setShowHistory] = useState(false);

  // Mostrar toast de erro
  useEffect(() => {
    if (error) {
      showToast(error, "error");
    }
  }, [error, showToast]);

  // Removido: Eventos de fallback não são mais exibidos ao usuário
  // O fallback acontece silenciosamente em background sem notificar o usuário

  const handleSendMessage = async (message: string, actionId?: string, imageUrl?: string) => {
    try {
      // Detectar se é uma ação rápida que suporta visualização
      // QuickActions com supportsVisualization: true são: alertas, status-recife, status-salvador
      // Também detectar query de dashboard que deve gerar gráficos
      const isDashboardQuery = message.toLowerCase().includes("status detalhado de todas as unidades") ||
        message.toLowerCase().includes("status de todas as unidades");

      const supportsVisualization = actionId ?
        (actionId === "alertas" || actionId === "status-recife" || actionId === "status-salvador") :
        false;

      // Se for query de dashboard, tratar como visualização de alertas (gráfico geral)
      const visualization = supportsVisualization || isDashboardQuery;
      const finalActionId = isDashboardQuery ? "alertas" : actionId;

      await sendMessage(
        message,
        undefined,  // context
        true,  // useStream
        visualization,  // visualization
        finalActionId,  // actionId
        imageUrl // NOVO: Passar URL da imagem para o hook
      );
    } catch (err) {
      // Toast já é mostrado pelo useEffect acima
      console.error("Erro ao enviar mensagem:", err);
    }
  };

  // Listener para evento de navegação ao dashboard (deve vir depois da definição de handleSendMessage)
  useEffect(() => {
    const handleNavigateDashboard = () => {
      // Enviar query automática para status detalhado
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
    // Se não houver mais conversas, fechar histórico
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

      // Criar blob e fazer download
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
      className="flex flex-col h-[100dvh] overflow-hidden bg-treq-gray-50"
      role="main"
      aria-label="Chat do Assistente Operacional Treq"
      style={{ maxHeight: '100dvh', height: '100dvh' }}
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

      <div className="flex-shrink-0">
        <InputArea
          onSend={handleSendMessage}
          isLoading={isLoading}
          conversationId={conversationId || undefined}
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

      {/* Histórico de Conversas */}
      {showHistory && (
        <ConversationHistory
          conversations={getSavedConversations()}
          currentConversationId={currentConversationId}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
          onClose={() => setShowHistory(false)}
        />
      )}

      {/* Toasts - Stack com espaçamento */}
      <div className="fixed bottom-2 right-2 sm:bottom-4 sm:right-4 md:bottom-6 md:right-6 z-50 flex flex-col gap-1.5 sm:gap-2 items-end max-w-[calc(100vw-1rem)]" aria-live="polite" aria-atomic="false">
        {toasts.map((toast, index) => (
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

