/**
 * Cliente API para comunicação com o backend.
 * 
 * Configurar variável de ambiente:
 * - NEXT_PUBLIC_API_URL (padrão: http://localhost:8000)
 */
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Constantes de configuração
const DEFAULT_TIMEOUT_MS = 30000 // 30 segundos
const MAX_RETRIES = 3
const RETRY_DELAY_MS = 1000 // 1 segundo inicial
const MAX_RETRY_DELAY_MS = 10000 // Máximo de 10 segundos

export interface ApiResponse<T = unknown> {
  data?: T
  error?: string
  message?: string
}

interface ApiRequestOptions extends RequestInit {
  timeout?: number
  retries?: number
  retryDelay?: number
}

/**
 * Cria um AbortController que cancela após timeout
 */
function createTimeoutController(timeoutMs: number): AbortController {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)
  
  // Limpar timeout se o controller já foi abortado
  controller.signal.addEventListener('abort', () => clearTimeout(timeoutId))
  
  return controller
}

/**
 * Sleep helper para retry com backoff exponencial
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Calcula delay para retry com backoff exponencial
 */
function calculateRetryDelay(attempt: number, baseDelay: number, maxDelay: number): number {
  const delay = baseDelay * Math.pow(2, attempt)
  return Math.min(delay, maxDelay)
}

/**
 * Verifica se um erro é retryable
 */
function isRetryableError(error: unknown): boolean {
  if (error instanceof Error) {
    // Erros de rede são retryable
    if (error.name === 'AbortError' || error.message.includes('network') || error.message.includes('fetch')) {
      return true
    }
  }
  return false
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<ApiResponse<T>> {
  const {
    timeout = DEFAULT_TIMEOUT_MS,
    retries = MAX_RETRIES,
    retryDelay = RETRY_DELAY_MS,
    headers,
    body,
    ...restOptions
  } = options

  // Detectar se body é FormData para não adicionar Content-Type
  const isFormData = body instanceof FormData
  
  // Preparar headers (não adicionar Content-Type para FormData, browser fará isso)
  const requestHeaders: HeadersInit = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...headers,
  }

  let lastError: Error | null = null

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      // Criar timeout controller para esta tentativa
      const timeoutController = createTimeoutController(timeout)
      
      // Combinar com signal existente se fornecido
      const signals: AbortSignal[] = [timeoutController.signal]
      if (options.signal) {
        signals.push(options.signal)
      }
      
      // Criar AbortController combinado
      const combinedController = new AbortController()
      signals.forEach(signal => {
        signal.addEventListener('abort', () => combinedController.abort())
      })

      const response = await fetch(`${API_URL}${endpoint}`, {
        ...restOptions,
        headers: requestHeaders,
        body,
        signal: combinedController.signal,
      })

      // Para erros HTTP, não fazer retry (exceto 429, 503, 504)
      if (!response.ok) {
        const shouldRetry = response.status === 429 || response.status === 503 || response.status === 504
        if (!shouldRetry || attempt >= retries) {
          const data = await response.json().catch(() => ({ message: response.statusText }))
          return {
            error: data.error || data.message || data.detail || 'Erro na requisição',
          }
        }
        // Retry para erros retryable HTTP
        lastError = new Error(`HTTP ${response.status}: ${response.statusText}`)
      } else {
        // Sucesso: parsear resposta
        const data = await response.json().catch(() => ({}))
        return { data: data as T }
      }
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error))
      
      // Se não for retryable ou última tentativa, retornar erro
      if (!isRetryableError(error) || attempt >= retries) {
        if (error instanceof Error && error.name === 'AbortError') {
          return {
            error: 'Timeout: A requisição demorou muito para responder',
          }
        }
        return {
          error: lastError.message || 'Erro desconhecido',
        }
      }
      
      // Calcular delay para próximo retry (backoff exponencial)
      const delay = calculateRetryDelay(attempt, retryDelay, MAX_RETRY_DELAY_MS)
      await sleep(delay)
    }
  }

  // Se chegou aqui, todas as tentativas falharam
  return {
    error: lastError?.message || 'Erro desconhecido após múltiplas tentativas',
  }
}

// Health check
export async function healthCheck(): Promise<boolean> {
  const response = await apiRequest<{ status: string }>('/health')
  return response.data?.status === 'ok'
}

