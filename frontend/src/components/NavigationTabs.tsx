"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export function NavigationTabs() {
    const pathname = usePathname();

    const isActive = (path: string) => {
        // Root é considerado Chat Unificado
        if (pathname === "/" && path === "/chat-unified") return true;
        // Exact match
        if (pathname === path) return true;
        // Prefix match
        if (path !== "/" && pathname?.startsWith(path + "/")) return true;
        return false;
    };

    return (
        <nav className="flex items-center justify-center bg-treq-gray-100 dark:bg-treq-gray-800 rounded-lg p-1 mx-4 h-9" aria-label="Navegação principal">
        </nav>
    );
}
