

interface UserBubbleProps {
    content: string;
}

export function UserBubble({ content }: UserBubbleProps) {
    return (
        <div className="flex justify-end mb-4 animate-in fade-in slide-in-from-bottom-2 px-2 sm:px-2 md:px-1 lg:px-2">
            <div className="max-w-[90%] sm:max-w-[85%] md:max-w-[80%] lg:max-w-[75%] xl:max-w-[70%] rounded-lg bg-treq-yellow text-treq-black px-3 py-2 sm:px-4 sm:py-3 shadow-sm hover:shadow-treq-yellow/20 transition-all duration-300">
                <p className="text-sm sm:text-base font-semibold whitespace-pre-wrap leading-relaxed break-words"
                    style={{
                        color: "#000000",
                        WebkitFontSmoothing: "antialiased",
                        MozOsxFontSmoothing: "grayscale",
                    }}>
                    {content}
                </p>
            </div>
        </div>
    );
}
