'use client';

import { useState } from 'react';
import { BaseModal } from './BaseModal';
import { JiraTaskForm } from '../forms/JiraTaskForm';
import { JiraTaskFormData, JiraPrefillData } from '@/lib/validations/jira.schema';
import { useToolAction } from '@/hooks/useToolAction';
import { CheckCircle2, AlertCircle, ExternalLink } from 'lucide-react';

interface JiraTaskModalProps {
    isOpen: boolean;
    onClose: () => void;
    prefill?: JiraPrefillData;
    threadId?: string;
}

export function JiraTaskModal({
    isOpen,
    onClose,
    prefill,
    threadId
}: JiraTaskModalProps) {
    const { executeAction, isLoading, error } = useToolAction();
    const [createdTask, setCreatedTask] = useState<any>(null);

    const handleSubmit = async (data: JiraTaskFormData) => {
        const result = await executeAction('jira_create_ticket', data, threadId);

        if (result.success) {
            setCreatedTask(result.data);
            // Opcional: Notificar chat sobre a ação manual?
        }
    };

    const handleClose = () => {
        if (createdTask) {
            setCreatedTask(null);
        }
        onClose();
    };

    return (
        <BaseModal
            isOpen={isOpen}
            onClose={handleClose}
            title="Criar Task no Jira"
            description="Revise os parâmetros extraídos pelo Treq antes de criar o ticket."
            size="lg"
        >
            {createdTask ? (
                <div className="py-8 text-center animate-in zoom-in-95 duration-300">
                    <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                        Ticket criado com sucesso!
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                        O ticket {createdTask.key} foi gerado no seu Jira.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-3 justify-center">
                        {createdTask.url && (
                            <a
                                href={createdTask.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="
                  inline-flex items-center gap-2 px-6 py-3 rounded-lg
                  bg-yellow-500 text-black font-semibold
                  hover:bg-yellow-600 transition-all shadow-md
                "
                            >
                                <ExternalLink className="w-4 h-4" />
                                Ver no Jira
                            </a>
                        )}
                        <button
                            onClick={handleClose}
                            className="px-6 py-3 rounded-lg border-2 border-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                        >
                            Fechar
                        </button>
                    </div>
                </div>
            ) : (
                <div className="space-y-4">
                    {error && (
                        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-start gap-3 text-red-800 dark:text-red-300">
                            <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                            <div>
                                <p className="font-semibold text-sm">Erro ao criar ticket</p>
                                <p className="text-xs opacity-80">{error}</p>
                            </div>
                        </div>
                    )}

                    <JiraTaskForm
                        onSubmit={handleSubmit}
                        onCancel={handleClose}
                        prefill={prefill}
                        isSubmitting={isLoading}
                    />
                </div>
            )}
        </BaseModal>
    );
}
