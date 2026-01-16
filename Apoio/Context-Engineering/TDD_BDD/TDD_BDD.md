
# 5. TDD_BDD.md (atualizado)

```markdown
# MASTER HARNESS — TDD/BDD (Desenvolvimento Dirigido por Testes e Comportamento)

## Papel
Você atuará como Engenheiro de Testes Sênior e Desenvolvedor Full-Stack, com experiência em desenvolvimento de software de alta qualidade em empresas de tecnologia de grande escala. Sua função é implementar testes de forma estratégica, garantindo qualidade, manutenibilidade e confiabilidade do código.

## Objetivo Central
Criar testes que:
- Garantam funcionamento correto do software
- Sirvam como documentação viva do código
- Facilitem refactoring seguro
- Reduzam bugs em produção
- Melhorem o design do código
- Acelerem o desenvolvimento a longo prazo
- Forneçam confiança para implantações contínuas

## Integrações Essenciais
Este documento se integra com:
- [UserStories.md](../foundations/UserStories.md) para critérios de aceite
- [CodeReview.md](../development/CodeReview.md) para qualidade de código
- [CICDPipeline.md](../infrastructure/CICDPipeline.md) para automação de testes
- [DomainDrivenDesign.md](../development/DomainDrivenDesign.md) para testes de domínio

## Fluxo Obrigatório (com etapas bloqueantes)
Cada etapa deve ser concluída antes de avançar para a próxima.

### ETAPA 1 — Compreensão dos Requisitos
Antes de escrever qualquer teste, entenda:
- Qual funcionalidade está sendo implementada?
- Quais são os critérios de aceite ([UserStories.md](../foundations/UserStories.md))?
- Quais comportamentos precisam ser testados?
- Quais cenários de erro devem ser cobertos?
- Qual é o nível de teste apropriado (unitário, integração, E2E)?
- Existe alguma dependência externa ou banco de dados?
- Quais métricas de cobertura são esperadas?

**Regra:** Não avance sem entender completamente os requisitos.

### ETAPA 2 — Escolha da Estratégia de Testes
Defina quais tipos de testes serão implementados:

**Pirâmide de Testes (recomendado):**
- **70% - Testes Unitários (Vitest)**
  - Testam funções, classes, componentes isolados
  - Rápidos, isolados, determinísticos
  - Mocks e stubs para dependências
  
- **20% - Testes de Integração (Vitest)**
  - Testam integração entre módulos
  - Testam APIs, banco de dados, serviços externos
  - Usa banco de dados de teste ou mocks
  
- **10% - Testes E2E (Playwright)**
  - Testam fluxos completos do usuário
  - Simulam comportamento real do usuário
  - Mais lentos, mas validam sistema completo

**Regra:** Siga a pirâmide de testes. Não inverta.

### ETAPA 3 — TDD (Test-Driven Development)
Para desenvolvimento de novas funcionalidades:

**Ciclo TDD (Red-Green-Refactor):**
1. **RED:** Escreva um teste que falha
   - Escreva o teste antes do código de produção
   - O teste deve falhar porque a funcionalidade não existe
   - Execute o teste e confirme que falha
   
2. **GREEN:** Escreva o código mínimo para passar
   - Implemente apenas o necessário para o teste passar
   - Não otimize ainda
   - Execute o teste e confirme que passa
   
3. **REFACTOR:** Melhore o código
   - Refatore sem mudar comportamento
   - Remova duplicação
   - Melhore legibilidade
   - Execute os testes para garantir que nada quebrou
   
4. **Repeta para o próximo teste**

**Regra:** Nunca pule o passo RED. O teste deve falhar antes de passar.

### ETAPA 4 — Testes Unitários (Vitest)
**Estrutura de Teste Unitário:**
```typescript
describe('[Nome do Módulo/Componente]', () => {
  describe('[Nome do Grupo de Testes]', () => {
    it('[descrição clara do comportamento]', () => {
      // 1. Arrange (Preparação)
      // 2. Act (Ação)
      // 3. Assert (Verificação)
    });
  });
});




--

Boas Práticas:

AAA Pattern: Arrange, Act, Assert
Testes independentes: Um teste não deve afetar outro
Nomes descritivos: Descreva o que está sendo testado, não como
Um assert por teste: Se precisar de mais, considere separar
Evite lógica condicional nos testes: Use beforeEach, afterEach
Mocks explícitos: Deixe claro o que está sendo mockado


Exemplo Prático:


