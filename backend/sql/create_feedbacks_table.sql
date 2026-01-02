-- Tabela para armazenar feedbacks dos usuários
-- Usada para análise de qualidade (RAG/LLM) e integração com LangSmith

CREATE TABLE IF NOT EXISTS feedbacks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id TEXT, -- ID do run no LangSmith (crucial para o loop de melhoria)
    feedback_type TEXT NOT NULL, -- 'positive' ou 'negative'
    score FLOAT NOT NULL, -- 1.0 para positive, 0.0 para negative
    comment TEXT, -- Comentário opcional do usuário
    metadata JSONB DEFAULT '{}', -- Metadados adicionais (browser, os, session, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_feedbacks_run_id ON feedbacks(run_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_type ON feedbacks(feedback_type);
CREATE INDEX IF NOT EXISTS idx_feedbacks_created_at ON feedbacks(created_at);

-- Comentário para o time de Dados
COMMENT ON TABLE feedbacks IS 'Tabela de feedbacks 👍/👎 para otimização do assistente operacional via LangSmith.';
