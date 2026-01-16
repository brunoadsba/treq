# LLM Development - Guia de Uso de Master Harnesses

## Visão Geral

Este documento orienta desenvolvedores e LLMs (Large Language Models) sobre como utilizar os Master Harnesses do repositório **Context-Engineering** no desenvolvimento de projetos. O foco é aplicar a **Engenharia de Contexto** (ACE - Agent Context Evolution) para evoluir continuamente o conhecimento das IAs, garantindo respostas precisas e contextuais.

## Contexto Específico: Projeto Treq

O **Treq** (Assistente Operacional de IA Empresarial) é uma plataforma cognitiva que utiliza:

* **RAG Multi-nível:** 3 níveis de LLMs (8B para consultas rápidas, 70B para tarefas complexas, GLM-4 para análises executivas)
* **Orquestração de 9 Agentes Especializados:** Monitoramento em tempo real
* **Base de Conhecimento RAG:** Supabase + pgvector com embeddings multilíngues
* **Pipeline de Documentos:** Processamento de PDF, Excel, Markdown com OCR
* **Desafios Técnicos:** Backend instável (crashes por memory overflow), necessidade de escalabilidade empresarial

## Integração com Master Harnesses

Os Master Harnesses do Context-Engineering foram projetados para guiar todo o ciclo de desenvolvimento do Treq:

### Fluxo Principal

```
1. PRD (Product Requirements Document)
   ↓
2. ADR (Architecture Decision Records)
   ↓
3. User Stories (Requisitos Detalhados)
   ↓
4. API Design (Design de APIs)
   ↓
5. Database Design (Design de Banco de Dados)
   ↓
6. Domain-Driven Design (Modelagem de Domínio)
   ↓
7. TDD/BDD (Desenvolvimento por Testes)
   ↓
8. Code Review (Revisão de Código)
   ↓
9. CI/CD Pipeline (Deploy Automático)
   ↓
10. Security Review (Segurança)
   ↓
11. Performance Review (Performance)
```

## Como LLMs Devem Usar os Master Harnesses

### 1. Como Desenvolvedores Usam os Master Harnesses

#### Para Gerar Requisitos (PRD)

**Comandos Cursor AI:**
```bash
/prd-create
```

**Cenário de Uso - Novo Feature:**

**Pergunta do Desenvolvedor:**
> "Preciso criar uma nova feature de upload de documentos avançados com OCR para tabelas em imagens."

**Como o LLM Deve Usar o PRD.md:**

1. **Contextualizar a Pergunta:**
   - Reconher que o Treq é uma plataforma RAG multi-nível
   - Consultar [`PRD.md`](./PRD/PRD.md) para entender padrões de requisitos

2. **Extrair Requisitos Específicos do PRD:**
   - Buscar seção: "Tipos de Documentos Suportados"
   - Identificar requisitos: PDF escaneados (OCR), tabelas em imagens, Markdown
   - Verificar constraints: "O sistema deve processar até 100 documentos simultâneos"

3. **Gerar Requisitos Funcionais:**
   ```gherkin
   Feature: Upload de Documentos Avançados
     Como um usuário de suporte técnico, eu quero fazer upload de documentos complexos
     Esses documentos incluem PDFs escaneados com tabelas e imagens que precisam de OCR
     Dado que o sistema já suporta PDF e Markdown, preciso implementar processamento de imagens
     
   Cenário 1: Upload de PDF com Tabelas
     Quando eu fizer upload de um PDF que contém tabelas
     E o sistema deve extrair essas tabelas automaticamente usando OCR
     E as tabelas devem ser estruturadas e indexadas para permitir busca
     
   Cenário 2: Upload de Imagens
     Quando eu fizer upload de uma imagem
     O sistema deve analisar a imagem
     E se ela contiver documentos técnicos (diagramas, fluxogramas)
     O sistema deve extraí-los e indexar como texto
   ```

