"use client";

/**
 * Ações para a feature de visão computacional.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

export async function uploadVisionImage(file: File, prompt?: string) {
    const formData = new FormData();
    formData.append("file", file);
    if (prompt) formData.append("prompt", prompt);

    const response = await fetch(`${API_URL}/vision/upload-multimodal`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error("Falha no upload multimodal");
    }

    return response.json();
}

export async function analyzeCameraCapture(base64Image: string, prompt?: string) {
    const response = await fetch(`${API_URL}/vision/analyze-webcam`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            base64_image: { image: base64Image },
            prompt: prompt,
        }),
    });

    if (!response.ok) {
        throw new Error("Falha na análise da captura");
    }

    return response.json();
}

/**
 * Utilitário para converter base64 em arquivo
 */
export function base64ToFile(base64: string, filename: string): File {
    const arr = base64.split(",");
    const mime = arr[0].match(/:(.*?);/)?.[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
}
