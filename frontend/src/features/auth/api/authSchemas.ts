import { z } from "zod";

export const loginSchema = z.object({
    username: z.string().min(1, "Usuário é obrigatório"),
    password: z.string().min(6, "Senha deve ter pelo menos 6 caracteres"),
});

export type LoginInput = z.infer<typeof loginSchema>;
