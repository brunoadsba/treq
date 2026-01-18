import { test, expect } from '@playwright/test';

test.describe('Navigation - E2E Tests', () => {
    test('Deve navegar entre Chat e Agente', async ({ page }) => {
        // Iniciar na home
        await page.goto('/');

        // Verificar se os links de navegação estão visíveis
        const nav = page.locator('nav[aria-label="Navegação principal"]');
        await expect(nav).toBeVisible();

        const chatLink = nav.getByRole('link', { name: 'Chat' });
        const agentLink = nav.getByRole('link', { name: 'Agente' });

        await expect(chatLink).toBeVisible();
        await expect(agentLink).toBeVisible();

        // Verificar estado inicial (assumindo /chat ou / como default)
        // Se estiver em '/', o botão 'Chat' deve estar ativo (aria-current='page')
        await expect(chatLink).toHaveAttribute('aria-current', 'page');

        // Navegar para Agente
        await agentLink.click();
        await expect(page).toHaveURL(/\/agent/);

        await expect(agentLink).toHaveAttribute('aria-current', 'page');
        await expect(chatLink).not.toHaveAttribute('aria-current');

        // Voltar para Chat
        await chatLink.click();
        await expect(page).toHaveURL(/\/chat/);
        await expect(chatLink).toHaveAttribute('aria-current', 'page');
    });
});
