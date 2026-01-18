# Estágio 1: Dependências
FROM node:18-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Estágio 2: Desenvolvimento (Hot-reload)
FROM node:18-alpine AS development
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=development
ENV NEXT_PUBLIC_API_URL=http://localhost:8002
# Permissões para o usuário node padrão do Alpine (UID 1000)
RUN chown -R node:node /app
USER node
CMD ["npm", "run", "dev"]

# Estágio 3: Builder para Produção
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_PUBLIC_API_URL=http://backend:8002
RUN npm run build

# Estágio 4: Runner de Produção
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
# O modo standalone coloca os arquivos em .next/standalone
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000

# Standalone mode usa o server.js gerado
CMD ["node", "server.js"]
