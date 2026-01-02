import { ReactNode } from "react";

// Helper para extrair texto de elementos React
export function extractText(node: ReactNode): string {
    if (typeof node === "string") return node;
    if (typeof node === "number") return String(node);
    if (Array.isArray(node)) {
        return node.map(extractText).join("");
    }
    if (node && typeof node === "object" && "props" in node) {
        return extractText((node as any).props?.children || "");
    }
    return "";
}

// Interface para conteúdo parseado do Chain of Thought
export interface ParsedCoT {
    hasCoT: boolean;
    thinking?: string;
    answer: string;
}

// Parser para Chain of Thought - extrai <pensamento> e <resposta>
export function parseChainOfThought(text: string): ParsedCoT {
    if (!text) return { hasCoT: false, answer: "" };

    // Remove pensamento completamente
    let content = text.replace(/<pensamento>[\s\S]*?<\/pensamento>/gi, '').trim();

    const respostaMatches = content.match(/<resposta>([\s\S]*?)<\/resposta>/gi);
    let answer: string;

    if (respostaMatches && respostaMatches.length > 0) {
        answer = respostaMatches
            .map(match => {
                const innerMatch = match.match(/<resposta>([\s\S]*?)<\/resposta>/i);
                return innerMatch ? innerMatch[1].trim() : '';
            })
            .filter(text => text.length > 0)
            .join('\n\n')
            .trim();

        if (!answer || answer.length === 0) {
            answer = content.replace(/<resposta>[\s\S]*?<\/resposta>/gi, '').trim();
        }
    } else {
        answer = content.trim();
    }

    // Limpeza final
    answer = answer
        .replace(/<resposta>/gi, '')
        .replace(/<\/resposta>/gi, '')
        .replace(/<pensamento>[\s\S]*?<\/pensamento>/gi, '')
        .trim();

    // Remove avisos repetitivos do backend que o frontend já gerencia via cards
    answer = answer
        .replace(/⏱️\s*\*\*Processamento:\*\*[^\n]*\n?/gi, '')
        .replace(/⚠️\s*\*\*Aviso:\*\*[^\n]*\n?/gi, '')
        .replace(/Esta análise requer processamento[^\n]*precisão\.?\s*/gi, '')
        .replace(/A inteligência artificial pode cometer erros[^\n]*críticas\.?\s*/gi, '')
        .replace(/para não atingir o gatilho\.?/gi, '') // Remove redundância chata
        .replace(/^\s*\n\s*\n\n/gm, '\n\n')
        // Eliminar frases de metalanguage que vazam do prompt
        .replace(/Resposta objetiva, clara e direta baseada no contexto/gi, '')
        .replace(/Baseado no contexto fornecido/gi, '')
        .replace(/Aqui está a resposta baseada no contexto/gi, '')
        .replace(/De acordo com o contexto/gi, 'Analisando os dados')
        // Correções de concordância comuns
        .replace(/\bOs prazo\b/gi, 'Os prazos')
        .replace(/\bO prazos\b/gi, 'O prazo')
        .trim();

    return {
        hasCoT: false,
        thinking: undefined,
        answer,
    };
}

// Filtro de termos técnicos no frontend
export function sanitizeTechnicalTerms(text: string): string {
    if (!text || typeof text !== 'string') return text;

    let result = text;

    // Regras de substituição (Sincronizadas com backend mas com foco em UX frontend)
    const patterns: [RegExp, string][] = [
        [/\bSLazo\b/gi, 'prazo'],
        [/\bSLazos\b/gi, 'prazos'],
        [/\b(com|do|da|no|na|em|para|por)\s+SLA\b\s+([a-záàâãéêíóôõúç]+)/gi, '$1 prazo $2'],
        [/\b(com|do|da|no|na|em|para|por)\s+SLA\b/gi, '$1 prazo'],
        [/\bSLA\b\s+(de|da|do)\s+(\d+\s*\w+)/gi, 'prazo $1 $2'],
        [/\bSLA\b\s+(\d+\s*\w+)/gi, 'prazo de $1'],
        [/\bSLA\b\s+([a-záàâãéêíóôõúç]+(?:\s+[a-záàâãéêíóôõúç]+)?)/gi, 'prazo $1'],
        [/\bSLA\b/gi, 'prazo'],
        [/\bSLAs\b/gi, 'prazos'],
        [/\bSLA\b\s*:\s*/gi, 'prazo: '],
        [/\bKPI\b|\bKPIs\b/gi, 'indicador de performance'],
        [/\bOOB\b/gi, 'fora do padrão'],
        [/\bBacklog\b/gi, 'lista de tarefas pendentes'],
        [/\bSprints?\b/gi, 'ciclo de trabalho'],
        [/\bsigma\b|\bdesvio padrão\b/gi, 'desvio acima do normal'],
        [/\bthresholds?\b/gi, 'gatilho'],
        [/\bplaybooks?\b/gi, 'manual de procedimentos'],
    ];

    for (const [pattern, replacement] of patterns) {
        result = result.replace(pattern, replacement);
    }

    return result;
}

/**
 * Corrige o problema do Action Card split e das double asterisks literais.
 * Garante que múltiplos parágrafos dentro de uma 'Ação' fiquem no mesmo bloco visual.
 */
export function formatActionBlocks(text: string): string {
    if (!text) return text;

    // Estratégia: Encontrar o início da Ação e capturar TUDO até o fim do texto
    // (Ação geralmente é a última parte da resposta ou uma seção isolada)
    // Se houver necessidade de separar, podemos procurar por outro marcador de seção no futuro.
    let processed = text.replace(/(💡\s*\*\*?Ação:\*\*?[\s\S]*)/gi, (match) => {
        // Envolvemos em uma tag customizada temporária para o renderizador saber que é um bloco único
        // Mas para manter compatibilidade com o matcher de 'p', vamos apenas garantir que não haja 
        // quebras de linha duplas (\n\n) que o ReactMarkdown usaria para separar em parágrafos fora do nosso controle.
        // Transformamos \n\n em \n para que o ReactMarkdown dentro do 'p' trate como parágrafos internos.
        return match.trim();
    });

    return processed;
}

/**
 * Fecha tags de markdown que ficaram abertas (ex: ** sem o par correspondente)
 * Útil para streaming ou respostas truncadas.
 */
export function repairMarkdown(text: string): string {
    if (!text) return text;

    // 1. Corrigir negritos e bullets quebrados por nova linha (Problema relatado pelo usuário)
    // Ex: **Nível 1 (Atenção\nAmarelo):** -> **Nível 1 (Atenção Amarelo):**
    let repaired = text
        .replace(/\*\*([^\*\n]*)\n+([^\*\n]*)\*\*/g, '**$1 $2**')
        .replace(/•\s*([^\n]+)\n\n+([A-Z])/g, '• $1 $2'); // Junta bullets que quebraram no meio da frase

    // 2. Fechar tags de markdown que ficaram abertas (ex: ** sem o par correspondente)
    // Útil para streaming ou respostas truncadas.
    const boldMatches = repaired.match(/\*\*/g);
    if (boldMatches && boldMatches.length % 2 !== 0) {
        repaired += "**";
    }

    return repaired;
}
