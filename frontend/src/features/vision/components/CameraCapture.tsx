"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Camera, X, RefreshCw } from "lucide-react";
import { useCamera } from "../hooks/useCamera";

interface CameraCaptureProps {
    onCapture: (base64Image: string) => void;
    onClose: () => void;
}

export function CameraCapture({ onCapture, onClose }: CameraCaptureProps) {
    const { videoRef, canvasRef, stream, error, startCamera, stopCamera, capturePhoto } = useCamera();
    const [mounted, setMounted] = useState(false);
    const [flash, setFlash] = useState(false);

    useEffect(() => {
        setMounted(true);
        startCamera();
        return () => stopCamera();
    }, [startCamera, stopCamera]);

    const handleCapture = () => {
        setFlash(true);
        setTimeout(() => setFlash(false), 150);

        const photo = capturePhoto();
        if (photo) {
            // Pequeno delay para o usuário sentir o "clique" antes de fechar
            setTimeout(() => {
                onCapture(photo);
                onClose();
            }, 200);
        }
    };

    if (!mounted) return null;

    const modalContent = (
        <div
            className="fixed inset-0 flex items-center justify-center bg-black/95 backdrop-blur-xl px-4 py-8 md:p-10"
            style={{ zIndex: 99999 }}
        >
            <div className="relative w-full max-w-2xl bg-zinc-950 rounded-[2.5rem] overflow-hidden shadow-[0_0_80px_rgba(255,205,0,0.15)] border border-white/10 flex flex-col h-[600px] max-h-[80vh]">
                {/* Flash Effect */}
                {flash && (
                    <div className="absolute inset-0 z-[100] bg-white animate-out fade-out duration-150" />
                )}

                {/* Header - Refined spacing and colors */}
                <div className="absolute top-0 inset-x-0 z-20 flex items-center justify-between p-6 bg-gradient-to-b from-black/60 to-transparent">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-black/40 backdrop-blur-md rounded-full border border-white/10">
                            <div className="w-2 h-2 rounded-full bg-treq-yellow shadow-[0_0_8px_#FFCD00]" />
                            <span className="text-white font-bold tracking-widest text-[10px] uppercase">
                                Live
                            </span>
                        </div>
                        <span className="text-white/90 font-medium tracking-tight text-sm uppercase flex items-center gap-2">
                            <Camera className="w-4 h-4 text-treq-yellow" />
                            Assistente Vision
                        </span>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-10 h-10 flex items-center justify-center bg-white/10 hover:bg-treq-error hover:text-white rounded-full transition-all duration-300 group backdrop-blur-md border border-white/5"
                        aria-label="Fechar"
                    >
                        <X className="w-5 h-5 text-white/70 group-hover:text-white group-hover:scale-110 transition-transform" />
                    </button>
                </div>

                {/* Video Area */}
                <div className="relative flex-1 bg-black flex items-center justify-center overflow-hidden">
                    {error ? (
                        <div className="p-10 text-center max-w-sm animate-in zoom-in-95 duration-300">
                            <div className="w-20 h-20 bg-treq-error/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-treq-error/20">
                                <X className="w-10 h-10 text-treq-error" />
                            </div>
                            <h3 className="text-white text-xl font-bold mb-3">Acesso Negado</h3>
                            <p className="text-gray-400 text-sm mb-8 leading-relaxed">{error}</p>
                            <button
                                onClick={startCamera}
                                className="w-full py-4 bg-treq-yellow text-black font-extrabold rounded-2xl hover:bg-treq-yellow-dark hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-2 shadow-xl shadow-treq-yellow/10"
                            >
                                <RefreshCw className="w-5 h-5" /> Tentar Novamente
                            </button>
                        </div>
                    ) : (
                        <>
                            <video
                                ref={videoRef}
                                autoPlay
                                muted
                                playsInline
                                className="w-full h-full object-cover -scale-x-100"
                            />

                            {/* Document Guide Overlay */}
                            {stream && (
                                <div className="absolute inset-0 pointer-events-none flex items-center justify-center p-8 opacity-40">
                                    <div className="w-full h-full border-2 border-dashed border-white/30 rounded-3xl relative">
                                        <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-treq-yellow rounded-tl-xl" />
                                        <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-treq-yellow rounded-tr-xl" />
                                        <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-treq-yellow rounded-bl-xl" />
                                        <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-treq-yellow rounded-br-xl" />
                                    </div>
                                </div>
                            )}

                            {!stream && (
                                <div className="absolute inset-0 flex flex-col items-center justify-center bg-zinc-950 gap-6">
                                    <div className="relative">
                                        <div className="w-20 h-20 border-4 border-treq-yellow/10 border-t-treq-yellow rounded-full animate-spin duration-700" />
                                        <Camera className="absolute inset-0 m-auto w-8 h-8 text-treq-yellow animate-pulse" />
                                    </div>
                                    <div className="flex flex-col items-center gap-2">
                                        <div className="text-treq-yellow text-xs font-black tracking-[0.3em] uppercase">
                                            Sincronizando Sensor
                                        </div>
                                        <div className="text-white/30 text-[10px] uppercase font-medium">
                                            Aguardando permissão de hardware
                                        </div>
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Controls */}
                <div className="absolute bottom-0 inset-x-0 z-20 p-10 flex flex-col items-center bg-gradient-to-t from-black/80 to-transparent">
                    <div className="flex items-center gap-8">
                        <button
                            onClick={handleCapture}
                            disabled={!stream}
                            className="relative w-24 h-24 rounded-full bg-white flex items-center justify-center shadow-[0_0_40px_rgba(255,255,255,0.2)] hover:scale-105 active:scale-90 transition-all duration-300 disabled:opacity-20 disabled:grayscale group"
                        >
                            <div className="w-20 h-20 rounded-full border-4 border-zinc-100 group-hover:border-treq-yellow transition-colors duration-300" />
                            <div className="absolute inset-0 m-auto w-6 h-6 bg-treq-yellow rounded-full shadow-[0_0_20px_#FFCD00] scale-0 group-hover:scale-100 transition-transform duration-300" />
                        </button>
                    </div>
                    <div className="mt-6 flex flex-col items-center gap-1">
                        <p className="text-white font-bold text-[10px] uppercase tracking-[0.3em]">
                            Clique para analisar
                        </p>
                        <p className="text-white/40 text-[9px] uppercase font-medium">
                            Enquadre o documento no centro
                        </p>
                    </div>
                </div>

                {/* Hidden Canvas for capture */}
                <canvas ref={canvasRef} className="hidden" />
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
}
