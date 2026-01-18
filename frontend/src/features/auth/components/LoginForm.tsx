"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema, type LoginInput } from "../api/authSchemas";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function LoginForm() {
    const router = useRouter();
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginInput>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginInput) => {
        setIsLoading(true);
        setError(null);

        try {
            const formData = new URLSearchParams();
            formData.append("username", data.username);
            formData.append("password", data.password);

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData.toString(),
            });

            if (!response.ok) {
                throw new Error("Credenciais inválidas");
            }

            const result = await response.json();
            localStorage.setItem("treq_token", result.access_token);
            localStorage.setItem("treq_user_id", "00000000-0000-0000-0000-000000000000"); // Mock user id for now

            router.push("/chat");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Erro ao entrar");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md p-8 bg-white rounded-2xl shadow-xl border border-treq-gray-100 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex flex-col items-center mb-8">
                <div className="w-16 h-16 bg-treq-red-600 rounded-xl flex items-center justify-center mb-4 shadow-lg">
                    <span className="text-white text-3xl font-bold italic">T</span>
                </div>
                <h1 className="text-2xl font-bold text-treq-gray-900">Treq Enterprise</h1>
                <p className="text-treq-gray-500">Acesse sua conta para continuar</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-treq-gray-700 mb-1">Usuário</label>
                    <input
                        {...register("username")}
                        type="text"
                        className="w-full px-4 py-3 rounded-xl border border-treq-gray-200 focus:ring-2 focus:ring-treq-red-500 focus:border-transparent outline-none transition-all"
                        placeholder="Ex: admin"
                    />
                    {errors.username && <p className="text-red-500 text-xs mt-1">{errors.username.message}</p>}
                </div>

                <div>
                    <label className="block text-sm font-medium text-treq-gray-700 mb-1">Senha</label>
                    <input
                        {...register("password")}
                        type="password"
                        className="w-full px-4 py-3 rounded-xl border border-treq-gray-200 focus:ring-2 focus:ring-treq-red-500 focus:border-transparent outline-none transition-all"
                        placeholder="••••••••"
                    />
                    {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
                </div>

                {error && (
                    <div className="p-3 bg-red-50 border border-red-100 rounded-lg">
                        <p className="text-red-600 text-sm text-center">{error}</p>
                    </div>
                )}

                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-treq-red-600 hover:bg-treq-red-700 text-white font-semibold py-3 rounded-xl shadow-lg shadow-treq-red-200 transition-all active:scale-[0.98] disabled:opacity-50"
                >
                    {isLoading ? "Entrando..." : "Entrar"}
                </button>
            </form>
        </div>
    );
}
