/**
 * Tipos unificados para fusão Chat + Agent
 * Compatível com ambos os sistemas existentes
 */

export interface UnifiedMessage {
  // Campos obrigatórios (comum a ambos)
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date | string;
  
  // Chat features (opcional)
  chartData?: any;
  reasoning?: any;
  runId?: string;
  isThinking?: boolean;
  thinkingDuration?: number;
  imageUrl?: string;
  
  // Agent features (opcional)
  toolsUsed?: any[];
}

export interface UnifiedChatConfig {
  mode: 'rag' | 'agent' | 'auto';
  enableStreaming?: boolean;
  enableVisualization?: boolean;
  enableTools?: boolean;
  userId?: string;
}

export interface UnifiedChatState {
  messages: UnifiedMessage[];
  conversationId: string | null;
  isLoading: boolean;
  error: string | null;
  mode: 'rag' | 'agent';
}

export interface UnifiedChatReturn {
  // Estado
  messages: UnifiedMessage[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  currentMode: 'rag' | 'agent';
  
  // Ações
  sendMessage: (message: string, options?: any) => Promise<void>;
  startNewConversation: () => void;
  loadConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  
  // Histórico
  savedConversations: any[];
  exportConversation: () => string | null;
}
