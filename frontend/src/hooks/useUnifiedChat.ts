import { useState, useCallback, useEffect } from 'react';
import { UnifiedMessage, UnifiedChatConfig, UnifiedChatReturn } from '@/types/unified';
import { useChat } from '@/hooks/useChat';
import { useAgentChat } from '@/features/agent/hooks/useAgentChat';

/**
 * Hook unificado que combina Chat RAG + Agent
 * Decide automaticamente qual sistema usar baseado na query
 */
export function useUnifiedChat(config: UnifiedChatConfig = { mode: 'auto' }): UnifiedChatReturn {
  const [currentMode, setCurrentMode] = useState<'rag' | 'agent'>('rag');
  
  // Hooks existentes
  const chatHook = useChat(config.userId);
  const agentHook = useAgentChat(config.userId);
  
  // Detectar automaticamente o modo baseado na mensagem
  const detectMode = useCallback((message: string): 'rag' | 'agent' => {
    if (config.mode !== 'auto') return config.mode as 'rag' | 'agent';
    
    // Palavras-chave que indicam necessidade de agente
    const agentKeywords = [
      'slack', 'jira', 'confluence', 'enviar', 'criar', 'atualizar',
      'conectar', 'integrar', 'ferramenta', 'tool', 'ação', 'executar'
    ];
    
    const lowerMessage = message.toLowerCase();
    const needsAgent = agentKeywords.some(keyword => lowerMessage.includes(keyword));
    
    return needsAgent ? 'agent' : 'rag';
  }, [config.mode]);
  
  // Converter mensagens para formato unificado
  const unifyMessages = useCallback((messages: any[], mode: 'rag' | 'agent'): UnifiedMessage[] => {
    return messages.map(msg => ({
      id: msg.id || crypto.randomUUID(),
      role: msg.role,
      content: msg.content,
      timestamp: msg.timestamp,
      
      // Chat fields
      ...(mode === 'rag' && {
        chartData: msg.chartData,
        reasoning: msg.reasoning,
        runId: msg.runId,
        isThinking: msg.isThinking,
        thinkingDuration: msg.thinkingDuration,
        imageUrl: msg.imageUrl,
      }),
      
      // Agent fields
      ...(mode === 'agent' && {
        toolsUsed: msg.toolsUsed,
      }),
    }));
  }, []);
  
  // Função unificada de envio
  const sendMessage = useCallback(async (message: string, options: any = {}) => {
    const detectedMode = detectMode(message);
    setCurrentMode(detectedMode);
    
    try {
      if (detectedMode === 'agent') {
        await agentHook.sendMessage(message);
      } else {
        await chatHook.sendMessage(
          message,
          options.context,
          config.enableStreaming ?? true,
          config.enableVisualization,
          options.actionId,
          options.imageUrl
        );
      }
    } catch (error) {
      console.error(`Erro no modo ${detectedMode}:`, error);
      // Fallback: tentar o outro modo em caso de erro
      try {
        const fallbackMode = detectedMode === 'agent' ? 'rag' : 'agent';
        setCurrentMode(fallbackMode);
        
        if (fallbackMode === 'agent') {
          await agentHook.sendMessage(message);
        } else {
          await chatHook.sendMessage(message);
        }
      } catch (fallbackError) {
        console.error('Erro no fallback também:', fallbackError);
        throw error; // Re-throw original error
      }
    }
  }, [detectMode, agentHook, chatHook, config]);
  
  // Determinar qual hook usar para cada propriedade
  const activeHook = currentMode === 'agent' ? agentHook : chatHook;
  
  // Unificar conversas salvas
  const savedConversations = [
    ...chatHook.getSavedConversations().map(conv => ({ ...conv, mode: 'rag' })),
    ...agentHook.savedConversations.map(conv => ({ ...conv, mode: 'agent' }))
  ].sort((a, b) => new Date(b.updatedAt || b.createdAt).getTime() - new Date(a.updatedAt || a.createdAt).getTime());
  
  return {
    // Estado unificado
    messages: unifyMessages(activeHook.messages, currentMode),
    isLoading: activeHook.isLoading,
    error: activeHook.error,
    conversationId: activeHook.conversationId,
    currentMode,
    
    // Ações unificadas
    sendMessage,
    startNewConversation: activeHook.startNewConversation,
    loadConversation: (id: string) => {
      const conv = savedConversations.find((c: any) => c.id === id);
      if (conv) {
        setCurrentMode(conv.mode || 'rag');
        if (conv.mode === 'agent') {
          agentHook.loadConversation(id);
        } else {
          chatHook.loadConversation(id);
        }
      }
    },
    deleteConversation: (id: string) => {
      const conv = savedConversations.find((c: any) => c.id === id);
      if (conv?.mode === 'agent') {
        agentHook.deleteConversation(id);
      } else {
        chatHook.deleteConversation(id);
      }
    },
    
    // Histórico unificado
    savedConversations,
    exportConversation: () => {
      const data = {
        messages: unifyMessages(activeHook.messages, currentMode),
        conversationId: activeHook.conversationId,
        mode: currentMode,
        exportedAt: new Date().toISOString()
      };
      return JSON.stringify(data, null, 2);
    }
  };
}
