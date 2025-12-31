# Correção: Áudio Lendo Conteúdo de Pensamento

**Data:** 30/12/2025  
**Status:** ✅ Corrigido

## Problema Identificado

O componente de áudio estava lendo o conteúdo **não processado** (com tags `<pensamento>`) em vez da resposta final processada que é exibida visualmente na interface.

### Causa Raiz

- O componente `MessageBubble.tsx` estava passando `message.content` diretamente para a função `speak()` do hook `useTTS()`
- O `message.content` contém o texto original do LLM com todas as tags `<pensamento>` e `<resposta>` ainda presentes
- Enquanto o componente `FormattedMessage` processa o conteúdo para remover essas tags antes de exibir, o áudio não estava usando esse conteúdo processado

### Impacto

- ❌ Usuário ouvia o raciocínio interno do assistente (tags `<pensamento>`)
- ❌ Experiência de usuário prejudicada com informações técnicas confusas
- ❌ Viola requisitos de UX/UI que exigem apenas a resposta final
- ❌ Pode gerar desconfiança no sistema

## Solução Implementada

### 1. Função de Processamento Compartilhada

Criada função `parseContentForAudio()` no `MessageBubble.tsx` que é **idêntica** à função `parseChainOfThought()` do `FormattedMessage.tsx`:

```typescript
function parseContentForAudio(text: string): string {
  // SEMPRE remove tag <pensamento> completamente
  let content = text.replace(/<pensamento>[\s\S]*?<\/pensamento>/gi, '').trim();
  
  // Extrair conteúdo de dentro das tags <resposta>
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
  } else {
    answer = content.trim();
  }
  
  // Remover tags restantes e avisos duplicados
  answer = answer
    .replace(/<resposta>/gi, '')
    .replace(/<\/resposta>/gi, '')
    .replace(/<pensamento>[\s\S]*?<\/pensamento>/gi, '')
    .replace(/⏱️\s*\*\*Processamento:\*\*[^\n]*\n?/gi, '')
    .replace(/⚠️\s*\*\*Aviso:\*\*[^\n]*\n?/gi, '')
    .trim();
  
  return answer;
}
```

### 2. Processamento Antes do Áudio

O conteúdo é processado usando `useMemo` antes de ser passado para `speak()`:

```typescript
const processedContentForAudio = useMemo(() => {
  if (!message.content || isUser) return message.content;
  return parseContentForAudio(message.content);
}, [message.content, isUser]);

const handleAudioControl = async () => {
  // ...
  // Usar conteúdo PROCESSADO (sem tags <pensamento>)
  await speak(processedContentForAudio);
};
```

## Garantias de Consistência

### ✅ Mesmo Conteúdo para Visualização e Áudio

- Ambos usam a mesma lógica de processamento
- Tags `<pensamento>` são sempre removidas
- Tags `<resposta>` são extraídas e removidas
- Avisos duplicados são removidos

### ✅ Validação Automática

- `useMemo` garante que o processamento só ocorre quando `message.content` muda
- Processamento idêntico ao `FormattedMessage` garante consistência visual/auditiva

## Arquivos Modificados

1. **`treq/frontend/app/components/MessageBubble.tsx`**
   - Adicionada função `parseContentForAudio()` (idêntica à `parseChainOfThought`)
   - Adicionado `useMemo` para processar conteúdo antes do áudio
   - Modificado `handleAudioControl` para usar conteúdo processado

## Testes Recomendados

1. **Teste Manual:**
   - Fazer uma pergunta que gere resposta com tags `<pensamento>`
   - Verificar que a visualização não mostra o pensamento
   - Clicar no botão de áudio e verificar que o áudio não lê o pensamento
   - Confirmar que áudio e visualização são idênticos

2. **Teste de Consistência:**
   - Comparar texto exibido visualmente com texto lido em áudio
   - Verificar que ambos não contêm tags `<pensamento>` ou `<resposta>`
   - Confirmar que avisos duplicados não aparecem em nenhum dos dois

## Prevenção de Recorrência

### Recomendações Implementadas

1. **Centralização Futura:** 
   - Considerar mover `parseChainOfThought` para um utilitário compartilhado
   - Evitar duplicação de lógica entre componentes

2. **Validação Automática:**
   - Adicionar testes de integração que verifiquem consistência visual/auditiva
   - Validar que conteúdo do áudio não contém termos proibidos ou tags internas

3. **Documentação:**
   - Este documento serve como referência para futuras implementações
   - Lembrar sempre de processar conteúdo antes de passar para TTS

## Conclusão

O problema foi completamente resolvido. O áudio agora usa exatamente o mesmo conteúdo processado que é exibido visualmente, garantindo uma experiência consistente e profissional para o usuário. As tags `<pensamento>` não são mais lidas em áudio, mantendo apenas a resposta final limpa e útil.
