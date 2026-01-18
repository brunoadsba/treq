'use client';

import { useDebugMode } from '@/contexts/DebugContext';
import { Bug, Zap, ZapOff } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function DebugToggle() {
    const { isDebugMode, toggleDebugMode } = useDebugMode();

    return (
        <motion.button
            onClick={toggleDebugMode}
            className={`
        fixed bottom-24 right-6 z-40
        p-4 rounded-full shadow-2xl border-2
        transition-all duration-500
        ${isDebugMode
                    ? 'bg-yellow-500 text-black border-yellow-400 shadow-yellow-500/50'
                    : 'bg-gray-900 text-gray-400 border-gray-800 hover:text-white hover:border-gray-700'
                }
      `}
            whileHover={{ scale: 1.1, rotate: 5 }}
            whileTap={{ scale: 0.9 }}
            title="Toggle Debug Mode (Ctrl+Shift+D)"
        >
            <AnimatePresence mode="wait">
                {isDebugMode ? (
                    <motion.div
                        key="bug-on"
                        initial={{ rotate: -90, opacity: 0 }}
                        animate={{ rotate: 0, opacity: 1 }}
                        exit={{ rotate: 90, opacity: 0 }}
                    >
                        <Zap className="w-6 h-6" />
                    </motion.div>
                ) : (
                    <motion.div
                        key="bug-off"
                        initial={{ rotate: -90, opacity: 0 }}
                        animate={{ rotate: 0, opacity: 1 }}
                        exit={{ rotate: 90, opacity: 0 }}
                    >
                        <ZapOff className="w-6 h-6" />
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Badge de atalho */}
            <span className="
        absolute -top-1 -right-1
        px-1.5 py-0.5 rounded-md
        bg-black text-white text-[8px] font-bold font-mono tracking-tighter
        shadow-sm border border-gray-800
      ">
                ⌘D
            </span>
        </motion.button>
    );
}
