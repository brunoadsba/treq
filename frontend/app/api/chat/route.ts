import { env } from "@/src/env.mjs";
import { createOpenAI } from "@ai-sdk/openai";
import { streamText } from "ai";
import { ChatInputSchema } from "@/src/features/chat/chat-schemas";

const zhipu = createOpenAI({
    apiKey: env.ZHIPU_API_KEY,
    baseURL: "https://open.bigmodel.cn/api/paas/v4/",
});

export const runtime = "edge";

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const result = ChatInputSchema.safeParse(body);

        if (!result.success) {
            return new Response(JSON.stringify({ error: "Input inválido" }), { status: 400 });
        }

        const { message, history = [] } = result.data;

        const streamResult = streamText({
            model: zhipu("glm-4"),
            messages: [
                { role: "system", content: "Você é o Assistente Operacional do Treq. Responda de forma direta, técnica e profissional, focada na resolução de problemas operacionais." },
                ...history.map((m: any) => ({
                    role: m.role as "user" | "assistant" | "system",
                    content: m.content,
                })),
                { role: "user", content: message },
            ],
        });

        return streamResult.toTextStreamResponse();
    } catch (error) {
        console.error("Erro no chat route:", error);
        return new Response(JSON.stringify({ error: "Falha ao processar mensagem" }), { status: 500 });
    }
}
