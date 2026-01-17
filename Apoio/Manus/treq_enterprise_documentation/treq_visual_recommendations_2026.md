# Guia de Recomendações Visuais: Treq Enterprise 2026 (Dual Theme)

Este guia apresenta uma visão modernizada para a interface do Treq, agora com suporte completo a **Dark Mode** e **Light Mode (Clear)**, alinhada com as tendências de design de 2026.

## 1. Estratégia de Cores Adaptativa

A interface deve alternar fluidamente entre os modos, mantendo a identidade visual "Enterprise".

| Elemento | Modo Dark (Deep Slate) | Modo Light (Clear) | Justificativa |
| :--- | :--- | :--- | :--- |
| **Fundo Principal** | `#0A0A0C` (Deep Black) | `#F8F9FA` (Soft Gray) | Equilíbrio entre foco e clareza. |
| **Acento Primário** | `#D4AF37` (Metallic Gold) | `#FFCD00` (Vibrant Yellow) | Ouro para sofisticação no Dark; Amarelo para energia no Light. |
| **Superfícies (Cards)** | `#161618` | `#FFFFFF` | Profundidade e separação clara de conteúdo. |
| **Texto Primário** | `#F3F4F6` | `#111827` | Máximo contraste e legibilidade. |
| **Raciocínio (IA)** | Gradiente `Indigo/Violet` | Gradiente `Sky/Indigo` | Diferenciação visual do processamento da IA. |

## 2. Tipografia e Hierarquia

- **Fonte:** `Geist` ou `Inter` com suporte a *Variable Weights*.
- **Modo Dark:** Usar pesos ligeiramente menores (ex: `400` em vez de `500`) para evitar o efeito de "sangramento" do texto branco no fundo preto.
- **Modo Light:** Usar pesos padrão com `letter-spacing: -0.01em` para um visual mais denso e profissional.

## 3. Componentes Enterprise 2026

### Bento Grids Adaptativos
- **Dark:** Bordas sutis de `1px` com `rgba(255,255,255,0.05)`.
- **Light:** Sombras suaves (`box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05)`) em vez de bordas fortes.

### Glassmorphism (Efeito Vidro)
- Aplicar `backdrop-filter: blur(16px)` em ambos os modos.
- No **Light Mode**, usar uma opacidade de fundo de `0.7` para manter a legibilidade sobre elementos coloridos.

## 4. Micro-interações de IA
- **Glow Effect:** No Dark Mode, a borda da mensagem brilha em dourado enquanto a IA "pensa". No Light Mode, usamos uma pulsação suave de sombra amarela.
- **Handoff Visual:** O campo de input muda para uma borda dourada (Dark) ou amarela vibrante (Light) quando a IA aguarda uma ação do usuário.

## 5. Dashboard de Insights (Home)
A nova Home deve ser um painel de controle que se adapta ao tema:
- **Gráficos:** Usar paletas de cores que funcionem em ambos os fundos (ex: tons de azul e esmeralda).
- **Cards de Status:** Indicadores de saúde operacional com ícones minimalistas e cores funcionais (Success/Warning/Error) consistentes.

---

**Conclusão:** O Treq Enterprise 2026 oferece uma experiência **"Context-Aware"**. A interface não é apenas bonita, mas funcional, adaptando-se ao ambiente de iluminação do usuário para garantir produtividade máxima em qualquer turno de trabalho.
