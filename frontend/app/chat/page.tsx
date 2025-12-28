"use client";

import { useChat } from "../hooks/useChat";
import { Header } from "../components/Header";
import { MessageList } from "../components/MessageList";
import { InputArea } from "../components/InputArea";
import { QuickActions } from "../components/QuickActions";
import { Toast } from "../components/Toast";
import { useToast } from "../hooks/useToast";
import { useEffect } from "react";

export default function ChatPage() {
  const { messages, isLoading, error, sendMessage, conversationId } = useChat();
  const { toasts, showToast, removeToast } = useToast();

  // Mostrar toast de erro
  useEffect(() => {
    if (error) {
      showToast(error, "error");
    }
  }, [error, showToast]);

  const handleSendMessage = async (message: string) => {
    try {
      await sendMessage(message);
    } catch (err) {
      // Toast já é mostrado pelo useEffect acima
      console.error("Erro ao enviar mensagem:", err);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />
      
      <QuickActions onActionClick={handleSendMessage} disabled={isLoading} />
      
      <MessageList messages={messages} isLoading={isLoading} />
      
      <InputArea 
        onSend={handleSendMessage} 
        isLoading={isLoading}
        conversationId={conversationId || undefined}
        onDocumentUploaded={(fileName, chunksIndexed) => {
          showToast(
            `✅ Documento "${fileName}" enviado com sucesso! ${chunksIndexed} chunks indexados.`,
            "success"
          );
        }}
        onDocumentUploadError={(error) => {
          showToast(`❌ Erro ao enviar documento: ${error}`, "error");
        }}
      />

      {/* Toasts */}
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  );
}

