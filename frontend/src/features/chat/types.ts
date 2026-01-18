export interface ChartData {
    type: "bar_chart" | "pie_chart" | "line_chart";
    title: string;
    subtitle?: string;
    data: {
        labels: string[];
        datasets: Array<{
            label: string;
            data: number[];
            backgroundColor?: string | string[];
            borderColor?: string | string[];
            borderWidth?: number;
            type?: "line" | "bar";
            tension?: number;
        }>;
    };
    options?: {
        responsive?: boolean;
        maintainAspectRatio?: boolean;
        scales?: any;
        plugins?: any;
    };
    metadata?: {
        period?: string;
        unit?: string;
        total_alerts?: number;
        last_updated?: string;
        empty?: boolean;
        message?: string;
    };
}

export interface ReasoningPlan {
    intent: string;
    context_status: string;
    context_analysis: string;
    missing_info: string[];
    strategy: string;
    needs_visualization: boolean;
    visualization_type: string | null;
    reasoning_steps: string[];
    key_entities: string[];
}

export interface ChatMessage {
    id?: string;
    role: "user" | "assistant" | "system";
    content: string;
    timestamp?: string | Date;
    chartData?: ChartData;
    reasoning?: ReasoningPlan;
    runId?: string;
    isThinking?: boolean;
    thinkingDuration?: number;
    imageUrl?: string;
}

export interface ChatResponse {
    response: string;
    conversation_id?: string;
    context_summary: string;
    sources: Array<{
        content: string;
        similarity: number;
        metadata: Record<string, any>;
    }>;
    fallback?: boolean;
    fallback_reason?: string;
    fallback_message?: string;
    chart_data?: ChartData;
    reasoning?: ReasoningPlan;
    run_id?: string;
}

export interface SavedConversation {
    id: string;
    title: string;
    messages: ChatMessage[];
    conversationId: string | null;
    createdAt: string;
    updatedAt: string;
}