**Como LLM Responde:**
> Conforme [`PRD.md`](./PRD/PRD.md) - Seção "Tipos de Documentos Suportados", a feature deve incluir:
> 
> - Suporte a **PDFs Escaneados com OCR** para extrair texto e tabelas
> - Suporte a **Imagens com OCR** para extrair diagramas e documentos técnicos
> - Processamento de **tabelas estruturadas** para dados tabulares em documentos
> - **Limitações de performance:** Máximo de 100 documentos processados simultaneamente
>
> 
> **Ação Recomendada:**
> - Criar ADR para documentar decisão técnica de usar bibliotecas específicas de OCR (Tesseract, PaddleOCR, etc.)
> - Consultar [`Database Design.md`](./DatabaseDesign/DatabaseDesign.md) para modelar schema de armazenamento de tabelas extraídas

---

#### Para Arquitetura (ADR)

**Comandos Cursor AI:**
```bash
/adr-create
```

**Cenário de Uso - Mudança de Arquitetura:**

**Pergunta do Desenvolvedor:**
> "Devo migrar do backend atual (FastAPI) para uma arquitetura baseada em microserviços para suportar melhor o RAG e processamento pesado de documentos?"

**Como o LLM Deve Usar o ADR.md:**

1. **Contextualizar a Pergunta:**
   - Reconher que o Treq precisa escalar para milhões de documentos
   - Consultar [`Database Design.md`](./DatabaseDesign/DatabaseDesign.md) para entender schema atual
   - Considerar que processamento de OCR e imagens é pesado em CPU

2. **Verificar ADRs Existentes:**
   - Buscar no arquivo [`ADR.md`](./ADR/ADR.md) se há decisões anteriores sobre arquitetura

3. **Propor Nova Decisão de Arquitetura:**
   - **Título:** Migrar para Microserviços com Message Queue (RabbitMQ)
   - **Status:** Proposta
   - **Contexto:** Backend atual (FastAPI) monolítico está causando crashes por memory overflow. Processamento de documentos (OCR, imagens) é pesado em CPU e pode estar consumindo toda a memória.
   - **Racional:**
     - Separar o processamento de documentos em um serviço dedicado (Document Processor Service)
     - Isso permite escalar o processamento independentemente da API REST
     - Utilizar fila de mensagens (RabbitMQ) para gerenciar carga
     - Backend REST permanece leve (apenas autenticação e orquestração)
   - **Benefícios:**
       - Escalabilidade independente de cada serviço
       - Backend mais estável e livre de crashes
       - Possibilidade de implementar rate limiting por serviço
       - Facilita monitoramento de performance por serviço
   - **Trade-offs:**
       - Complexidade arquitetural aumenta
       - Mais dependências externas (RabbitMQ)
       - Latência adicional devido à comunicação entre serviços
   - **Alternativa:** Manter monolito e implementar otimizações no processamento de documentos (lazy loading, cache de OCR, etc.)

4. **Gerar ADR:**
   ```markdown
   # ADR-001: Arquitetura de Microserviços para Processamento de Documentos
   
   ## Status
   
   Data: 15/01/2026
   
   Decisores: Equipe de Engenharia + Especialista ACE
   
   ## Contexto
   
   O Treq é uma plataforma cognitiva empresarial que precisa processar até 1 milhão de documentos simultaneamente. O backend atual (FastAPI monolítico) está enfrentando problemas de estabilidade (crashes por memory overflow) quando processa operações pesadas de LLM e indexação de documentos.
   
   ## Problema
   
   O processamento de documentos (OCR, análise de tabelas em imagens) é extremamente pesado em CPU e consumo de memória. Atualmente, essas operações ocorrem no mesmo processo que as chamadas de LLM, o que causa:
   - Aumento drástico de uso de memória
   - Inicialização lenta e carregamento do servidor
   - Crashes intermitentes (SIGTERM 139) devido a memory overflow
   
   ## Decisão
   
   Propomos migrar o backend FastAPI atual para uma arquitetura baseada em microserviços, separando o processamento de documentos em um serviço dedicado.
   
   ## Consequências
   
   Positivas:
   - Escalabilidade independente do processamento de documentos
   - Backend REST mais leve e estável
   - Possibilidade de implementar rate limiting e caching por serviço
   - Monitoramento granular por serviço (document processor, LLM service, etc.)
   - Redução de crashes por isolamento de processamento pesado
   
   Negativas:
   - Aumento da complexidade arquitetural do sistema
   - Mais dependências externas (RabbitMQ)
   - Latência adicional entre serviços
   - Custo de infraestrutura mais alto (filas de mensagens, etc.)
   
   ## Alternativas Consideradas
   
   1. Manter monolito e otimizar:
      - Implementar lazy loading para bibliotecas de OCR
      - Cachear resultados de OCR para documentos repetidos
      - Usar modelos de OCR mais eficientes (Tesseract v4)
   
   2. Implementar rate limiting global:
      - Limitar taxa de uploads de documentos por usuário
      - Priorizar processamento de documentos em fila separada
   
   ## Decisão
   
   Migrar para arquitetura baseada em microserviços, separando o processamento de documentos em um serviço dedicado (Document Processor Service), com backend REST mantendo-se leve.
   
   ## Impacto
   
   Esta mudança afeta principalmente o Database Design (schema de documentos), API Design (endpoint de upload) e CI/CD Pipeline (deploy de múltiplos serviços).
   ```
