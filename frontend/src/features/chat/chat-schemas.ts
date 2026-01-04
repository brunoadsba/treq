import { z } from "zod";

export const MessageSchema = z.object({
    id: z.string().uuid().optional(),
    role: z.enum(["user", "assistant", "system"]),
    content: z.string().min(1),
    timestamp: z.date().optional(),
});

export const ChatInputSchema = z.object({
    message: z.string().min(1).max(2000),
    history: z.array(MessageSchema).optional(),
});

export const ChatResponseSchema = z.object({
    success: z.boolean(),
    message: z.string().optional(),
    data: z.object({
        content: z.string(),
        suggestions: z.array(z.string()).optional(),
    }).optional(),
});

export type Message = z.infer<typeof MessageSchema>;
export type ChatInput = z.infer<typeof ChatInputSchema>;
export type ChatResponse = z.infer<typeof ChatResponseSchema>;
