
Context-Engineering/
├── README.md # Este arquivo - ponto de entrada
├── foundations/ # Documentos fundamentais
│ ├── PRD.md # Requisitos de Produto
│ ├── ADR.md # Decisões Arquiteturais
│ └── UserStories.md # Histórias de Usuário detalhadas
├── development/ # Documentos de desenvolvimento
│ ├── TDD_BDD.md # Estratégia de testes
│ ├── CodeReview.md # Processo de revisão de código
│ ├── DomainDrivenDesign.md # Modelagem de domínio
│ └── SecurityReview.md # Revisão de segurança
└── infrastructure/ # Documentos de infraestrutura
├── APIDesign.md # Design de APIs
├── DatabaseDesign.md # Design de banco de dados
├── CICDPipeline.md # Pipeline de CI/CD
└── PerformanceReview.md # Revisão de performance



## Fluxo de Trabalho Recomendado
Os harnesses são projetados para serem usados em sequência, formando um fluxo de trabalho completo:

1. **Definição de Produto** (foundations/)
   - Comece com o PRD para entender requisitos de negócio
   - Gere User Stories detalhadas com critérios de aceite

2. **Arquitetura e Design** (foundations/ + infrastructure/)
   - Utilize ADR para documentar decisões arquiteturais
   - Aplique Domain-Driven Design para modelagem de domínio
   - Crie Database Design e API Design alinhados com o domínio

3. **Implementação** (development/)
   - Siga TDD/BDD para desenvolvimento orientado a testes
   - Utilize Code Review para garantir qualidade
   - Aplique Security Review para identificar vulnerabilidades

4. **Infraestrutura e Operações** (infrastructure/)
   - Configure CI/CD Pipeline para automação
   - Realize Performance Review para otimização
   - Monitore e refine continuamente

## Integração com Ferramentas

### Cursor AI
Todos os harnesses incluem comandos personalizados do Cursor AI iniciados com `/`:
- Comandos específicos por domínio (ex: `/prd-create`, `/api-design`)
- Comando universal `/ace-refine` para evoluir contexto em `.context.md`
- Alinhamento com `.cursor/rules` para conformidade com padrões do projeto

### Agentes de IA (LangChain)
Cada harness define uma orquestração de agentes:
- **Agente Principal**: Responsável pela execução principal
- **Agentes Especializados**: Para análises específicas (segurança, performance, etc.)
- **Ferramentas (Tools)**: Funções específicas para cada contexto
- **Padrão de Entrega (Handoff)**: Fluxo de trabalho entre agentes
- **Critérios de Validação**: Requisitos de qualidade do output

## Documentos Principais e Suas Relações

| Documento | Categoria | Dependências Diretas | Documentos que Dependem |
|-----------|-----------|----------------------|-------------------------|
| PRD.md | foundations | Nenhuma | UserStories.md, ADR.md |
| ADR.md | foundations | PRD.md | DomainDrivenDesign.md, DatabaseDesign.md, APIDesign.md |
| UserStories.md | foundations | PRD.md | TDD_BDD.md, CodeReview.md |
| DomainDrivenDesign.md | development | ADR.md | DatabaseDesign.md, APIDesign.md, SecurityReview.md |
| DatabaseDesign.md | infrastructure | ADR.md, DomainDrivenDesign.md | APIDesign.md, SecurityReview.md |
| APIDesign.md | infrastructure | ADR.md, DomainDrivenDesign.md | TDD_BDD.md, SecurityReview.md |
| TDD_BDD.md | development | UserStories.md, APIDesign.md | CodeReview.md |
| CodeReview.md | development | TDD_BDD.md | CICDPipeline.md |
| SecurityReview.md | development | DatabaseDesign.md, APIDesign.md | CICDPipeline.md |
| CICDPipeline.md | infrastructure | CodeReview.md, SecurityReview.md | PerformanceReview.md |
| PerformanceReview.md | infrastructure | CICDPipeline.md | SecurityReview.md (feedback loop) |

## Como Contribuir
- Mantenha a estrutura de diretórios definida
- Siga os padrões da indústria documentados em cada harness
- Adicione exemplos práticos relevantes à stack tecnológica
- Mantenha documentação em português brasileiro
- Garanta compatibilidade com a stack definida
- Utilize o comando `/ace-refine` para evoluir contexto
- Siga o fluxo obrigatório de cada harness

## Licença
Este projeto é proprietário e confidencial. Não é permitido compartilhar sem autorização expressa.

## Suporte
Para dúvidas ou sugestões:
- Consulte os Master Harnesses específicos
- Revise os exemplos práticos
- Utilize os comandos Cursor AI
- Consulte as referências externas em cada documento

---
**Última Atualização:** 15/01/2026  
**Versão:** 2.0.0  
**Status:** Todas as fases completas (100%)