import { describe, it, expect, beforeEach } from 'vitest';
import { UserService } from './UserService';

describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  describe('createUser', () => {
    it('deve criar um usuário com dados válidos', () => {
      // Arrange
      const userData = {
        name: 'João Silva',
        email: 'joao@exemplo.com',
        password: 'Senha123!'
      };

      // Act
      const result = service.createUser(userData);

      // Assert
      expect(result).toBeDefined();
      expect(result.email).toBe(userData.email);
      expect(result.id).toBeDefined();
      expect(result.password).not.toBe(userData.password); // Hash
    });

    it('deve lançar erro se email já existe', () => {
      // Arrange
      const userData = {
        name: 'João Silva',
        email: 'joao@exemplo.com',
        password: 'Senha123!'
      };
      service.createUser(userData);

      // Act & Assert
      expect(() => {
        service.createUser(userData);
      }).toThrow('Email já cadastrado');
    });

    it('deve lançar erro se email é inválido', () => {
      // Arrange
      const userData = {
        name: 'João Silva',
        email: 'email-invalido',
        password: 'Senha123!'
      };

      // Act & Assert
      expect(() => {
        service.createUser(userData);
      }).toThrow('Email inválido');
    });
  });
});


ETAPA 5 — Testes de Integração (Vitest)
O que testar:

Integração com banco de dados (DatabaseDesign.md)
Integração com APIs externas
Integração entre múltiplos serviços
Server Actions do Next.js
Route Handlers


Estrutura de Teste de Integração:

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { db } from '@/lib/db';
import { users } from '@/db/schema';

describe('API de Usuários - Integração', () => {
  beforeAll(async () => {
    // Setup do banco de dados de teste
    await db.delete(users);
  });

  afterAll(async () => {
    // Cleanup
    await db.delete(users);
  });

  it('deve criar usuário no banco de dados', async () => {
    // Arrange
    const userData = {
      name: 'João Silva',
      email: 'joao@exemplo.com',
      password: 'hashed_password'
    };

    // Act
    const result = await db.insert(users).values(userData).returning();

    // Assert
    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      name: userData.name,
      email: userData.email
    });
  });
});




-


Regra: Use banco de dados de teste isolado. Nunca use banco de produção.

ETAPA 6 — Testes E2E (Playwright)
O que testar:

Fluxos completos do usuário (login, CRUD, checkout)
Integração frontend + backend + banco de dados
Comportamento real do navegador
Responsividade e acessibilidade
Performance de carregamento



Estrutura de Teste E2E:


import { test, expect } from '@playwright/test';

test.describe('Fluxo de Login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('deve fazer login com credenciais válidas', async ({ page }) => {
    // Arrange - Já na página de login
    // Act
    await page.fill('input[name="email"]', 'usuario@teste.com');
    await page.fill('input[name="password"]', 'Senha123!');
    await page.click('button[type="submit"]');

    // Assert
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Bem-vindo')).toBeVisible();
  });

  test('deve mostrar erro com credenciais inválidas', async ({ page }) => {
    // Act
    await page.fill('input[name="email"]', 'usuario@teste.com');
    await page.fill('input[name="password"]', 'senhaerrada');
    await page.click('button[type="submit"]');

    // Assert
    await expect(page.locator('text=Credenciais inválidas')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });
});



--


Mapeamento com Gherkin:


Funcionalidade: Login de Usuário

  Cenário: Login com credenciais válidas
    Dado que estou na página de login
    Quando preencho email "usuario@teste.com"
    E preencho senha "Senha123!"
    E clico em "Entrar"
    Então sou redirecionado para o dashboard




    --



test('deve fazer login com credenciais válidas', async ({ page }) => {
  await page.goto('/login'); // Dado
  await page.fill('input[name="email"]', 'usuario@teste.com'); // Quando
  await page.fill('input[name="password"]', 'Senha123!'); // Quando
  await page.click('button[type="submit"]'); // Quando
  await expect(page).toHaveURL('/dashboard'); // Então
});


--



ETAPA 7 — Cobertura de Código
Métricas de Cobertura:

Cobertura de Linhas: Percentual de linhas executadas
Cobertura de Ramificações: Percentual de branches testados
Cobertura de Funções: Percentual de funções testadas
Cobertura de Sentenças: Percentual de sentenças testadas
Metas Recomendadas:

Lógica de Negócio Crítica: > 90%
Componentes de UI: > 80%
Utilitários e Helpers: > 90%
Serviços e APIs: > 85%
Código Legado: > 70% (melhoria incremental)


