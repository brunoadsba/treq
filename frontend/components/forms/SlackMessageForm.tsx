'use client';

import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Hash, AtSign, AlertCircle } from 'lucide-react';
import { SlackMessageFormData, slackMessageSchema, SlackPrefillData } from '@/lib/validations/slack.schema';

interface SlackMessageFormProps {
    onSubmit: (data: SlackMessageFormData) => void;
    onCancel: () => void;
    prefill?: SlackPrefillData;
    isSubmitting?: boolean;
    availableChannels?: string[];
}

export function SlackMessageForm({
    onSubmit,
    onCancel,
    prefill,
    isSubmitting = false,
    availableChannels = ['general', 'engineering', 'support', 'alerts']
}: SlackMessageFormProps) {
    const {
        register,
        handleSubmit,
        control,
        watch,
        formState: { errors, isDirty },
    } = useForm<SlackMessageFormData>({
        resolver: zodResolver(slackMessageSchema),
        defaultValues: {
            channel: prefill?.channel || '',
            text: prefill?.text || '',
            threadTs: prefill?.threadTs || '',
            mentions: prefill?.mentions || [],
        },
    });

    const messageText = watch('text');
    const characterCount = messageText?.length || 0;

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Canal */}
            <div>
                <label htmlFor="channel" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                    <Hash className="w-4 h-4" />
                    Canal *
                </label>
                <Controller
                    name="channel"
                    control={control}
                    render={({ field }) => (
                        <div className="relative">
                            <select
                                {...field}
                                className={`
                  w-full px-4 py-3 rounded-lg border-2
                  focus:outline-none focus:ring-2 focus:ring-yellow-500
                  dark:bg-gray-800 dark:text-white appearance-none
                  ${errors.channel
                                        ? 'border-red-500'
                                        : 'border-gray-300 dark:border-gray-700'
                                    }
                `}
                            >
                                <option value="">Selecione um canal</option>
                                {availableChannels.map((channel) => (
                                    <option key={channel} value={channel}>
                                        #{channel}
                                    </option>
                                ))}
                            </select>
                            <Hash className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                        </div>
                    )}
                />
                {errors.channel && (
                    <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="w-4 h-4" />
                        {errors.channel.message}
                    </p>
                )}
            </div>

            {/* Mensagem */}
            <div>
                <div className="flex items-center justify-between mb-2">
                    <label htmlFor="text" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Mensagem *
                    </label>
                    <span className={`text-xs ${characterCount > 3500 ? 'text-red-600' : 'text-gray-500'}`}>
                        {characterCount} / 4000
                    </span>
                </div>
                <textarea
                    id="text"
                    {...register('text')}
                    rows={6}
                    className={`
            w-full px-4 py-3 rounded-lg border-2
            focus:outline-none focus:ring-2 focus:ring-yellow-500
            dark:bg-gray-800 dark:text-white font-mono text-sm
            ${errors.text
                            ? 'border-red-500'
                            : 'border-gray-300 dark:border-gray-700'
                        }
          `}
                    placeholder="Digite sua mensagem aqui..."
                />
                {errors.text && (
                    <p className="mt-1 text-sm text-red-600">{errors.text.message}</p>
                )}

                {/* Preview Simples */}
                {messageText && (
                    <div className="mt-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Preview:</p>
                        <div className="text-sm prose dark:prose-invert max-w-none whitespace-pre-wrap">
                            {messageText}
                        </div>
                    </div>
                )}
            </div>

            {/* Botões */}
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-800">
                <button
                    type="button"
                    onClick={onCancel}
                    disabled={isSubmitting}
                    className="
            px-6 py-2.5 rounded-lg border-2 border-gray-300
            text-gray-700 font-medium
            hover:bg-gray-50 dark:hover:bg-gray-800
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors
          "
                >
                    Cancelar
                </button>

                <button
                    type="submit"
                    disabled={isSubmitting || !isDirty}
                    className="
            px-6 py-2.5 rounded-lg
            bg-yellow-500 text-black font-medium
            hover:bg-yellow-600
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all
            flex items-center justify-center min-w-[120px] gap-2
          "
                >
                    {isSubmitting ? (
                        <>
                            <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                            Enviando...
                        </>
                    ) : (
                        'Enviar Mensagem'
                    )}
                </button>
            </div>
        </form>
    );
}
