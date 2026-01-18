'use client';

import { useState } from 'react';
import { apiRequest } from '@/lib/api';

interface ToolActionResponse {
    success: boolean;
    message?: string;
    data?: any;
}

export function useToolAction() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const executeAction = async (
        toolName: string,
        args: Record<string, any>,
        threadId?: string
    ): Promise<ToolActionResponse> => {
        setIsLoading(true);
        setError(null);

        try {
            // Endpoint genérico para execução manual de ferramentas
            const response = await apiRequest<ToolActionResponse>('/agent/tools/execute', {
                method: 'POST',
                body: JSON.stringify({
                    tool_name: toolName,
                    arguments: args,
                    thread_id: threadId,
                }),
            });

            if (response.error) {
                throw new Error(response.error);
            }

            return response.data || { success: true };

        } catch (err: any) {
            const msg = err.message || 'Falha ao executar ação';
            setError(msg);
            return { success: false, message: msg };

        } finally {
            setIsLoading(false);
        }
    };

    return { executeAction, isLoading, error };
}
