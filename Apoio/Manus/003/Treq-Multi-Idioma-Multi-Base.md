# Plano de Implementação: Treq Multi-Idioma & Multi-Base

Este plano detalha a evolução do Treq para suportar duas instâncias distintas: **Treq Operacional (PT-BR)** e **Treq Marketing (EN-US)**.

---

## 🎯 Visão Geral

O objetivo é permitir que o sistema alterne entre dois modos de operação baseados em variáveis de ambiente ou cabeçalhos de requisição, mantendo o custo zero.

| Característica | Treq Operacional (PT-BR) | Treq Marketing (EN-US) |
| :--- | :--- | :--- |
| **Idioma UI/LLM** | Português | Inglês |
| **Base de Dados** | Real (Supabase/Sotreq) | Mock (Arquivos JSON/Markdown) |
| **Domínio** | Operações/Técnico | Marketing Digital |

---

## 🛠️ Fase 1: Configuração e Ambiente

### 1.1 Variáveis de Ambiente (`.env`)
O desenvolvedor deve configurar o sistema para identificar o modo de operação:
```bash
# Modos: 'production' (PT) ou 'marketing' (EN)
TREQ_MODE=production 
TREQ_LANG=pt-br
```

### 1.2 Estrutura de Pastas
```text
src/
├── i18n/
│   ├── pt.json          # Traduções UI Português
│   └── en.json          # Traduções UI Inglês
├── mocks/
│   └── marketing_db/    # Base de dados mockada em Inglês
│       ├── seo_basics.md
│       └── ads_strategy.json
```

---

## 🧠 Fase 2: Lógica de Alternância (Backend)

### 2.1 Factory de Base de Dados
Implementar um padrão Factory no `rag_service.py` para decidir de onde ler os dados:

```python
class DataProviderFactory:
    @staticmethod
    def get_provider():
        if os.getenv("TREQ_MODE") == "marketing":
            return MockDataProvider(path="src/mocks/marketing_db/")
        return SupabaseDataProvider() # Base Real
```

### 2.2 Prompts Dinâmicos
Os System Prompts devem ser carregados dinamicamente com base no idioma:
- **PT**: "Você é um assistente operacional da Sotreq..."
- **EN**: "You are a Digital Marketing expert assistant..."

---

## 🎨 Fase 3: Internacionalização (Frontend)

### 3.1 i18n Framework
Utilizar `react-i18next` ou similar para gerenciar as strings da interface.
- **Regra**: O idioma da UI deve seguir a variável `TREQ_LANG`.

### 3.2 Componentes Condicionais
- Exibir logos ou banners específicos para a versão de Marketing (ex: "Treq Marketing Demo").

---

## 🚀 Roteiro de Implementação para o Dev

### Passo 1: Core i18n
1. Instalar dependências de tradução.
2. Criar os arquivos de dicionário `pt.json` e `en.json`.
3. Envolver a aplicação no Provider de tradução.

### Passo 2: Mock Engine
1. Criar a pasta `src/mocks/marketing_db/`.
2. Popular com 5-10 documentos de Marketing Digital em Inglês.
3. Implementar o `MockDataProvider` que simula a busca vetorial (pode usar busca por palavra-chave simples para manter custo zero).

### Passo 3: Middleware de Contexto
1. Garantir que cada requisição ao LLM envie o `language` no contexto.
2. Ajustar o `AgentState` para incluir o campo `locale`.

---

## ✅ Critérios de Aceite

1. **Versão PT**: Deve retornar dados reais da Sotreq e responder em Português.
2. **Versão EN**: Deve retornar dados de Marketing Digital (mocks) e responder em Inglês.
3. **Custo**: Nenhuma nova infraestrutura paga deve ser adicionada.

---
**Nota**: Este plano permite que você use a versão de Marketing como uma "Demo" rápida para clientes internacionais sem expor dados reais da Sotreq.
