"use client";

import { useState, useEffect, useMemo } from "react";
import { SavedConversation } from "@/hooks/useChat";
import { Search, X, MessageSquare, Clock, Trash2 } from "lucide-react";
import { useHighContrast } from "@/hooks/useHighContrast";

interface ConversationHistoryProps {
  conversations: SavedConversation[];
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onClose: () => void;
}

export function ConversationHistory({
  conversations,
  currentConversationId,
  onSelectConversation,
  onDeleteConversation,
  onClose,
}: ConversationHistoryProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const isHighContrast = useHighContrast();

  const filteredConversations = useMemo(() => {
    if (!searchQuery.trim()) return conversations;
    
    const query = searchQuery.toLowerCase();
    return conversations.filter(
      (conv) =>
        conv.title.toLowerCase().includes(query) ||
        conv.messages.some((msg) =>
          msg.content.toLowerCase().includes(query)
        )
    );
  }, [conversations, searchQuery]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Agora";
    if (diffMins < 60) return `${diffMins}m atrás`;
    if (diffHours < 24) return `${diffHours}h atrás`;
    if (diffDays < 7) return `${diffDays}d atrás`;
    return date.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
  };

  return (
    <div className={`fixed inset-0 z-50 flex ${isHighContrast ? 'bg-black' : 'bg-black bg-opacity-50'}`}>
      {/* Overlay para fechar */}
      <div className="absolute inset-0" onClick={onClose} aria-hidden="true" />
      
      {/* Sidebar */}
      <div className={`relative w-full max-w-[90vw] sm:w-96 md:w-[420px] ${isHighContrast ? 'bg-black border-r border-white' : 'bg-white'} shadow-xl flex flex-col`}>
        {/* Header */}
        <div className={`p-4 border-b ${isHighContrast ? 'border-white' : 'border-treq-gray-200'} flex items-center justify-between`}>
          <h2 className={`text-lg font-semibold ${isHighContrast ? 'text-white' : 'text-treq-gray-900'}`}>
            Histórico de Conversas
          </h2>
          <button
            onClick={onClose}
            className={`p-2 rounded-lg hover:bg-treq-gray-100 transition-colors ${isHighContrast ? 'hover:bg-treq-gray-800 text-white' : ''}`}
            aria-label="Fechar histórico"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Busca */}
        <div className={`p-4 border-b ${isHighContrast ? 'border-white' : 'border-treq-gray-200'}`}>
          <div className="relative">
            <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 ${isHighContrast ? 'text-white' : 'text-treq-gray-400'}`} />
            <input
              type="text"
              placeholder="Buscar conversas..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full pl-10 pr-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-treq-yellow ${
                isHighContrast
                  ? 'bg-black border-white text-white placeholder:text-treq-gray-400'
                  : 'bg-white border-treq-gray-300 text-treq-gray-900 placeholder:text-treq-gray-400'
              }`}
              aria-label="Buscar conversas"
            />
          </div>
        </div>

        {/* Lista de conversas */}
        <div className="flex-1 overflow-y-auto">
          {filteredConversations.length === 0 ? (
            <div className={`p-8 text-center ${isHighContrast ? 'text-white' : 'text-treq-gray-500'}`}>
              <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-sm">
                {searchQuery ? "Nenhuma conversa encontrada" : "Nenhuma conversa salva"}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-treq-gray-200">
              {filteredConversations.map((conversation) => {
                const isActive = conversation.id === currentConversationId;
                const messageCount = conversation.messages.length;
                
                return (
                  <div
                    key={conversation.id}
                    className={`p-4 hover:bg-treq-gray-50 transition-colors cursor-pointer group ${
                      isActive ? (isHighContrast ? 'bg-treq-gray-800 border-l-4 border-treq-yellow' : 'bg-treq-yellow-light border-l-4 border-treq-yellow') : ''
                    } ${isHighContrast ? 'hover:bg-treq-gray-800' : ''}`}
                    onClick={() => onSelectConversation(conversation.id)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className={`text-sm font-medium mb-1 truncate ${
                          isActive 
                            ? (isHighContrast ? 'text-treq-yellow' : 'text-treq-gray-900')
                            : (isHighContrast ? 'text-white' : 'text-treq-gray-900')
                        }`}>
                          {conversation.title}
                        </h3>
                        <div className="flex items-center gap-3 text-xs text-treq-gray-500 mb-2">
                          <span className="flex items-center gap-1">
                            <MessageSquare className="w-3 h-3" />
                            {messageCount} {messageCount === 1 ? 'mensagem' : 'mensagens'}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatDate(conversation.updatedAt)}
                          </span>
                        </div>
                        {conversation.messages.length > 0 && (
                          <p className={`text-xs truncate ${
                            isHighContrast ? 'text-treq-gray-400' : 'text-treq-gray-600'
                          }`}>
                            {conversation.messages[0].content.substring(0, 60)}...
                          </p>
                        )}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (confirm("Deseja excluir esta conversa?")) {
                            onDeleteConversation(conversation.id);
                          }
                        }}
                        className={`opacity-0 group-hover:opacity-100 p-1.5 rounded hover:bg-treq-error-light transition-all ${
                          isHighContrast ? 'hover:bg-treq-gray-700' : ''
                        }`}
                        aria-label={`Excluir conversa: ${conversation.title}`}
                        title="Excluir conversa"
                      >
                        <Trash2 className={`w-4 h-4 ${isHighContrast ? 'text-white' : 'text-treq-error'}`} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className={`p-4 border-t ${isHighContrast ? 'border-white' : 'border-treq-gray-200'} text-xs ${isHighContrast ? 'text-white' : 'text-treq-gray-500'}`}>
          {conversations.length} {conversations.length === 1 ? 'conversa salva' : 'conversas salvas'}
        </div>
      </div>
    </div>
  );
}