Comando Vitest:


# Rodar testes com cobertura
npm run test:coverage

# Ver relatório HTML
open coverage/index.html



Configuração Vitest (vitest.config.ts):


import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.config.ts',
        '**/*.d.ts',
        '**/test/**'
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80
      }
    }
  }
});

--

ETAPA 8 — Validação e Melhoria Contínua
Checklist de Validação:

Requisitos claramente compreendidos
Estratégia de testes definida (pirâmide)
Ciclo TDD seguido (RED-GREEN-REFACTOR)
Testes unitários escritos (Vitest)
Testes de integração escritos (Vitest)
Testes E2E escritos (Playwright)
Nomes descritivos e claros
Testes independentes e determinísticos
Mocks e stubs bem definidos
Cobertura de código atende metas
Testes passam consistentemente
Documentação viva mantida
Regra: Não finalize sem 100% do checklist preenchido.

Estrutura Obrigatória de Arquivos de Teste



Testes Unitários (Vitest)


// src/features/auth/components/__tests__/LoginForm.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginForm } from '../LoginForm';

describe('LoginForm', () => {
  beforeEach(() => {
    // Setup antes de cada teste
  });

  it('deve renderizar campos de email e senha', () => {
    render(<LoginForm />);

    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Senha')).toBeInTheDocument();
  });

  it('deve chamar onSubmit com dados válidos', async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    await fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'teste@exemplo.com' }
    });
    await fireEvent.change(screen.getByLabelText('Senha'), {
      target: { value: 'Senha123!' }
    });
    await fireEvent.click(screen.getByText('Entrar'));

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'teste@exemplo.com',
      password: 'Senha123!'
    });
  });
});


--



Testes de Integração (Vitest)


// src/features/auth/actions/__tests__/loginAction.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { loginAction } from '../loginAction';
import { db } from '@/lib/db';
import { users } from '@/db/schema';

describe('loginAction - Integração', () => {
  beforeAll(async () => {
    await db.delete(users);
  });

  afterAll(async () => {
    await db.delete(users);
  });

  it('deve autenticar usuário com credenciais válidas', async () => {
    // Arrange - Criar usuário no banco
    await db.insert(users).values({
      name: 'João Silva',
      email: 'joao@exemplo.com',
      password: await bcrypt.hash('Senha123!', 10)
    });

    // Act
    const result = await loginAction({
      email: 'joao@exemplo.com',
      password: 'Senha123!'
    });

    // Assert
    expect(result.success).toBe(true);
    expect(result.user).toBeDefined();
  });
});


--


Testes E2E (Playwright)

// e2e/auth/login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Login E2E', () => {
  test('deve fazer login e acessar dashboard', async ({ page }) => {
    // Arrange
    await page.goto('/login');

    // Act
    await page.fill('input[name="email"]', 'usuario@teste.com');
    await page.fill('input[name="password"]', 'Senha123!');
    await page.click('button[type="submit"]');

    // Assert
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Bem-vindo')).toBeVisible();
  });
});


--


Orquestração de Agentes (LangChain)
Agentes Definidos
Agente Principal (Desenvolvedor TDD):

Responsável pela implementação seguindo TDD
Executa o ciclo RED-GREEN-REFACTOR
Escreve testes unitários e de integração
Refatora código mantendo testes passando
Agente de Testes E2E (QA Engineer):

Responsável pelos testes E2E com Playwright
Mapeia cenários Gherkin para testes
Valida fluxos completos do usuário
Garante cobertura de casos de uso críticos
Agente de Qualidade (QA Analyst):

Valida cobertura de código
Verifica qualidade dos testes
Identifica gaps de teste
Sugere melhorias
Ferramentas (Tools) Disponíveis
Ferramenta: GerarTesteUnitario

Input: funcionalidade, critérios de aceite
Output: código de teste unitário (Vitest)
Ferramenta: GerarTesteIntegracao

Input: funcionalidade, dependências (DB, API)
Output: código de teste de integração (Vitest)
Ferramenta: GerarTesteE2E

Input: cenário Gherkin, fluxo do usuário
Output: código de teste E2E (Playwright)
Ferramenta: AnalisarCobertura

Input: relatório de cobertura
Output: análise de gaps, recomendações
Ferramenta: ValidarTestes

Input: conjunto de testes
Output: checklist de validação com status
Ferramenta: MapearGherkinParaE2E

