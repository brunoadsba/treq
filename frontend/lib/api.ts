/**
 * Cliente API para comunicação com o backend.
 * 
 * Configurar variável de ambiente:
 * - NEXT_PUBLIC_API_URL (padrão: http://localhost:8000)
 */
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiResponse<T = unknown> {
  data?: T
  error?: string
  message?: string
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    const data = await response.json()

    if (!response.ok) {
      return {
        error: data.error || data.message || 'Erro na requisição',
      }
    }

    return { data: data as T }
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Erro desconhecido',
    }
  }
}

// Health check
export async function healthCheck(): Promise<boolean> {
  const response = await apiRequest<{ status: string }>('/health')
  return response.data?.status === 'ok'
}

