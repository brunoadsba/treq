'use client';

import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Calendar, Tag, User, AlertCircle } from 'lucide-react';
import { JiraTaskFormData, jiraTaskSchema, JiraPrefillData } from '@/lib/validations/jira.schema';

interface JiraTaskFormProps {
    onSubmit: (data: JiraTaskFormData) => void;
    onCancel: () => void;
    prefill?: JiraPrefillData;
    isSubmitting?: boolean;
}

const priorityColors: Record<string, string> = {
    Highest: 'bg-red-100 text-red-800 border-red-300',
    High: 'bg-orange-100 text-orange-800 border-orange-300',
    Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    Low: 'bg-blue-100 text-blue-800 border-blue-300',
    Lowest: 'bg-gray-100 text-gray-800 border-gray-300',
};

export function JiraTaskForm({
    onSubmit,
    onCancel,
    prefill,
    isSubmitting = false
}: JiraTaskFormProps) {
    const {
        register,
        handleSubmit,
        control,
        watch,
        formState: { errors, isDirty },
    } = useForm<JiraTaskFormData>({
        resolver: zodResolver(jiraTaskSchema),
        defaultValues: {
            summary: prefill?.summary || '',
            description: prefill?.description || '',
            priority: prefill?.priority || 'Medium',
            assignee: prefill?.assignee || '',
            dueDate: prefill?.dueDate || '',
            labels: prefill?.labels || [],
            issueType: prefill?.issueType || 'Task',
        },
    });

    const selectedPriority = watch('priority');

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Tipo de Issue */}
            <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Tipo de Issue
                </label>
                <Controller
                    name="issueType"
                    control={control}
                    render={({ field }) => (
                        <div className="flex flex-wrap gap-2">
                            {(['Task', 'Bug', 'Story', 'Epic'] as const).map((type) => (
                                <button
                                    key={type}
                                    type="button"
                                    onClick={() => field.onChange(type)}
                                    className={`
                    px-4 py-2 rounded-lg border-2 text-sm font-medium transition-all
                    ${field.value === type
                                            ? 'border-yellow-500 bg-yellow-50 text-yellow-900 dark:bg-yellow-900/20 dark:text-yellow-300'
                                            : 'border-gray-300 text-gray-700 hover:border-gray-400 dark:border-gray-700 dark:text-gray-300'
                                        }
                  `}
                                >
                                    {type}
                                </button>
                            ))}
                        </div>
                    )}
                />
            </div>

            {/* Título */}
            <div>
                <label htmlFor="summary" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Título da Task *
                </label>
                <input
                    id="summary"
                    type="text"
                    {...register('summary')}
                    className={`
            w-full px-4 py-3 rounded-lg border-2
            focus:outline-none focus:ring-2 focus:ring-yellow-500
            dark:bg-gray-800 dark:text-white
            ${errors.summary
                            ? 'border-red-500'
                            : 'border-gray-300 dark:border-gray-700'
                        }
          `}
                    placeholder="Ex: Implementar autenticação OAuth"
                />
                {errors.summary && (
                    <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="w-4 h-4" />
                        {errors.summary.message}
                    </p>
                )}
            </div>

            {/* Descrição */}
            <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Descrição
                </label>
                <textarea
                    id="description"
                    {...register('description')}
                    rows={4}
                    className={`
            w-full px-4 py-3 rounded-lg border-2
            focus:outline-none focus:ring-2 focus:ring-yellow-500
            dark:bg-gray-800 dark:text-white
            ${errors.description
                            ? 'border-red-500'
                            : 'border-gray-300 dark:border-gray-700'
                        }
          `}
                    placeholder="Descreva a tarefa em detalhes..."
                />
                {errors.description && (
                    <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                )}
            </div>

            {/* Grid de campos menores */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Prioridade */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Prioridade *
                    </label>
                    <Controller
                        name="priority"
                        control={control}
                        render={({ field }) => (
                            <select
                                {...field}
                                className={`
                  w-full px-4 py-3 rounded-lg border-2
                  focus:outline-none focus:ring-2 focus:ring-yellow-500
                  dark:bg-gray-800 dark:text-white
                  ${priorityColors[field.value]}
                `}
                            >
                                <option value="Highest">🔴 Highest</option>
                                <option value="High">🟠 High</option>
                                <option value="Medium">🟡 Medium</option>
                                <option value="Low">🔵 Low</option>
                                <option value="Lowest">⚪ Lowest</option>
                            </select>
                        )}
                    />
                </div>

                {/* Data de vencimento */}
                <div>
                    <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        Vencimento
                    </label>
                    <input
                        id="dueDate"
                        type="date"
                        {...register('dueDate')}
                        className="
              w-full px-4 py-3 rounded-lg border-2 border-gray-300
              dark:border-gray-700 dark:bg-gray-800 dark:text-white
              focus:outline-none focus:ring-2 focus:ring-yellow-500
            "
                    />
                    {errors.dueDate && (
                        <p className="mt-1 text-sm text-red-600">{errors.dueDate.message}</p>
                    )}
                </div>
            </div>

            {/* Botões de ação */}
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
                            Criando...
                        </>
                    ) : (
                        'Criar Task'
                    )}
                </button>
            </div>
        </form>
    );
}
