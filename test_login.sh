#!/bin/bash

echo "🔐 Testando Login Treq..."

# Teste 1: Login direto na API
echo "1. Testando API diretamente:"
TOKEN=$(curl -s -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ "$TOKEN" != "" ]; then
  echo "✅ API Login OK - Token: ${TOKEN:0:20}..."
else
  echo "❌ API Login FALHOU"
  exit 1
fi

# Teste 2: Verificar se token funciona
echo "2. Testando token:"
HEALTH=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8002/health | jq -r '.status')

if [ "$HEALTH" = "ok" ]; then
  echo "✅ Token válido"
else
  echo "❌ Token inválido"
fi

# Teste 3: Testar endpoint protegido
echo "3. Testando endpoint protegido:"
CHAT_TEST=$(curl -s -X POST http://localhost:8002/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "teste", "user_id": "test"}' | jq -r '.response // .detail')

if [[ "$CHAT_TEST" != *"Unauthorized"* ]] && [[ "$CHAT_TEST" != *"401"* ]]; then
  echo "✅ Endpoint protegido OK"
else
  echo "❌ Endpoint protegido FALHOU: $CHAT_TEST"
fi

echo ""
echo "🎯 Para usar no frontend:"
echo "Username: admin"
echo "Password: admin123"
echo "Token gerado: $TOKEN"
