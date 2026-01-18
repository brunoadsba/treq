import { test, expect } from '@playwright/test';

test.describe('Treq Agent - E2E Tests', () => {
    // Configuração prévia: assumindo que o backend e frontend estão rodando

    test.beforeEach(async ({ page }) => {
        // 0. Autenticar para obter token JWT (Usando mock admin no backend)
        const loginResponse = await page.request.post('http://localhost:8002/auth/login', {
            form: {
                username: 'admin',
                password: 'admin123',
            }
        });
        const loginData = await loginResponse.json();
        const token = loginData.access_token;

        // Navegar para a página inicial para poder setar localStorage
        await page.goto('/');
        await page.evaluate((t) => localStorage.setItem('treq_token', t), token);

        // Navegar para a página do agente
        await page.goto('/agent');
    });

    test('Deve responder corretamente a uma saudação', async ({ page }) => {
        // 1. Identificar input
        const input = page.locator('textarea[placeholder="Pergunte ao Agente Operacional..."]');
        await expect(input).toBeVisible();

        // 2. Enviar saudação "oi"
        await input.fill('oi');

        // O ChatInput geralmente tem um botão de envio ou enter
        await input.press('Enter');

        // Verificar se usuário enviou
        await expect(page.getByText('oi', { exact: true })).toBeVisible();

        // 3. Aguardar resposta
        // Procurar por qualquer bolha (loading ou resposta)
        // O selector agora pode esperar por loading ou bubble
        // 3. Aguardar resposta
        const agentBubble = page.getByTestId(/agent-bubble/);

        // Esperar que o bubble contenha a resposta 'Olá'
        const responseText = agentBubble.last().filter({ hasText: 'Olá' });
        await expect(responseText).toBeVisible({ timeout: 15000 });

        const bubbleContent = agentBubble.last();
        await expect(bubbleContent).toContainText('Treq');
        await expect(bubbleContent).not.toContainText('Sotreq');
        await expect(bubbleContent).toContainText('Olá');
    });

    test('Deve responder a uma pergunta de RAG sem vazar arquivos internos', async ({ page }) => {
        const input = page.locator('textarea[placeholder="Pergunte ao Agente Operacional..."]');
        await expect(input).toBeVisible();

        // Pergunta que poderia acionar RAG
        await input.fill('qual o procedimento de contenção?');
        await input.press('Enter');

        // Aguardar resposta do agente
        // Aguardar resposta do agente (qualquer texto longo que não seja 'thinking')
        const agentBubble = page.getByTestId(/agent-bubble/);
        const bubble = agentBubble.last();

        // Aumentar timeout pois RAG pode ser lento na primeira chamada (cold start)
        await expect(bubble).toBeVisible({ timeout: 30000 });

        // Garantir que não está vazio
        await expect(bubble).not.toBeEmpty();

        // Validar saneamento e branding com retry
        await expect(bubble).not.toContainText('.xlsx');
        await expect(bubble).not.toContainText('.pdf');
        await expect(bubble).not.toContainText('Base_Operacional');
        await expect(bubble).not.toContainText('Sotreq');
    });
});
