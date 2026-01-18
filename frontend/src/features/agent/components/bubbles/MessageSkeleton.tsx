interface MessageSkeletonProps {
    variant?: 'text' | 'card' | 'list';
}

export function MessageSkeleton({ variant = 'text' }: MessageSkeletonProps) {
    return (
        <div className="flex justify-start mb-6 animate-in fade-in duration-500 px-2 sm:px-2 md:px-1 lg:px-2">
            <div className="bg-white dark:bg-gray-900 rounded-lg px-4 py-3 sm:px-5 sm:py-4 border border-treq-gray-100 dark:border-gray-800 shadow-sm transition-all duration-300 w-full max-w-lg">
                <div className="flex flex-col gap-3">
                    {variant === 'text' && (
                        <>
                            <div className="h-4 bg-treq-gray-100 dark:bg-gray-800 rounded w-3/4 animate-pulse"></div>
                            <div className="h-4 bg-treq-gray-100 dark:bg-gray-800 rounded w-1/2 animate-pulse"></div>
                            <div className="h-4 bg-treq-gray-100 dark:bg-gray-800 rounded w-5/6 animate-pulse"></div>
                        </>
                    )}
                    {variant === 'card' && (
                        <>
                            <div className="h-6 bg-treq-gray-100 dark:bg-gray-800 rounded w-1/2 animate-pulse mb-1"></div>
                            <div className="h-20 bg-treq-gray-50 dark:bg-gray-800/50 rounded w-full animate-pulse"></div>
                        </>
                    )}
                    {variant === 'list' && (
                        <div className="space-y-4">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="flex gap-3 items-center">
                                    <div className="w-2 h-2 rounded-full bg-treq-gray-100 dark:bg-gray-800 animate-pulse"></div>
                                    <div className="h-4 bg-treq-gray-100 dark:bg-gray-800 rounded w-full animate-pulse"></div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