```

**Como LLM Responde:**
> Conforme [`ADR.md`](./ADR/ADR.md) e [`Database Design.md`](./DatabaseDesign/DatabaseDesign.md) - A decisão documentada em ADR define que o processamento de documentos deve ser movido para um microserviço dedicado.
>
> 
> **Ação Recomendada:**
> - Consultar [`API Design.md`](./APIDesign/APIDesign.md) para modelar o endpoint `/documents/upload-advanced` do Document Processor Service
> - Definir contrato de API (Request/Response)
> - Consultar [`User Stories`](./UserStories/UserStories.md) para criar histórias de usuário para o novo processo de upload

---

#### Para Domain-Driven Design (DDD)

**Comandos Cursor AI:**
```bash
/ddd-contexts
```

**Cenário de Uso - Modelagem de Domínio RAG:**

**Pergunta do Desenvolvedor:**
> "Como devo modelar o domínio do Treq para suportar RAG multi-nível com contextos específicos para cada nível de LLM (8B, 70B, GLM-4)?"

**Como o LLM Deve Usar o DomainDrivenDesign.md:**

1. **Contextualizar a Pergunta:**
   - Reconher que o Treq usa 9 agentes especializados orquestrados
   - Consultar [`DomainDrivenDesign.md`](./DomainDrivenDesign/DomainDrivenDesign.md) para entender conceitos de DDD
   - Entender que RAG multi-nível é uma forma avançada de aplicar DDD

2. **Extrair Bounded Contexts:**
   - Identificar contextos delimitados principais:
     - **Document Context:** Upload, processamento, indexação, RAG
     - **LLM Orchestration Context:** Roteamento inteligente entre 3 níveis de LLMs
     - **User Context:** Autenticação, sessão, preferências
     - **System Context:** Monitoramento, observabilidade, alertas

3. **Definir Agregados e Entidades:**
   - **Agregado Raiz 1: DocumentContext**
     - Entidades: Document, Chunk, Embedding, Metadata
     - Invariante: "Todos os chunks devem ter embeddings válidos"
     - Repositório: DocumentService (processamento), VectorDB (busca)
   
   - **Agregado Raiz 2: OrquestradorLLM**
     - Entidades: Query, LLMResponse, RoutingStrategy
     - Invariante: "Roteamento deve respeitar prioridade de queries e disponibilidade de LLMs"
     - Repositório: LLMService (8B, 70B, GLM-4), RouterService

4. **Definir Eventos de Domínio:**
   - `DocumentUploaded` - Quando documento é processado
   - `ContextRetrieved` - Quando RAG recupera contexto
   - `LLMResponseGenerated` - Quando LLM gera resposta
   - `RoutingDecisionMade` - Quando orquestrador escolhe LLM

**Como LLM Responde:**
> Conforme [`DomainDrivenDesign.md`](./DomainDrivenDesign/DomainDrivenDesign.md) - O domínio do Treq deve ser modelado como bounded contexts com agregados bem definidos.
>
> 
> **Exemplo de Modelagem:**
> ```python
> # domain/document_context.py
> 
> from dataclasses import dataclass
> 
> @dataclass
> class DocumentChunk:
>     id: str
>     content: str
>     metadata: dict
>     embedding_id: str
>     document_id: str
> 
> @dataclass
> class OrquestradorQuery:
>     query: str
>     query_type: QueryType  # Enum (RAPIDA, COMPLEXA, EXECUTIVA)
>     user_id: str
>     context: list[str]
> 
> @dataclass
> class OrquestradorDecision:
>     chosen_llm: str  # "8b", "70b", "glm4"
>     reason: str
> ```
> 
> **Ação Recomendada:**
> - Criar novo ADR documentando a modelagem DDD para RAG multi-nível
> - Consultar [`User Stories`](./UserStories/UserStories.md) para criar histórias de usuário que validem o comportamento do orquestrador

---

#### Para TDD/BDD

**Comandos Cursor AI:**
```bash
/tdd-create
```

**Cenário de Uso - Testar Processamento de Documentos:**

**Pergunta do Desenvolvedor:**
> "Preciso escrever testes unitários para o Document Processor Service que processa PDFs com OCR e extraí tabelas."

**Como o LLM Deve Usar o TDD_BDD.md:**

1. **Consultar Padrões de Teste:**
   - Ler seção "TDD/BDD" do [`TDD_BDD.md`](./TDD_BDD/TDD_BDD.md)
   - Seguir ciclo Red-Green-Refactor

2. **Escrever Testes Unitários:**
   ```python
   # tests/unit/test_document_processor.py
   
   import pytest
   from app.services.document_processor import DocumentProcessorService
   
   def test_extract_tables_from_scanned_pdf():
       # Setup
       service = DocumentProcessorService()
       
       # Act
       pdf_content = load_test_pdf("document_with_tables.pdf")
       tables = service.extract_tables(pdf_content)
       
       # Assert
       assert len(tables) > 0
       assert tables[0]['row_count'] == 15
       assert tables[0]['column_names'][0] == "Quantidade"
   
   def test_extract_text_from_image_with_ocr():
       # Setup
       service = DocumentProcessorService()
       
       # Act
       image = load_test_image("technical_diagram.png")
       text = service.extract_text_with_ocr(image)
       
       # Assert
       assert "diagrama" in text.lower()
       assert len(text) > 0
   ```
   
3. **Seguir Ciclo Red-Green-Refactor:**
   - **Red:** Escrever testes que falhem intencionalmente
   - **Green:** Fazer passar os testes
   - **Refactor:** Otimizar código sem alterar comportamento

**Como LLM Responde:**
> Conforme [`TDD_BDD.md`](./TDD_BDD/TDD_BDD.md) - Testes BDD devem seguir formato Gherkin e cobrir happy paths e edge cases do Document Processor Service.
>
> 
> **Ação Recomendada:**
> - Criar novos casos de teste para PDFs com tabelas complexas
> - Validar que OCR funciona para diferentes tipos de documentos (contrato, relatório, etc.)
> - Implementar mocking para imagens e PDFs em testes para evitar dependências externas

---

#### Para Code Review

**Comandos Cursor AI:**
```bash
/cr-analyze
```

**Cenário de Uso - Analisar Código Instável:**

**Pergunta do Desenvolvedor:**
> "O backend está crashando com SIGTERM 139 (memory overflow) quando processa LLM calls. Como posso fazer code review para identificar e resolver isso?"

**Como o LLM Deve Usar o CodeReview.md:**

1. **Analisar Sintomas de Memory Overflow:**
   - Ler seção "Análise de Causa Raiz (Root Cause #1)" de [`PROBLEMAS_PENDENTES_TESTES_E2E.md`](../../../treq/PROBLEMAS_PENDENTES_TESTES_E2E.md)
   - Identificar se crash é causado por:
     - **Bibliotecas pesadas:** LangChain, NumPy, pandas
     - **Iterações infinitas:** Loop sem saída em embeddings
     - **Falta de lazy loading:** Bibliotecas carregadas no startup
     - **Processamento de documentos:** Operação pesada em CPU

2. **Aplicar Checklists de Segurança:**
   - Ler seção "Análise de Causa Raiz (Root Cause #1)" de [`CodeReview.md`](./CodeReview/CodeReview.md)
   - Verificar se há vulnerabilidades de segurança que possam causar memory overflow (ex: DoS por PDF malicioso)

3. **Propor Correções Focadas:**
   - Implementar **Lazy Loading para Bibliotecas Pesadas** (já solução proposta em problemas pendentes)
   - Adicionar **Rate Limiting Agressivo** para LLM calls (limitar número de requisições simultâneas)
   - Implementar **Monitoramento de Memória em Runtime** (verificar uso de RAM antes de cada LLM call)
   - Usar **Circuit Breaker** para LLM calls (desabilitar se houver falhas consecutivas)

**Como LLM Responde:**
> Conforme [`CodeReview.md`](./CodeReview/CodeReview.md) e [`PROBLEMAS_PENDENTES_TESTES_E2E.md`](../../../treq/PROBLEMAS_PENDENTES_TESTES_E2E.md) - O crash por memory overflow está relacionado a operações de LLM. Implementar lazy loading, rate limiting e circuit breaker pode resolver o problema.
>
> 
> **Ação Recomendada:**
> - Criar ADR documentando a implementação dessas correções de segurança e performance
> - Priorizar correções que resolvem o crash (Root Cause #1) em vez de correções cosméticas

---

#### Para Security Review

**Comandos Cursor AI:**
```bash
/sec-owasp
```

**Cenário de Uso - Proteger Uploads de Documentos:**

**Pergunta do Desenvolvedor:**
> "Preciso implementar OWASP ASVS para o endpoint de upload de documentos para proteger contra ataques como DoS, brute force e injeção de arquivos maliciosos."

**Como o LLM Deve Usar o SecurityReview.md:**

1. **Consultar OWASP ASVS Requirements:**
   - Ler seção "OWASP ASVS v4.0 Verification" de [`SecurityReview.md`](./SecurityReview/SecurityReview.md)
   - Identificar requisitos relevantes para upload de arquivos (validação de tipos, tamanho, escaneamento de malware)

2. **Implementar Validações de Entrada:**
   ```python
   from fastapi import UploadFile, HTTPException
   
   # Validações OWASP ASVS
   def validate_upload_file(file: UploadFile) -> UploadFile:
       # V1.1: Input Validation
       if file.size > 50 * 1024 * 1024:  # 50MB
           raise HTTPException(status_code=413, detail="Arquivo muito grande")
       
       # V2.1: File Type Validation
       allowed_types = ["application/pdf", "image/png", "image/jpeg"]
       if file.content_type not in allowed_types:
           raise HTTPException(status_code=415, detail="Tipo de arquivo não suportado")
       
       # V5.2: Malicious File Scanning
       # (Simplificado) Em produção, usar VirusTotal ou similar
       scan_result = scan_for_malware(file)
       if scan_result.is_malicious:
           raise HTTPException(status_code=422, detail="Arquivo malicioso detectado")
   
   @app.post("/documents/upload", dependencies=[Depends(validate_upload_file)])
   async def upload_document(file: UploadFile, user: User = Depends(get_current_user)):
       validated_file = validate_upload_file(file)
       scan_result = await scan_for_malware(validated_file)
       if scan_result.is_malicious:
           raise HTTPException(status_code=422)
       
       # Processar arquivo (chamada ao Document Processor Service)
       document_id = await document_processor.process(validated_file)
       
       return {"document_id": document_id, "status": "queued"}
   ```

3. **Implementar Rate Limiting:**
   - Limitar uploads por usuário/IP para prevenir DoS
   - Usar [`SlowAPI`](https://fastapi.tiangolo.com/tutorial/rate-limit/) `Limiter` para gerenciar taxa

**Como LLM Responde:**
> Conforme [`SecurityReview.md`](./SecurityReview/SecurityReview.md) - Upload de documentos deve seguir OWASP ASVS v4.0. Implementar validação de entrada, escaneamento de malware e rate limiting.
>
> 
> **Ação Recomendada:**
> - Criar ADR documentando a implementação de OWASP ASVS v4.0 para o endpoint de upload
> - Consultar [`API Design.md`](./APIDesign/APIDesign.md) para definir contrato da API com limites de upload

---

## Integração com Sistemas Específicos do Treq

### 1. RAG Multi-nível

Como LLMs podem acessar os Master Harnesses para entender a arquitetura RAG do Treq:

**Pergunta do Desenvolvedor:**
> "Como configurar o orquestrador do Treq para usar os 3 níveis de LLMs (8B, 70B, GLM-4) em vez de apenas um modelo?"

**Como LLM Deve Usar os Master Harnesses:**

1. **Consultar [`PerformanceReview.md`](./PerformanceReview/PerformanceReview.md):**
   - Buscar seção "Strategies de Performance e Observabilidade"
   - Entender que diferentes níveis de LLM devem ser usados baseado no tipo de query

2. **Aplicar Lógica de Roteamento:**
   - Queries simples (palavras-chave) → LLM 8B (rápido)
   - Queries complexas (explicações, sínteses) → LLM 70B (moderadamente rápido)
   - Queries executivas (análises de dados) → LLM GLM-4 (mais lento mas mais inteligente)

**Resposta do LLM:**
> Para implementar orquestração inteligente com múltiplos níveis de LLMs, consulte [`APIDesign/APIDesign.md`](./APIDesign/APIDesign.md) para criar endpoint `/chat/with_routing_strategy` e [`Database Design.md`](./DatabaseDesign/DatabaseDesign.md) para modelar tabela `llm_routing_config`.
>
> 
> **Exemplo:**
> ```python
> # database/schema.py
> from sqlalchemy import Column, String, Enum as EnumType
> 
> class LLMRoutingConfig(Base):
>     __tablename__ = 'llm_routing_configs'
>     id = Column(String, primary_key=True)
>     query_patterns = Column(JSON)
>     default_llm = Column(String, nullable=False, server_default='8b')
>     fallback_llm = Column(String, nullable=False, server_default='70b')
>     analysis_llm = Column(String, nullable=False, server_default='glm4')
> ```

---

### 2. Base de Conhecimento RAG

Como LLMs podem referenciar a configuração de RAG do Treq:

**Pergunta do Desenvolvedor:**
> "Como configurar pgvector e embeddings no Supabase para suportar busca semântica em 3 idiomas (português, inglês, espanhol)?"

**Como LLM Deve Usar os Master Harnesses:**

1. **Consultar [`DatabaseDesign.md`](./DatabaseDesign/DatabaseDesign.md):**
   - Buscar seção "Configuração de pgvector"
   - Entender modelo de dados para embeddings

2. **Aplicar Configuração Multilíngue:**
   - Criar coluna `language` na tabela `documents` (PT, EN, ES)
   - Gerar embeddings separados para cada idioma

3. **Implementar Busca Filtrada por Idioma:**
   - Adicionar filtro em queries: `WHERE language = 'pt'`
   - Garantir que resultados sejam relevantes para o idioma do usuário

**Resposta do LLM:**
> Para configurar RAG multi-língue no Treq, consulte [`DatabaseDesign.md`](./DatabaseDesign/DatabaseDesign.md) para entender schema de embeddings e [`APIDesign/APIDesign.md`](./APIDesign/APIDesign.md) para criar endpoint `/documents/search?lang=pt`. Use [`TDD_BDD/TDD_BDD.md`](./TDD_BDD/TDD_BDD.md) para escrever testes que validem busca em múltiplos idiomas.
>
> 
> **Exemplo:**
> ```python
> # api/routes/documents.py
> @router.get("/search")
> async def search_documents(query: str, lang: str = "pt"):
>     # Validação
>     if not query or len(query) < 3:
>         raise HTTPException(status_code=400, detail="Query muito curta")
>     
>     # Busca vetorial (pgvector)
>     query_embedding = await generate_embedding(query)
>     results = await db.query(f"""
>         SELECT documents.content, documents.id
>         FROM documents
>         JOIN embeddings ON documents.id = embeddings.doc_id
>         WHERE embeddings.lang = $1
>         ORDER BY documents.embedding <-> $1
>         LIMIT 10
>     """)
>     
>     return {"results": results}
> ```

---

## Best Practices para LLMs

### 1. Contexto Evolutivo (ACE)

**Como LLMs Podem Melhorar o Contexto:**

1. **Solicitar Feedback Ativo:**
   - Quando um usuário avalia uma resposta (👎 ou 👎), o LLM deve usar isso para evoluir
   - LLM deve registrar o feedback no [`backend/.agent/context-cache.txt`](../../../treq/backend/.agent/context-cache.txt)

2. **Fornecer Chain of Thought:**
   - Para queries complexas, mostrar o raciocínio passo-a-passo
   - Ajuda a construir confiança com desenvolvedores e usuários

3. **Evitar Alucinações:**
   - LLM deve admitir "Não tenho certeza" quando não souber a resposta
   - Citar fontes (ex: "Conforme documento X")
   - Usar RAG para fundamentar respostas em documentos reais

4. **Respeitar Latência:**
   - LLMs devem ser rápidos para não degradar a experiência do usuário
   - Se uma query demora mais que 3 segundos, considerar usar LLM menor (8B) em vez de GLM-4

---

## Casos de Uso Completos

### Caso 1: Criação de Novo Feature Usando PRD + ADR + TDD/BDD

**Desenvolvedor:** Alice
**Feature:** Upload de Documentos Avançados

```gherkin
Feature: Upload de Documentos Avançados
  
  Como um usuário de suporte técnico, eu quero fazer upload de documentos complexos
  Esses documentos incluem PDFs escaneados com tabelas e imagens
  Dado que o sistema já suporta PDF e Markdown, preciso implementar processamento de imagens
