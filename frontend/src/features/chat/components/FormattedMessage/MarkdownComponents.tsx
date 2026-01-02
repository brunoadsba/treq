"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { CheckCircle2, AlertTriangle, XCircle, Lightbulb, BarChart2 } from "lucide-react";
import { extractText } from "../../utils/message-parser";

interface MarkdownComponentsProps {
    isHighContrast: boolean;
}

export const getMarkdownComponents = ({ isHighContrast }: MarkdownComponentsProps) => ({
    h2: ({ children }: any) => {
        const text = extractText(children);
        if (text.includes("Status:")) {
            return (
                <h2 className="text-base sm:text-lg md:text-xl font-bold mb-4 sm:mb-5 md:mb-6 text-treq-gray-900 flex items-center gap-2 pb-3 sm:pb-4 border-b-2 border-gray-300 leading-tight">
                    {children}
                </h2>
            );
        }
        return (
            <h2 className="text-base sm:text-lg md:text-xl font-bold mb-4 sm:mb-5 md:mb-6 mt-6 sm:mt-7 md:mt-8 text-treq-gray-900 first:mt-0 leading-tight">
                {children}
            </h2>
        );
    },
    h3: ({ children }: any) => (
        <h3 className="text-[15px] sm:text-base md:text-lg font-semibold mb-3 sm:mb-4 md:mb-5 mt-5 sm:mt-6 md:mt-7 text-treq-gray-900 leading-tight">
            {children}
        </h3>
    ),
    p: ({ children }: any) => {
        const text = extractText(children);

        // Status / Alertas
        if (text.match(/^(✅|⚠️|🔴)/)) {
            const isOK = text.includes("✅");
            const isWarning = text.includes("⚠️");
            const isCritical = text.includes("🔴");

            return (
                <div className={`inline-flex items-center gap-2 px-2 sm:px-3 py-1 sm:py-1.5 rounded-md font-semibold text-sm sm:text-base mb-3 sm:mb-4 md:mb-5 ${isOK ? "bg-green-50 text-green-700 border border-green-300" :
                    isWarning ? "bg-yellow-50 text-yellow-700 border border-yellow-300" :
                        isCritical ? "bg-red-50 text-red-700 border border-red-300" :
                            "bg-gray-50 text-gray-700 border border-gray-300"
                    }`}>
                    {isOK && <CheckCircle2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-green-600" />}
                    {isWarning && <AlertTriangle className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-yellow-600" />}
                    {isCritical && <XCircle className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-red-600" />}
                    <span>{text.replace(/^(✅|⚠️|🔴)\s*/, "")}</span>
                </div>
            );
        }

        return (
            <p className="text-[15px] sm:text-base md:text-[16px] lg:text-[17px] text-treq-gray-900 leading-[1.75] sm:leading-[1.8] md:leading-[1.85] mb-4 sm:mb-5 md:mb-6 last:mb-0 tracking-tight sm:tracking-normal text-justify">
                {children}
            </p>
        );
    },
    ul: ({ children }: any) => (
        <ul className="list-none space-y-3 sm:space-y-4 my-5 sm:my-6">
            {children}
        </ul>
    ),
    li: ({ children }: any) => {
        const text = extractText(children);
        const hasBullet = text.startsWith("•") || text.match(/^\*\*/);

        if (hasBullet) {
            const cleanedText = text.replace(/^•\s*/, "").trim();
            return (
                <li className="flex items-start gap-3 sm:gap-3.5 text-[15px] sm:text-base text-treq-gray-900 mb-3 sm:mb-4">
                    <span className="text-treq-yellow-dark mt-[2px] flex-shrink-0 font-bold text-lg">•</span>
                    <span className="flex-1 text-justify">{cleanedText || children}</span>
                </li>
            );
        }
        return (
            <li className="text-[15px] sm:text-base text-treq-gray-900 pl-3 mb-3 text-justify">
                {children}
            </li>
        );
    },
    strong: ({ children }: any) => (
        <strong className="font-bold text-treq-gray-900">{children}</strong>
    ),
    code: ({ children }: any) => (
        <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono text-gray-800">{children}</code>
    ),
    pre: ({ children }: any) => (
        <pre className="bg-gray-100 p-2 rounded-lg overflow-x-auto my-2 text-xs font-mono">{children}</pre>
    ),
});
