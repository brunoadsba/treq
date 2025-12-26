"use client";

import { useState, useCallback, useRef, useEffect } from "react";

interface UseTTSReturn {
  speak: (text: string, language?: string) => Promise<void>;
  pause: () => void;
  resume: () => Promise<void>;
  stop: () => void;
  isSpeaking: boolean;
  isPaused: boolean;
  isLoading: boolean;
}

// Interface para cache de áudio
interface AudioCacheEntry {
  audio: HTMLAudioElement;
  timestamp: number;
}

// Tamanho máximo do cache (número de áudios armazenados)
const MAX_CACHE_SIZE = 20;

// Helper para criar hash simples do texto
function hashText(text: string, language: string): string {
  // Criar hash simples (não precisa ser criptograficamente seguro)
  let hash = 0;
  const str = `${text}_${language}`;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return `tts_${Math.abs(hash)}`;
}

export function useTTS(): UseTTSReturn {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Cache de áudio: Map<hash, AudioCacheEntry>
  const audioCacheRef = useRef<Map<string, AudioCacheEntry>>(new Map());
  
  // Referência do áudio atual sendo reproduzido
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);
  const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const currentTextRef = useRef<string>(""); // Texto atual para verificar se é o mesmo

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Limpeza periódica do cache (remove entradas antigas)
  useEffect(() => {
    const cleanupCache = () => {
      const cache = audioCacheRef.current;
      const now = Date.now();
      const CACHE_TTL = 30 * 60 * 1000; // 30 minutos
      
      // Remover entradas expiradas
      for (const [key, entry] of cache.entries()) {
        if (now - entry.timestamp > CACHE_TTL) {
          cache.delete(key);
        }
      }
      
      // Se ainda estiver muito grande, remover os mais antigos
      if (cache.size > MAX_CACHE_SIZE) {
        const entries = Array.from(cache.entries())
          .sort((a, b) => a[1].timestamp - b[1].timestamp);
        
        // Remover 20% dos mais antigos
        const toRemove = Math.ceil(entries.length * 0.2);
        for (let i = 0; i < toRemove; i++) {
          cache.delete(entries[i][0]);
        }
      }
    };
    
    // Limpar cache a cada 5 minutos
    const interval = setInterval(cleanupCache, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
      }
      if (typeof window !== "undefined" && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const speak = useCallback(
    async (text: string, language: string = "pt-BR") => {
      if (!text.trim()) return;

      // Criar hash do texto para cache
      const cacheKey = hashText(text, language);
      currentTextRef.current = text;

      // Se já está pausado e é o mesmo texto, retomar
      if (isPaused && currentAudioRef.current && currentTextRef.current === text) {
        await resume();
        return;
      }

      // Verificar cache primeiro
      const cachedEntry = audioCacheRef.current.get(cacheKey);
      if (cachedEntry) {
        console.log("✅ Áudio encontrado no cache (reutilizando)");
        
        // Parar áudio anterior se houver
        if (currentAudioRef.current && currentAudioRef.current.src !== cachedEntry.audio.src) {
          currentAudioRef.current.pause();
          currentAudioRef.current = null;
        }

        // Criar novo elemento Audio com a mesma URL (reutilizar blob URL)
        const audio = new Audio(cachedEntry.audio.src);
        currentAudioRef.current = audio;
        
        // Resetar tempo para começar do início
        audio.currentTime = 0;
        
        // Configurar event handlers
        audio.onplay = () => {
          setIsSpeaking(true);
          setIsPaused(false);
          setIsLoading(false);
        };

        audio.onpause = () => {
          setIsPaused(true);
          setIsSpeaking(false);
        };

        audio.onended = () => {
          setIsSpeaking(false);
          setIsPaused(false);
          // Não remover currentAudioRef aqui, pode ser reutilizado
        };

        audio.onerror = () => {
          setIsSpeaking(false);
          setIsPaused(false);
          setIsLoading(false);
          console.error("Erro ao reproduzir áudio do cache");
          // Tentar gerar novo áudio
          audioCacheRef.current.delete(cacheKey);
          speak(text, language); // Recursão controlada (apenas 1 nível)
        };

        try {
          setIsLoading(false);
          setIsSpeaking(false);
          await audio.play();
          return;
        } catch (error) {
          console.error("Erro ao reproduzir áudio do cache:", error);
          // Remover entrada corrompida e tentar gerar novo
          audioCacheRef.current.delete(cacheKey);
        }
      }

      // Gerar novo áudio (não está no cache)
      setIsLoading(true);
      setIsSpeaking(false);
      setIsPaused(false);

      const startTime = performance.now();

      try {
        // Tentar usar Gemini TTS primeiro
        const response = await fetch(`${apiUrl}/audio/synthesize`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text,
            language,
            voice: "Charon",
          }),
        });

        if (!response.ok) {
          throw new Error(`Erro na API: ${response.statusText}`);
        }

        const data = await response.json();

        // Se Gemini retornou áudio, usar ele
        if (data.audio_url && !data.use_web_speech) {
          // Parar áudio anterior se houver
          if (currentAudioRef.current) {
            currentAudioRef.current.pause();
            currentAudioRef.current = null;
          }

          // Decodificar base64 e criar blob
          const base64Data = data.audio_url.split(",")[1];
          const audioBlob = await fetch(`data:audio/wav;base64,${base64Data}`).then(r => r.blob());
          const audioUrl = URL.createObjectURL(audioBlob);

          // Criar novo áudio
          const audio = new Audio(audioUrl);
          currentAudioRef.current = audio;
          
          // Configurar event handlers
          audio.onplay = () => {
            setIsSpeaking(true);
            setIsPaused(false);
            setIsLoading(false);
          };

          audio.onpause = () => {
            setIsPaused(true);
            setIsSpeaking(false);
          };

          audio.onended = () => {
            setIsSpeaking(false);
            setIsPaused(false);
            // Não limpar URL aqui, pode ser reutilizado
          };

          audio.onerror = () => {
            setIsSpeaking(false);
            setIsPaused(false);
            setIsLoading(false);
            console.error("Erro ao reproduzir áudio");
            // Fallback para Web Speech API em caso de erro
            fallbackToWebSpeech(text, language);
          };

          // Salvar no cache ANTES de reproduzir (salvar URL do blob, não o elemento)
          // Criar elemento de referência para o cache (sem reproduzir)
          const cacheAudio = new Audio(audioUrl);
          audioCacheRef.current.set(cacheKey, {
            audio: cacheAudio,
            timestamp: Date.now(),
          });

          const endTime = performance.now();
          const duration = ((endTime - startTime) / 1000).toFixed(2);
          console.log(`⏱️ TTS gerado em ${duration}s (${text.length} caracteres)`);

          await audio.play();
          return;
        }

        // Fallback para Web Speech API se necessário
        fallbackToWebSpeech(text, language);
      } catch (error) {
        console.error("Erro ao sintetizar áudio:", error);
        const endTime = performance.now();
        const duration = ((endTime - startTime) / 1000).toFixed(2);
        console.log(`❌ Falha na geração de TTS após ${duration}s`);
        setIsLoading(false);
        // Fallback para Web Speech API
        fallbackToWebSpeech(text, language);
      }
    },
    [apiUrl, isPaused]
  );

  const fallbackToWebSpeech = (text: string, language: string) => {
    if (typeof window === "undefined" || !window.speechSynthesis) {
      console.warn("Web Speech API não disponível");
      setIsLoading(false);
      return;
    }

    // Parar qualquer síntese anterior
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => {
      setIsSpeaking(true);
      setIsPaused(false);
      setIsLoading(false);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setIsPaused(false);
      currentUtteranceRef.current = null;
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
      setIsPaused(false);
      setIsLoading(false);
      currentUtteranceRef.current = null;
      console.error("Erro na síntese de voz");
    };

    currentUtteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const pause = useCallback(() => {
    // Pausar áudio do Gemini se estiver tocando
    if (currentAudioRef.current && !currentAudioRef.current.paused) {
      currentAudioRef.current.pause();
      setIsPaused(true);
      setIsSpeaking(false);
    }
    // Pausar Web Speech API (não suporta pause direto, precisa cancelar)
    else if (typeof window !== "undefined" && window.speechSynthesis && isSpeaking) {
      // Web Speech API não tem pause nativo, então cancelamos
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      setIsPaused(false);
      currentUtteranceRef.current = null;
    }
  }, [isSpeaking]);

  const resume = useCallback(async () => {
    // Retomar áudio do Gemini se estiver pausado
    if (currentAudioRef.current && currentAudioRef.current.paused) {
      try {
        await currentAudioRef.current.play();
      } catch (error) {
        console.error("Erro ao retomar áudio:", error);
        setIsPaused(false);
      }
    }
    // Web Speech API não suporta resume, precisa reiniciar
    // Não fazemos nada aqui, o usuário precisa clicar em speak novamente
  }, []);

  const stop = useCallback(() => {
    // Parar áudio do Gemini
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      // Não limpar currentAudioRef aqui, pode ser reutilizado do cache
    }

    // Parar Web Speech API
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      currentUtteranceRef.current = null;
    }

    setIsSpeaking(false);
    setIsPaused(false);
    setIsLoading(false);
  }, []);

  return {
    speak,
    pause,
    resume,
    stop,
    isSpeaking,
    isPaused,
    isLoading,
  };
}