```

**Passo 1: Criar PRD (2-3 dias)**
- **Comando:** `/prd-create`
- **Saída:** Documento [`PRD.md`](./PRD/PRD.md) atualizado com novos requisitos

**Passo 2: Criar ADR (1 dia)**
- **Comando:** `/adr-create`
- **Saída:** Documento [`ADR.md`](./ADR/ADR.md) com nova decisão técnica

**Passo 3: Criar User Stories (1 dia)**
- **Comando:** `/us-create`
- **Saída:** Documento [`UserStories.md`](./UserStories/UserStories.md) com cenários de teste

**Passo 4: Implementar e Testar (5-7 dias)**
- **Comando:** `/tdd-create` → `/test-unit`
- **Saída:** Código [`DocumentProcessorService.py`](../backend/app/services/document_processor.py) e testes em [`tests/unit/test_document_processor.py`](../tests/unit/test_document_processor.py)

**Passo 5: Code Review (1 dia)**
- **Comando:** `/cr-analyze`
- **Saída:** Documento [`CodeReview.md`](./CodeReview/CodeReview.md) com análise de performance e segurança

**Passo 6: Deploy (1 dia)**
- **Comando:** `/cicd-cd`
- **Saída:** Feature disponível em produção

---

## Conclusão

Usar os Master Harnesses do **Context-Engineering** garante que o desenvolvimento do Treq seja:

- **Consistente:** Seguindo padrões da indústria e melhores práticas
- **Documentado:** Todas as decisões e requisitos ficam registrados
- **Escalável:** A arquitetura e os processos podem crescer com o negócio
- **De Alta Qualidade:** Testes, revisões e validações de segurança são sistemáticos
- **Evolutivo:** Contexto evolutivo (ACE) permite que LLMs aprendam continuamente

---

## Referências Cruzadas com Outros Master Harnesses

| Master Harness | Uso no Treq | Integração |
|---------------|----------------|-----------|
| **PRD** | Definir requisitos para uploads avançados | [`Database Design`](./DatabaseDesign/DatabaseDesign.md) para schema de documentos |
| **ADR** | Decidir microserviços para processamento | [`API Design`](./APIDesign/APIDesign.md) para endpoints |
| **User Stories** | Cenários de teste para OCR e tabelas | [`TDD/BDD`](./TDD_BDD/TDD_BDD.md) para testes unitários |
| **Code Review** | Analisar memory overflow | [`Security Review`](./SecurityReview/SecurityReview.md) para OWASP ASVS |

---

**Última Atualização:** 15/01/2026
