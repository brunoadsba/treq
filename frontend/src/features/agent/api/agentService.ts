import { AgentChatRequest, AgentChatResponse } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

export const agentService = {
    /**
     * Envia uma mensagem para o Agente Enterprise.
     */
    async sendMessage(query: string, userId: string): Promise<AgentChatResponse> {
        const payload: AgentChatRequest = {
            query,
            user_id: userId,
        };

        try {
            const response = await fetch(`${API_BASE_URL}/agent/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // TODO: Adicionar Auth Token real quando integrado com NextAuth/Clerk
                    'X-User-ID': userId,
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                if (response.status === 429) {
                    throw new Error('Muitas requisições. Aguarde um momento antes de tentar novamente.');
                }
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Erro na comunicação com o Agente: ${response.status}`);
            }

            return await response.json();
        } catch (error: any) {
            console.error('[AgentService] Error:', error);
            throw error;
        }
    },
};
