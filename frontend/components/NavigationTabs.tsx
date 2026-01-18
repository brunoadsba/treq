"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export function NavigationTabs() {
    const pathname = usePathname();

    const isActive = (path: string) => {
        // Root é considerado Chat
        if (pathname === "/" && path === "/chat") return true;

        // Exact match
        if (pathname === path) return true;

        // Prefix match (mas evita match parcial incorreto ex: /chat-bot match /chat)
        if (path !== "/" && pathname?.startsWith(path + "/")) return true;

        return false;
    };

    return (
        <nav className="flex items-center justify-center bg-treq-gray-100 dark:bg-treq-gray-800 rounded-lg p-1 mx-4 h-9" aria-label="Navegação principal">
            <Link
                href="/chat"
                className={cn(
                    "px-4 py-1.5 rounded-md text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-treq-yellow flex items-center h-full border-b-2",
                    isActive("/chat")
                        ? "bg-white dark:bg-black text-treq-black dark:text-white shadow-sm border-treq-yellow"
                        : "text-treq-gray-600 dark:text-treq-gray-400 hover:text-treq-black dark:hover:text-white border-transparent"
                )}
                aria-current={isActive("/chat") ? "page" : undefined}
            >
                Chat
            </Link>
            <Link
                href="/agent"
                className={cn(
                    "px-4 py-1.5 rounded-md text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-treq-yellow flex items-center h-full relative border-b-2",
                    isActive("/agent")
                        ? "bg-white dark:bg-black text-treq-black dark:text-white shadow-sm border-treq-yellow"
                        : "text-treq-gray-600 dark:text-treq-gray-400 hover:text-treq-black dark:hover:text-white border-transparent"
                )}
                aria-current={isActive("/agent") ? "page" : undefined}
            >
                Agente
                {/* Badge de Estado do Agente (Simulação de Atividade) */}
                <span className="absolute -top-1 -right-0.5 flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-treq-yellow opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-treq-yellow shadow-sm shadow-treq-yellow/20"></span>
                </span>
            </Link>
        </nav>
    );
}
