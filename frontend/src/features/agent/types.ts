export interface ToolOutput {
    tool: 'jira_create_ticket' | 'slack_notify';
    result: Record<string, any>;
}

export interface AgentMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    toolsUsed?: ToolOutput[];
}

export interface AgentState {
    messages: AgentMessage[];
    isLoading: boolean;
    error: string | null;
}

// API Contracts matching Backend
export interface AgentChatRequest {
    query: string;
    user_id: string;
}

export interface AgentChatResponse {
    response: string;
    tools_used: string[];
    tool_outputs: ToolOutput[];
    thread_id: string;
    flow: string[];
    context_count: number;
}
