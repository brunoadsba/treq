"use client";

import { useState, useRef, useCallback } from "react";

// Helper para logging (substituindo o logger do backend se necessário ou usando console)
const logger = {
    info: (...args: any[]) => console.log("[Vision-Camera]", ...args),
    warn: (...args: any[]) => console.warn("[Vision-Camera]", ...args),
    error: (...args: any[]) => console.error("[Vision-Camera]", ...args),
};

export function useCamera() {
    const [stream, setStream] = useState<MediaStream | null>(null);
    const [error, setError] = useState<string | null>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const isStarting = useRef(false);
    const activeStreamRef = useRef<MediaStream | null>(null);

    const startCamera = useCallback(async () => {
        if (isStarting.current || activeStreamRef.current) return;

        try {
            isStarting.current = true;
            setError(null);
            logger.info("Iniciando acesso à câmera...");

            let mediaStream: MediaStream;
            try {
                mediaStream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
                    audio: false,
                });
            } catch (err) {
                logger.warn("Falha ao abrir câmera traseira, tentando qualquer câmera...");
                mediaStream = await navigator.mediaDevices.getUserMedia({
                    video: true,
                    audio: false,
                });
            }

            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
                try {
                    await videoRef.current.play();
                } catch (e) {
                    if ((e as Error).name !== 'AbortError') {
                        logger.error("Erro ao dar play no vídeo:", e);
                    }
                }
            }

            activeStreamRef.current = mediaStream;
            setStream(mediaStream);
            logger.info("Câmera iniciada com sucesso.");
        } catch (err) {
            console.error("Erro ao acessar câmera:", err);
            const msg = err instanceof Error ? err.message : "Erro desconhecido";
            setError(`Não foi possível acessar a câmera: ${msg}. Verifique as permissões.`);
        } finally {
            isStarting.current = false;
        }
    }, []);

    const stopCamera = useCallback(() => {
        if (activeStreamRef.current) {
            activeStreamRef.current.getTracks().forEach(track => track.stop());
            activeStreamRef.current = null;
            logger.info("Câmera interrompida.");
        }
        setStream(null);
    }, []);

    const capturePhoto = useCallback(() => {
        if (!videoRef.current || !canvasRef.current) return null;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const context = canvas.getContext("2d");
        if (context) {
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            return canvas.toDataURL("image/jpeg", 0.8);
        }
        return null;
    }, []);

    return {
        videoRef,
        canvasRef,
        stream,
        error,
        startCamera,
        stopCamera,
        capturePhoto,
    };
}