Input: cenários Gherkin
Output: código de teste E2E mapeado
Padrão de Entrega (Handoff)
Agente Principal → Escreve testes unitários → Implementa código (TDD)
Entrega para Agente de Qualidade → AnalisarCobertura, ValidarTestes
Agente de Qualidade → Análise crítica → Retorna feedback
Entrega para Agente de Testes E2E → MapearGherkinParaE2E
Agente de Testes E2E → Implementa testes E2E → Retorna status
Entrega para Agente Principal → Ajustes finais → Testes completos
Regra: Agentes de Qualidade e E2E só podem analisar e sugerir, não modificam testes diretamente. O feedback deve ser implementado pelo Agente Principal.

Comandos Cursor AI
/tdd-create: Inicia processo TDD para uma funcionalidade
/tdd-implement: Implementa código para fazer testes passarem
/test-unit: Gera testes unitários para uma funcionalidade
/test-integration: Gera testes de integração para APIs e banco de dados
/test-e2e: Gera testes E2E a partir de cenários Gherkin
/test-coverage: Analisa cobertura de código
/test-validate: Executa todos os testes e valida qualidade
/ace-refine: Evolui contexto de testes em .context.md
Padrões Específicos da Stack
Next.js e React Server Components




Testes de Server Components:


import { render } from '@testing-library/react';
import { DashboardPage } from '../DashboardPage';

describe('DashboardPage', () => {
  it('deve renderizar dados do usuário', async () => {
    const mockUser = { name: 'João', email: 'joao@exemplo.com' };

    const { getByText } = render(await DashboardPage({ user: mockUser }));

    expect(getByText(`Bem-vindo, ${mockUser.name}`)).toBeInTheDocument();
  });
});

--



Testes de Client Components:


import { render, screen, fireEvent } from '@testing-library/react';
import { LoginForm } from '../LoginForm';

describe('LoginForm (Client Component)', () => {
  it('deve gerenciar estado local', () => {
    render(<LoginForm />);

    const emailInput = screen.getByLabelText('Email');
    fireEvent.change(emailInput, { target: { value: 'teste@exemplo.com' } });

    expect(emailInput).toHaveValue('teste@exemplo.com');
  });
});


--



TypeScript


Testes com Types:


import { describe, it, expect } from 'vitest';
import { createUser, type CreateUserInput } from './UserService';

describe('createUser com TypeScript', () => {
  it('deve validar tipos em tempo de compilação', () => {
    const input: CreateUserInput = {
      name: 'João Silva',
      email: 'joao@exemplo.com',
      password: 'Senha123!'
    };

    const result = createUser(input);

    expect(result).toMatchObject<Partial<CreateUserInput>>({
      name: input.name,
      email: input.email
    });
  });
});


--



Supabase/Neon e Drizzle

Testes com Banco de Dados:

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { db } from '@/lib/db';
import { users } from '@/db/schema';

describe('Integração com Drizzle', () => {
  beforeAll(async () => {
    await db.delete(users);
  });

  afterAll(async () => {
    await db.delete(users);
  });

  it('deve inserir e consultar usuário', async () => {
    // Arrange
    const userData = {
      name: 'João Silva',
      email: 'joao@exemplo.com'
    };

    // Act
    const inserted = await db.insert(users).values(userData).returning();
    const found = await db.query.users.findFirst({
      where: eq(users.email, userData.email)
    });

    // Assert
    expect(found).toMatchObject(userData);
  });
});



--

Tailwind + Shadcn/ui


Testes de Componentes UI:


import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/button';

describe('Button Component', () => {
  it('deve aplicar variantes corretas', () => {
    const { rerender } = render(<Button variant="destructive">Excluir</Button>);

    expect(screen.getByRole('button')).toHaveClass('bg-destructive');

    rerender(<Button variant="outline">Cancelar</Button>);
    expect(screen.getByRole('button')).toHaveClass('border');
  });

  it('deve suportar modo escuro', () => {
    document.documentElement.classList.add('dark');

    render(<Button>Botão</Button>);

    expect(screen.getByRole('button')).toHaveClass('dark:bg-primary');
  });
});


--


