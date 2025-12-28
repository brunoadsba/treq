"use client";

import { useState, useCallback } from "react";

export interface UseDocumentUploadReturn {
  isUploading: boolean;
  error: string | null;
  uploadDocument: (file: File, documentType?: string) => Promise<{ success: boolean; chunksIndexed: number; message: string }>;
}

export function useDocumentUpload(): UseDocumentUploadReturn {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const uploadDocument = useCallback(
    async (file: File, documentType?: string): Promise<{ success: boolean; chunksIndexed: number; message: string }> => {
      setIsUploading(true);
      setError(null);

      try {
        const formData = new FormData();
        formData.append("file", file);
        if (documentType) {
          formData.append("document_type", documentType);
        }

        const response = await fetch(`${apiUrl}/documents/upload`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: response.statusText }));
          throw new Error(errorData.detail || "Erro ao fazer upload do documento");
        }

        const data = await response.json();
        
        if (!data.success) {
          throw new Error(data.message || "Upload falhou");
        }

        return {
          success: true,
          chunksIndexed: data.chunks_indexed || 0,
          message: data.message || "Documento enviado com sucesso",
        };
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Erro desconhecido";
        setError(errorMessage);
        throw err;
      } finally {
        setIsUploading(false);
      }
    },
    [apiUrl]
  );

  return {
    isUploading,
    error,
    uploadDocument,
  };
}

