'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface DebugContextType {
    isDebugMode: boolean;
    toggleDebugMode: () => void;
    showTimeline: boolean;
    setShowTimeline: (show: boolean) => void;
    expandedNodes: Set<string>;
    toggleNode: (nodeId: string) => void;
}

const DebugContext = createContext<DebugContextType | undefined>(undefined);

export function DebugProvider({ children }: { children: ReactNode }) {
    const [isDebugMode, setIsDebugMode] = useState(false);
    const [showTimeline, setShowTimeline] = useState(true);
    const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

    // Carregar preferência do localStorage
    useEffect(() => {
        const saved = localStorage.getItem('treq-debug-mode');
        if (saved === 'true') {
            setIsDebugMode(true);
        }
    }, []);

    // Salvar preferência
    useEffect(() => {
        localStorage.setItem('treq-debug-mode', String(isDebugMode));
    }, [isDebugMode]);

    // Atalho de teclado: Ctrl+Shift+D
    useEffect(() => {
        const handleKeyPress = (e: KeyboardEvent) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                setIsDebugMode((prev) => !prev);
            }
        };

        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, []);

    const toggleDebugMode = () => setIsDebugMode((prev) => !prev);

    const toggleNode = (nodeId: string) => {
        setExpandedNodes((prev) => {
            const next = new Set(prev);
            if (next.has(nodeId)) {
                next.delete(nodeId);
            } else {
                next.add(nodeId);
            }
            return next;
        });
    };

    return (
        <DebugContext.Provider
            value={{
                isDebugMode,
                toggleDebugMode,
                showTimeline,
                setShowTimeline,
                expandedNodes,
                toggleNode,
            }}
        >
            {children}
        </DebugContext.Provider>
    );
}

export function useDebugMode() {
    const context = useContext(DebugContext);
    if (!context) {
        throw new Error('useDebugMode must be used within DebugProvider');
    }
    return context;
}
