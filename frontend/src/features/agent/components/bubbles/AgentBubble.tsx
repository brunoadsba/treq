import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

import { ToolOutput } from '../../types';
import { JiraCard } from '../tools/JiraCard';
import { SlackCard } from '../tools/SlackCard';

interface AgentBubbleProps {
    content: string;
    toolsUsed?: ToolOutput[];
}

export function AgentBubble({ content, toolsUsed }: AgentBubbleProps) {
    return (
        <div data-testid="agent-bubble" className="flex justify-start mb-6 animate-in fade-in slide-in-from-bottom-2 px-2 sm:px-2 md:px-1 lg:px-2">
            <div className="max-w-[90%] sm:max-w-[85%] md:max-w-[80%] lg:max-w-[75%] xl:max-w-[70%] rounded-lg bg-white border border-treq-gray-200 shadow-sm px-4 py-3 sm:px-5 sm:py-4 md:px-6 md:py-5 lg:px-7 lg:py-6 transition-all duration-300 hover:shadow-lg dark:bg-gray-900 dark:border-gray-800">
                {/* Content Card */}
                <div className="prose prose-sm max-w-none prose-p:my-1.5 prose-headings:text-gray-900 dark:prose-headings:text-gray-100 dark:prose-p:text-gray-300">
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkBreaks]}
                    >
                        {content}
                    </ReactMarkdown>
                </div>

                {/* Tools Section */}
                {toolsUsed && toolsUsed.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 space-y-2 animate-in fade-in slide-in-from-top-1">
                        {toolsUsed.map((tool, idx) => {
                            if (tool.tool === 'jira_create_ticket') {
                                return <JiraCard key={idx} output={tool} />;
                            }
                            if (tool.tool === 'slack_notify') {
                                return <SlackCard key={idx} output={tool} />;
                            }
                            // Fallback for unknown tools
                            return (
                                <div key={idx} className="text-xs text-gray-500 bg-gray-50 dark:bg-gray-800 px-3 py-2 rounded-lg border border-gray-100 dark:border-gray-700">
                                    🛠️ Executou: {tool.tool}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
