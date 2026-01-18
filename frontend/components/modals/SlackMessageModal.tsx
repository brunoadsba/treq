'use client';

import { useState } from 'react';
import { BaseModal } from './BaseModal';
import { SlackMessageForm } from '../forms/SlackMessageForm';
import { SlackMessageFormData, SlackPrefillData } from '@/lib/validations/slack.schema';
import { useToolAction } from '@/hooks/useToolAction';
import { CheckCircle2, AlertCircle, Send } from 'lucide-react';

interface SlackMessageModalProps {
    isOpen: boolean;
    onClose: () => void;
    prefill?: SlackPrefillData;
    threadId?: string;
}

export function SlackMessageModal({
    isOpen,
    onClose,
    prefill,
    threadId
}: SlackMessageModalProps) {
    const { executeAction, isLoading, error } = useToolAction();
    const [isSent, setIsSent] = useState(false);

    const handleSubmit = async (data: SlackMessageFormData) => {
        const result = await executeAction('slack_notify', data, threadId);

        if (result.success) {
            setIsSent(true);
            setTimeout(() => {
                setIsSent(false);
                onClose();
            }, 2000);
        }
    };

    const handleClose = () => {
        setIsSent(false);
        onClose();
    };

    return (
        <BaseModal
            isOpen={isOpen}
            onClose={handleClose}
            title="Enviar Mensagem Slack"
            description="Revise a mensagem e o canal de destino."
            size="md"
        >
            {isSent ? (
                <div className="py-12 text-center animate-in zoom-in-95 duration-300">
                    <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                        Mensagem enviada!
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                        Sua equipe foi notificada com sucesso.
                    </p>
                </div>
            ) : (
                <div className="space-y-4">
                    {error && (
                        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-start gap-3 text-red-800 dark:text-red-300">
                            <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                            <div>
                                <p className="font-semibold text-sm">Erro ao enviar mensagem</p>
                                <p className="text-xs opacity-80">{error}</p>
                            </div>
                        </div>
                    )}

                    <SlackMessageForm
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
