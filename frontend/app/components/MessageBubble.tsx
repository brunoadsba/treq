"use client";

import { useState, lazy, Suspense, useMemo } from "react";
import { ChatMessage } from "../hooks/useChat";
import { Volume2, Loader2, Pause, Play, Gauge } from "lucide-react";
import { useTTS, PLAYBACK_RATES } from "../hooks/useTTS";

// Lazy loading para FormattedMessage (componente pesado com markdown)
const FormattedMessage = lazy(() => import("./FormattedMessage").then(m => ({ default: m.FormattedMessage })));
// Lazy loading para ChartMessage (componente pesado com Recharts)
const ChartMessage = lazy(() => import("./ChartMessage").then(m => ({ default: m.ChartMessage })));
// Import direto para ChartLoadingSkeleton (componente leve)
import { ChartLoadingSkeleton } from "./ChartLoadingSkeleton";

// Função para processar conteúdo removendo tags <pensamento> e <resposta>
// DEVE ser idêntica à função parseChainOfThought do FormattedMessage
// para garantir que áudio e visualização usem o mesmo conteúdo processado
function parseContentForAudio(text: string): string {
  if (!text || typeof text !== 'string') return text;
  
  // SEMPRE remove tag <pensamento> completamente do texto (nunca exibir ao usuário)
  let content = text.replace(/<pensamento>[\s\S]*?<\/pensamento>/gi, '').trim();
  
  // Extrair conteúdo de dentro das tags <resposta> (pode haver múltiplas)
  const respostaMatches = content.match(/<resposta>([\s\S]*?)<\/resposta>/gi);
  let answer: string;
  
  if (respostaMatches && respostaMatches.length > 0) {
    // Extrair conteúdo de todas as tags <resposta> e juntar
    answer = respostaMatches
      .map(match => {
        const innerMatch = match.match(/<resposta>([\s\S]*?)<\/resposta>/i);
        return innerMatch ? innerMatch[1].trim() : '';
      })
      .filter(text => text.length > 0)
      .join('\n\n')
      .trim();
    
    // Se não conseguiu extrair conteúdo válido, usar texto completo sem as tags
    if (!answer || answer.length === 0) {
      answer = content.replace(/<resposta>[\s\S]*?<\/resposta>/gi, '').trim();
    }
  } else {
    // Não há tags <resposta>, usar texto completo
    answer = content.trim();
  }
  
  // REMOVER TODAS as tags <resposta> e </resposta> que possam ter sobrado (segurança extra)
  answer = answer
    .replace(/<resposta>/gi, '')
    .replace(/<\/resposta>/gi, '')
    .replace(/<pensamento>[\s\S]*?<\/pensamento>/gi, '') // Remover pensamento novamente (segurança extra)
    .trim();
  
  // Remover avisos duplicados do markdown (o frontend já renderiza esses cards)
  answer = answer
    .replace(/⏱️\s*\*\*Processamento:\*\*[^\n]*\n?/gi, '')
    .replace(/⚠️\s*\*\*Aviso:\*\*[^\n]*\n?/gi, '')
    .replace(/Esta análise requer processamento[^\n]*precisão\.?\s*/gi, '')
    .replace(/A inteligência artificial pode cometer erros[^\n]*críticas\.?\s*/gi, '')
    .replace(/^\s*\n\s*\n/gm, '\n')  // Remover linhas vazias extras
    .trim();
  
  return answer;
}

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const { 
    speak, 
    pause, 
    resume, 
    stop, 
    setPlaybackRate,
    playbackRate,
    isSpeaking, 
    isPaused, 
    isLoading 
  } = useTTS();
  
  const [showSpeedMenu, setShowSpeedMenu] = useState(false);

  // Processar conteúdo para áudio (remover tags <pensamento> e <resposta>)
  // CRÍTICO: Usar exatamente o mesmo conteúdo processado que é exibido visualmente
  const processedContentForAudio = useMemo(() => {
    if (!message.content || isUser) return message.content;
    return parseContentForAudio(message.content);
  }, [message.content, isUser]);

  const handleAudioControl = async () => {
    if (!isUser && processedContentForAudio) {
      if (isLoading) {
        // Não fazer nada enquanto carrega
        return;
      }
      
      if (isPaused) {
        // Retomar reprodução
        await resume();
      } else if (isSpeaking) {
        // Pausar reprodução
        pause();
      } else {
        // Iniciar reprodução com conteúdo PROCESSADO (sem tags <pensamento>)
        await speak(processedContentForAudio);
      }
    }
  };

  // Determinar ícone e título baseado no estado
  const getIconAndTitle = () => {
    if (isLoading) {
      return {
        icon: <Loader2 className="w-4 h-4 animate-spin" />,
        title: "Carregando áudio...",
      };
    }
    
    if (isPaused) {
      return {
        icon: <Play className="w-4 h-4" />,
        title: "Retomar reprodução",
      };
    }
    
    if (isSpeaking) {
      return {
        icon: <Pause className="w-4 h-4" />,
        title: "Pausar reprodução",
      };
    }
    
    return {
      icon: <Volume2 className="w-4 h-4" />,
      title: "Ouvir resposta",
    };
  };

  const { icon, title } = getIconAndTitle();

  // Função para alterar velocidade
  const handleSpeedChange = (rate: number) => {
    setPlaybackRate(rate);
    setShowSpeedMenu(false);
  };

  // Formatar velocidade para exibição
  const formatSpeed = (rate: number) => {
    return rate === 1.0 ? "Normal" : `${rate}x`;
  };

  return (
    <div
      className={`flex w-full mb-4 sm:mb-5 md:mb-4 lg:mb-5 animate-fade-in transition-all duration-200 px-2 sm:px-2 md:px-1 lg:px-2 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-[90%] sm:max-w-[85%] md:max-w-[80%] lg:max-w-[75%] xl:max-w-[70%] rounded-lg transition-all duration-200 hover:shadow-md ${
          isUser
            ? "bg-treq-yellow text-treq-black px-3 py-2 sm:px-4 sm:py-3"
            : message.chartData
            ? "bg-transparent border-0 shadow-none p-0 w-full max-w-full" // Máximo espaço para gráficos
            : "bg-white border border-treq-gray-200 shadow-sm px-4 py-3 sm:px-5 sm:py-4 md:px-6 md:py-5 lg:px-7 lg:py-6"
        }`}
      >
        {isUser ? (
          <p 
            className="text-sm sm:text-base font-semibold whitespace-pre-wrap leading-relaxed break-words"
            style={{
              color: "#000000", // Preto puro sempre para máximo contraste no amarelo
              WebkitFontSmoothing: "antialiased",
              MozOsxFontSmoothing: "grayscale",
            }}
          >
            {message.content}
          </p>
        ) : (
          <>
            {/* Renderizar gráfico se chartData presente */}
            {message.chartData ? (
              <Suspense fallback={<ChartLoadingSkeleton />}>
                <ChartMessage 
                  chartData={message.chartData}
                  isLoading={false}
                  error={undefined}
                />
              </Suspense>
            ) : (
              // Renderização de texto existente
              <Suspense fallback={<div className="text-sm text-treq-gray-500">Carregando...</div>}>
                <FormattedMessage content={message.content} />
              </Suspense>
            )}
          </>
        )}
        
        {!isUser && message.content && !message.chartData && (
          <div className="flex items-center gap-1.5 sm:gap-2 mt-3 sm:mt-4 pt-2 sm:pt-3 border-t border-treq-gray-100">
            <button
              onClick={handleAudioControl}
              disabled={isLoading}
              className={`p-1.5 sm:p-2 rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 hover:scale-110 active:scale-95 min-w-[36px] min-h-[36px] sm:min-w-[40px] sm:min-h-[40px] flex items-center justify-center ${
                isSpeaking || isPaused
                  ? "text-treq-info hover:bg-treq-info-light"
                  : "text-treq-gray-500 hover:text-treq-gray-700 hover:bg-treq-gray-100"
              } disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100`}
              title={title}
              aria-label={title}
            >
              {icon}
            </button>
            
            {/* Controle de Velocidade (apenas quando está tocando/pausado) */}
            {(isSpeaking || isPaused) && (
              <div className="relative">
                <button
                  onClick={() => setShowSpeedMenu(!showSpeedMenu)}
                  className="p-2 rounded-lg text-treq-gray-500 hover:text-treq-gray-700 hover:bg-treq-gray-100 transition-colors text-xs flex items-center gap-1 focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2"
                  title={`Velocidade: ${formatSpeed(playbackRate)}`}
                  aria-label={`Velocidade atual: ${formatSpeed(playbackRate)}`}
                >
                  <Gauge className="w-3 h-3" />
                  <span>{formatSpeed(playbackRate)}</span>
                </button>
                
                {/* Menu dropdown de velocidades */}
                {showSpeedMenu && (
                  <>
                    {/* Overlay para fechar menu ao clicar fora */}
                    <div 
                      className="fixed inset-0 z-10"
                      onClick={() => setShowSpeedMenu(false)}
                      aria-hidden="true"
                    />
                    <div className="absolute bottom-full left-0 mb-1 bg-white border border-treq-gray-200 rounded-lg shadow-lg z-20 min-w-[90px]">
                      {PLAYBACK_RATES.map((rate) => (
                        <button
                          key={rate}
                          onClick={() => handleSpeedChange(rate)}
                          className={`w-full text-left px-3 py-2 text-sm hover:bg-treq-gray-100 first:rounded-t-lg last:rounded-b-lg transition-colors focus:outline-none focus:bg-treq-gray-100 ${
                            playbackRate === rate
                              ? "bg-treq-info-light text-treq-info font-medium"
                              : "text-treq-gray-700"
                          }`}
                          aria-label={`Velocidade ${formatSpeed(rate)}`}
                        >
                          {formatSpeed(rate)}
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}
            
            {(isSpeaking || isPaused) && (
              <button
                onClick={stop}
                className="p-2 rounded-lg text-treq-gray-400 hover:text-treq-gray-600 hover:bg-treq-gray-100 transition-colors text-xs focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2"
                title="Parar reprodução"
                aria-label="Parar reprodução"
              >
                Parar
              </button>
            )}
          </div>
        )}
        
        {message.timestamp && (
          <p className="text-xs mt-1.5 sm:mt-2 text-treq-gray-500 opacity-75">
            {new Date(message.timestamp).toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        )}
      </div>
    </div>
  );
}
