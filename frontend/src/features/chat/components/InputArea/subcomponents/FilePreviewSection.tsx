"use client";

import React from "react";
import { Paperclip, X } from "lucide-react";
import { useHighContrast } from "@/hooks/useHighContrast";

interface FilePreviewSectionProps {
    attachedFile: File | null;
    cameraPreview: string | null;
    onRemove: () => void;
}

export function FilePreviewSection({
    attachedFile,
    cameraPreview,
    onRemove,
}: FilePreviewSectionProps) {
    const isHighContrast = useHighContrast();

    if (!attachedFile) return null;

    return (
        <div
            className={`px-4 py-3 border-b flex items-center justify-between animate-fade-in ${isHighContrast
                    ? "bg-treq-yellow-dark border-treq-yellow"
                    : "bg-treq-info-light border-treq-info"
                }`}
        >
            <div className="flex items-center gap-3 flex-1 min-w-0">
                <div
                    className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center overflow-hidden ${isHighContrast ? "bg-treq-yellow" : "bg-treq-info"
                        }`}
                >
                    {cameraPreview ? (
                        <img
                            src={cameraPreview}
                            alt="Preview"
                            className="w-full h-full object-cover"
                        />
                    ) : (
                        <Paperclip
                            className={`w-5 h-5 ${isHighContrast ? "text-black" : "text-white"}`}
                        />
                    )}
                </div>
                <div className="flex-1 min-w-0">
                    <p
                        className={`text-sm font-medium truncate ${isHighContrast ? "text-black" : "text-treq-info-dark"
                            }`}
                    >
                        {attachedFile.name}
                    </p>
                    <p
                        className={`text-xs ${isHighContrast ? "text-black/70" : "text-treq-info-dark/70"
                            }`}
                    >
                        {(attachedFile.size / 1024).toFixed(1)} KB
                    </p>
                </div>
            </div>
            <button
                onClick={onRemove}
                className={`flex-shrink-0 ml-2 p-1.5 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-treq-yellow focus:ring-offset-2 ${isHighContrast
                        ? "text-black hover:bg-treq-yellow-light"
                        : "text-treq-info-dark hover:bg-treq-info"
                    }`}
                aria-label="Remover arquivo anexado"
            >
                <X className="w-5 h-5" />
            </button>
        </div>
    );
}