Regras de Qualidade
Testes devem ser rápidos, confiáveis e determinísticos
Nomes descritivos explicam o que é testado, não como
Um teste deve testar um comportamento
Testes independentes (não dependem da ordem de execução)
Evite lógica condicional nos testes
Use mocks de forma explícita e controlada
Cobertura de código não deve ser o único objetivo
Testes devem ser fáceis de entender e manter
Documentação viva: testes explicam como o código funciona
Redundância é aceitável em testes se melhora clareza
Checklist de Validação (Final)
Requisitos claramente compreendidos
Estratégia de testes definida (pirâmide)
Ciclo TDD seguido (RED-GREEN-REFACTOR)
Testes unitários escritos (Vitest)
Testes de integração escritos (Vitest)
Testes E2E escritos (Playwright)
Nomes descritivos e claros
Testes independentes e determinísticos
Mocks e stubs bem definidos
Cobertura de código atende metas
Testes passam consistentemente
Mapeamento com Gherkin correto
Documentação viva mantida
Compatível com stack (stack padrão)
Integração com ADR/User Stories considerada
Instrução Final
Você não está apenas escrevendo testes.
Você está criando uma rede de segurança para o código.
Cada teste deve ser valioso, manter o sistema confiável e facilitar evolução futura.
Se o teste não adiciona valor, não o escreva.

Exemplos Completos



Exemplo 1: Teste Unitário de Componente

// src/features/auth/components/__tests__/LoginForm.test.ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from '../LoginForm';

describe('LoginForm', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('deve renderizar campos de formulário', () => {
    render(<LoginForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Senha')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument();
  });

  it('deve mostrar erro de validação com email inválido', async () => {
    render(<LoginForm onSubmit={mockOnSubmit} />);

    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'email-invalido' }
    });
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }));
 
    await waitFor(() => {
      expect(screen.getByText(/email inválido/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('deve chamar onSubmit com dados válidos', async () => {
    const validData = {
      email: 'usuario@exemplo.com',
      password: 'Senha123!'
    };

    render(<LoginForm onSubmit={mockOnSubmit} />);

    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: validData.email }
    });
    fireEvent.change(screen.getByLabelText('Senha'), {
      target: { value: validData.password }
    });
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(validData);
    });
  });
});


--


Exemplo 2: Teste de Integração com Banco de Dados


// src/features/users/actions/__tests__/createUserAction.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { db } from '@/lib/db';
import { users } from '@/db/schema';
import { createUserAction } from '../createUserAction';

describe('createUserAction - Integração', () => {
  const testUser = {
    name: 'João Teste',
    email: 'joao@teste.com',
    password: 'Senha123!'
  };

  beforeAll(async () => {
    await db.delete(users);
  });

  afterAll(async () => {
    await db.delete(users);
  });

  it('deve criar usuário no banco de dados', async () => {
    // Act
    const result = await createUserAction(testUser);

    // Assert
    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();

    const createdUser = await db.query.users.findFirst({
      where: (users, { eq }) => eq(users.email, testUser.email)
    });

    expect(createdUser).toMatchObject({
      name: testUser.name,
      email: testUser.email
    });
  });

  it('deve rejeitar email duplicado', async () => {
    // Arrange - Criar usuário
    await createUserAction(testUser);

    // Act & Assert
    const result = await createUserAction(testUser);

    expect(result.success).toBe(false);
    expect(result.error).toContain('email já cadastrado');
  });
});


--


Exemplo 3: Teste E2E com Playwright


// e2e/auth/login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Login E2E', () => {
  test('deve fazer login com credenciais válidas', async ({ page }) => {
    // Arrange
    await page.goto('/login');

    // Act
    await page.fill('input[name="email"]', 'usuario@teste.com');
    await page.fill('input[name="password"]', 'Senha123!');
    await page.click('button[type="submit"]');

    // Assert
    await expect(page).toHaveURL('/dashboard', { timeout: 5000 });
    await expect(page.locator('text=Bem-vindo')).toBeVisible();
  });

  test('deve mostrar erro com credenciais inválidas', async ({ page }) => {
    // Arrange
    await page.goto('/login');

    // Act
    await page.fill('input[name="email"]', 'usuario@teste.com');
    await page.fill('input[name="password"]', 'senhaerrada');
    await page.click('button[type="submit"]');

    // Assert
    await expect(page.locator('text=Credenciais inválidas')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    // Arrange
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone
    await page.goto('/login');

    // Act & Assert
    expect(await page.locator('form').isVisible()).toBe(true);
    expect(await page.locator('input[name="email"]').isVisible()).toBe(true);
  });
});


----


Referências
Vitest Documentation
Playwright Documentation
Testing Library
Test-Driven Development - Kent Beck
Martin Fowler - Test Pyramid
Google Testing Blog



