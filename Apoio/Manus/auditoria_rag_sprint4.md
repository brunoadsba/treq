# Auditoria de Qualidade da Base de Conhecimento RAG

**Data:** 2026-01-16  
**Projeto:** Treq - Assistente Operacional Sotreq

---

## 1. Diagnóstico de Qualidade (Problemas Encontrados)

### Análise da Amostra RAG (Teste E2E anterior)

A amostra obtida do endpoint `/chat/` retornou 8 documentos com os seguintes padrões:

| ID | Severidade | Tipo de Problema | Descrição | Chunk(s) Afetado(s) |
|:---|:-----------|:-----------------|:----------|:--------------------|
| 1 | **Alto** | **Conteúdo Irrelevante** | Documentos sobre "piloto de precificação" e "roteiro de vídeo" estão sendo recuperados para queries sobre "procedimentos operacionais", indicando poluição semântica na base | `piloto_precificacao.md`, `roteiro_video_final.md` |
| 2 | **Alto** | **Falta de Metadados RLS** | Nenhum chunk possui campo `allowed_users` ou `user_id` no metadata, impossibilitando RLS baseado em usuário | Todos os chunks |
| 3 | **Médio** | **Inconsistência de Tipo** | Campo `document_type` às vezes é `"markdown"`, às vezes `"unknown"`, afetando filtragem por tipo | `teste_completo.md` |
| 4 | **Médio** | **Chunks Muito Granulares** | Chunks com 1000 chars + overlap de 200 podem fragmentar procedimentos importantes ao meio | Múltiplos |
| 5 | **Médio** | **Ruído de Formatação** | Chunks contêm listas de checkboxes (`- [ ]`) e markdown de tabelas que poluem o embedding vetorial | `piloto_precificacao.md` chunks 3-6 |
| 6 | **Baixo** | **Metadados Redundantes** | Campos `source` e `filename` frequentemente duplicam a mesma informação | Múltiplos |

### Estrutura Atual de Metadados

```json
{
  "type": "documentacao",
  "source": "nome_do_arquivo",
  "filename": "nome_do_arquivo.md",
  "file_size": 8742,
  "chunk_index": 2,
  "total_chunks": 6,
  "document_type": "markdown",
  "relative_path": "docs/arquivo.md"
}
```

**Campos Ausentes para RLS:**
- `allowed_users`: Lista de IDs de usuários autorizados
- `department`: Departamento com acesso
- `classification`: Classificação de sensibilidade (public, internal, confidential)

---

## 2. Recomendações de Otimização

### 2.1 Ajuste de Chunking

| Parâmetro | Atual | Recomendado | Justificativa |
|-----------|-------|-------------|---------------|
| `chunk_size` | 1000 | **1500** | Preservar procedimentos completos sem fragmentação |
| `chunk_overlap` | 200 | **300** | Garantir contexto entre boundaries de chunks |
| Estratégia | Recursive | **Parent Document RAG** | Retornar chunks pequenos, mas usar documento pai para contexto LLM |

**Implementação recomendada:**

```python
# Em chunking_service.py
self.chunk_size = 1500  # Aumentado de 1000
self.chunk_overlap = 300  # Aumentado de 200

# Adicionar separador prioritário para preservar seções
separators=["\\n## ", "\\n### ", "\\n\\n", "\\n", ". ", " "]
```

### 2.2 Correção de Metadados

Adicionar pipeline de pré-processamento antes da indexação:

```python
def prepare_metadata(filename: str, content: str, user_id: str = None) -> dict:
    return {
        # Campos existentes
        "filename": filename,
        "source": Path(filename).stem,
        "document_type": detect_document_type(filename),
        
        # NOVOS: Campos para RLS
        "allowed_users": [user_id] if user_id else ["*"],  # "*" = público
        "department": infer_department(filename, content),
        "classification": "internal",  # Padrão mais restritivo
        
        # NOVOS: Campos para filtragem semântica
        "domain": classify_domain(content),  # operacional, comercial, técnico
        "indexed_at": datetime.utcnow().isoformat(),
        "version": "1.0"
    }
```

### 2.3 Melhoria de Conteúdo

**Regra de limpeza para remover ruído:**

```python
import re

def clean_content(text: str) -> str:
    # Remover checkboxes markdown
    text = re.sub(r'- \[[ x]\] ', '', text)
    
    # Remover linhas de tabela vazias
    text = re.sub(r'\|[-: ]+\|', '', text)
    
    # Remover múltiplas quebras de linha
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remover headers repetitivos de rodapé
    text = re.sub(r'---\n*$', '', text)
    
    return text.strip()
```

### 2.4 Re-indexação da Base

1. Exportar chunks atuais para backup
2. Aplicar novas regras de chunking e limpeza
3. Adicionar metadados RLS
4. Re-indexar com embeddings novos
5. Validar qualidade com queries de teste

---

## 3. Validação de Segurança (Foco RLS)

### 3.1 Validação

| Aspecto | Status | Descrição |
|---------|--------|-----------|
| Campo `allowed_users` | ❌ **Ausente** | Não existe no schema atual |
| Filtro RLS no Supabase | ❌ **Não Implementado** | Qualquer usuário pode ler todos os chunks |
| Filtro na aplicação | ⚠️ **Parcial** | Endpoint `/chat/` não filtra por usuário |

### 3.2 Cenário de Risco

```
ATAQUE: Usuário do departamento "Comercial" envia query:
  "Qual o procedimento de manutenção do equipamento X?"

RESULTADO ATUAL: Sistema retorna documentos técnicos confidenciais
  que deveriam ser restritos ao departamento "Engenharia".

IMPACTO: Vazamento de informações técnicas sensíveis
```

### 3.3 Sugestão de Mitigação

**Opção A: RLS no Supabase (Recomendado)**

```sql
-- Habilitar RLS na tabela
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

-- Política de leitura por usuário
CREATE POLICY "users_read_allowed_docs" ON knowledge_base
FOR SELECT USING (
  metadata->>'classification' = 'public'
  OR metadata->'allowed_users' ? auth.uid()::text
  OR metadata->'allowed_users' ? '*'
);
```

**Opção B: Filtro na Aplicação**

```python
# Em rag_service.py search_similar()
async def search_similar(self, query: str, user_id: str = None, ...):
    filters = filters or {}
    
    if user_id:
        # Adicionar filtro de acesso
        filters['allowed_users'] = user_id
    
    # ... resto do código
```

---

## Resumo de Prioridades

| # | Ação | Severidade | Esforço | Impacto |
|---|------|------------|---------|---------|
| 1 | Implementar `allowed_users` no metadata | Alta | Médio | Segurança |
| 2 | Ativar RLS no Supabase | Alta | Baixo | Segurança |
| 3 | Aumentar chunk_size para 1500 | Média | Baixo | Qualidade |
| 4 | Adicionar limpeza de conteúdo | Média | Baixo | Embedding |
| 5 | Re-indexar base com novos padrões | Média | Alto | Qualidade + Segurança |
| 6 | Remover documentos irrelevantes | Baixa | Baixo | Precisão |

---

> [!WARNING]
> A base atual opera em **modo público** - qualquer usuário autenticado pode recuperar qualquer documento. Implementar RLS é **crítico** antes de adicionar documentos sensíveis.
