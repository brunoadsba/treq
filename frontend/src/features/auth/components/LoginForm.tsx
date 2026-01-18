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
        <div className="w-full max-w-md p-8 bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-treq-gray-100 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col items-center mb-10">
                <div className="w-20 h-20 bg-treq-yellow rounded-2xl flex items-center justify-center mb-6 shadow-xl shadow-treq-yellow/20 rotate-3 hover:rotate-0 transition-transform duration-300">
                    <span className="text-treq-black text-4xl font-black">T</span>
                </div>
                <h1 className="text-3xl font-black text-treq-black tracking-tighter">Treq</h1>
                <p className="text-treq-gray-500 font-medium">Acesse sua conta para continuar</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <div>
                    <label className="block text-sm font-bold text-treq-gray-700 mb-2 uppercase tracking-widest">Usuário</label>
                    <input
                        {...register("username")}
                        type="text"
                        className="w-full px-5 py-4 rounded-2xl border-2 border-treq-gray-100 focus:border-treq-yellow outline-none transition-all bg-treq-gray-50/50 focus:bg-white text-treq-black placeholder:text-treq-gray-400"
                        placeholder="admin"
                    />
                    {errors.username && <p className="text-treq-error text-xs mt-2 font-semibold">{errors.username.message}</p>}
                </div>

                <div>
                    <label className="block text-sm font-bold text-treq-gray-700 mb-2 uppercase tracking-widest">Senha</label>
                    <input
                        {...register("password")}
                        type="password"
                        className="w-full px-5 py-4 rounded-2xl border-2 border-treq-gray-100 focus:border-treq-yellow outline-none transition-all bg-treq-gray-50/50 focus:bg-white text-treq-black placeholder:text-treq-gray-400"
                        placeholder="••••••••"
                    />
                    {errors.password && <p className="text-treq-error text-xs mt-2 font-semibold">{errors.password.message}</p>}
                </div>

                {error && (
                    <div className="p-4 bg-treq-error-light border border-treq-error/20 rounded-2xl flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-treq-error animate-pulse" />
                        <p className="text-treq-error-dark text-sm font-bold">{error}</p>
                    </div>
                )}

                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-treq-black hover:bg-treq-gray-900 text-treq-yellow font-black py-4 rounded-2xl shadow-xl shadow-treq-black/10 transition-all active:scale-[0.97] disabled:opacity-50 flex items-center justify-center gap-2 group"
                >
                    {isLoading ? (
                        <div className="w-5 h-5 border-3 border-treq-yellow/30 border-t-treq-yellow rounded-full animate-spin" />
                    ) : (
                        <>
                            <span>Entrar</span>
                            <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                            </svg>
                        </>
                    )}
                </button>
            </form>
        </div>
    );
}
