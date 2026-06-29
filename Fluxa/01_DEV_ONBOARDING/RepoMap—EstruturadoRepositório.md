# Repo Map — Estrutura do Repositório

> **Onde encontrar cada coisa no código da Fluxa.**
>
> Este documento é o GPS do repositório. Qualquer dev novo deve lê-lo primeiro.

---

## Visão Geral

```
base-x/
├── client/              ← Frontend React (Vite + Tailwind 4)
├── server/              ← Backend Express + tRPC
├── drizzle/             ← Schema do banco + migrações
├── shared/              ← Tipos e constantes compartilhados
├── docs/                ← Documentação (você está aqui)
├── e2e/                 ← Testes end-to-end (Playwright)
├── scripts/             ← Scripts utilitários
└── [raiz]               ← Config (vite, vitest, tsconfig, package.json)
```

---

## `/client` — Frontend

```
client/
├── index.html                    ← HTML base (meta tags, fontes, PWA)
├── public/
│   ├── manifest.json             ← PWA manifest
│   ├── sw.js                     ← Service Worker (offline + push)
│   ├── favicon.svg               ← Ícone
│   ├── icon-192.png / icon-512.png  ← PWA icons
│   └── sitemap.xml               ← SEO
└── src/
    ├── App.tsx                   ← Rotas + layout principal
    ├── main.tsx                  ← Entry point (providers)
    ├── index.css                 ← Tema global (CSS vars, Tailwind)
    ├── pages/                    ← Páginas (1 arquivo = 1 rota)
    ├── components/               ← Componentes reutilizáveis
    │   ├── ui/                   ← shadcn/ui (button, card, dialog...)
    │   └── mission-control/      ← Componentes do Mission Control
    ├── hooks/                    ← Custom hooks
    ├── contexts/                 ← React contexts (Cart, Theme)
    ├── lib/
    │   └── trpc.ts              ← Cliente tRPC (conexão com backend)
    └── _core/
        └── hooks/useAuth.ts     ← Hook de autenticação
```

### Páginas por Persona

| Persona | Páginas principais |
|---|---|
| **Participante** | `Menu.tsx`, `MyOrders.tsx`, `MyTickets.tsx`, `TicketPurchase.tsx`, `Withdrawal.tsx`, `EventEntry.tsx` |
| **Produtor (Admin)** | `MissionControl.tsx`, `AdminDashboard.tsx`, `AdminEvents.tsx`, `AdminProducts.tsx`, `AdminOrders.tsx`, `AdminFinancials.tsx`, `AdminPostEvent.tsx` |
| **Operador (Staff)** | `StaffConsole.tsx`, `StaffKDS.tsx`, `StationKDS.tsx`, `StaffWithdrawal.tsx` |
| **Público (Landing)** | `Home.tsx`, `Onboarding.tsx`, `DemoShowcase.tsx`, `LiveDemo.tsx`, `PilotLanding.tsx` |
| **Sistema** | `Login.tsx`, `Register.tsx`, `NotFound.tsx`, `LGPD.tsx`, `PrivacyPolicy.tsx`, `TermsOfUse.tsx` |

---

## `/server` — Backend

```
server/
├── _core/                        ← Framework (NÃO MEXER sem necessidade)
│   ├── index.ts                  ← Express app + middlewares + webhooks
│   ├── trpc.ts                   ← Definição de procedures (public/protected/admin)
│   ├── context.ts                ← Context do tRPC (user, session)
│   ├── oauth.ts                  ← Manus OAuth flow
│   ├── cookies.ts                ← Configuração de cookies
│   ├── env.ts                    ← Variáveis de ambiente
│   ├── llm.ts                    ← Helper para chamar LLM
│   ├── notification.ts           ← Push notifications para owner
│   ├── imageGeneration.ts        ← Geração de imagens via IA
│   ├── voiceTranscription.ts     ← Transcrição de áudio
│   ├── heartbeat.ts              ← Jobs periódicos (cron)
│   ├── storageProxy.ts           ← Proxy para storage
│   ├── dataApi.ts                ← API de dados externos
│   ├── map.ts                    ← Google Maps proxy
│   ├── sdk.ts                    ← SDK interno
│   ├── systemRouter.ts           ← Router de sistema (notify owner)
│   └── vite.ts                   ← Integração Vite dev/prod
├── routers/                      ← Routers tRPC (lógica de negócio)
│   ├── orders.ts                 ← Pedidos + pagamento MP
│   ├── events.ts                 ← CRUD de eventos
│   ├── products.ts               ← Produtos + categorias
│   ├── ingredients.ts            ← Insumos + ficha técnica
│   ├── tickets.ts                ← Ingressos + check-in
│   ├── fluxaControl.ts           ← Mission Control (dashboard ao vivo)
│   ├── intelligence.ts           ← Alertas + sugestões IA
│   ├── syntropyPlanner.ts        ← Onboarding conversacional
│   ├── eventPlanner.ts           ← Planejamento de evento
│   ├── aiInsights.ts             ← Insights IA + ações
│   ├── offlineOrders.ts          ← Modo offline
│   ├── withdrawal.ts             ← Retirada de itens (QR)
│   ├── stationTokens.ts          ← Tokens de estação (KDS)
│   ├── stripe.ts                 ← Pagamento Stripe
│   ├── stripeConnect.ts          ← Split via Stripe Connect
│   ├── plans.ts                  ← Planos de assinatura
│   ├── pilot.ts                  ← Programa piloto
│   ├── refunds.ts                ← Estornos
│   ├── menuTemplates.ts          ← Templates de cardápio
│   ├── auth.ts                   ← Autenticação + MFA
│   ├── seed.ts                   ← Dados demo
│   └── shared.ts                 ← staffProcedure (shared)
├── intelligence-engine.ts        ← Motor de inteligência (Syntropy runtime)
├── dispatch.ts                   ← Smart Routing (distribuição de pedidos)
├── scheduled-ia-analysis.ts      ← Análise IA periódica (heartbeat)
├── scheduled-invoice-collection.ts ← Cobrança de faturas
├── mercadopago.ts                ← SDK Mercado Pago
├── stripe.ts                     ← SDK Stripe
├── pagarme.ts                    ← SDK Pagar.me (legado)
├── pushNotification.ts           ← Push notifications (VAPID)
├── weather.ts                    ← Integração clima
├── plans.ts                      ← Definição de planos
├── sentry.ts                     ← Monitoramento de erros
├── storage.ts                    ← S3 helpers
├── db.ts                         ← Query helpers (Drizzle)
├── ai/
│   └── safeInvokeLLM.ts         ← Wrapper seguro para LLM
└── *.test.ts                     ← Testes unitários (vitest)
```

---

## `/drizzle` — Banco de Dados

```
drizzle/
├── schema.ts                     ← TODAS as tabelas (fonte de verdade)
├── relations.ts                  ← Relações entre tabelas
├── 0000_*.sql ... 0054_*.sql     ← Migrações SQL (em ordem)
└── meta/
    ├── _journal.json             ← Histórico de migrações
    └── *.snapshot.json           ← Snapshots do schema
```

---

## `/shared` — Compartilhado

```
shared/
├── const.ts                      ← Constantes (status, enums)
├── types.ts                      ← Tipos TypeScript compartilhados
└── _core/
    └── errors.ts                 ← Tipos de erro padrão
```

---

## Raiz — Configuração

| Arquivo | Função |
|---|---|
| `package.json` | Dependências + scripts |
| `vite.config.ts` | Build config (client + server) |
| `vitest.config.ts` | Config de testes |
| `tsconfig.json` | TypeScript config |
| `AGENTS.md` | Constituição para IAs/devs |
| `todo.md` | Backlog de features/bugs |

---

## Arquivos Legados (raiz)

Estes arquivos na raiz são documentação/QA de sprints anteriores. Não fazem parte do runtime:

```
AUDIT-BP-v16-ALIGNMENT.md, AUDITORIA-FLUXA.md, BRAND-ARCHITECTURE.md,
FEATURES.md, FLUXA-IDENTIDADE.md, FLUXA-MAPA-DE-FLUXOS.md,
QA-*.md, ROADMAP_EVENTO_REAL.md, SPEC-MISSION-CONTROL.md, etc.
```

---

## Convenções

| Convenção | Regra |
|---|---|
| Nomes de arquivo | `camelCase.ts` para código, `UPPER_CASE.md` para docs |
| Páginas | 1 arquivo = 1 rota (nome = funcionalidade) |
| Routers | 1 arquivo = 1 domínio (orders, events, products...) |
| Testes | `*.test.ts` ao lado do arquivo testado |
| Migrações | Nunca editar manualmente — usar `pnpm drizzle-kit generate` |
| Imagens | Nunca no repo — usar `manus-upload-file --webdev` |


---


# Feature → File Map

> **Precisa mexer em algo? Encontre aqui qual arquivo abrir.**

---

## Fluxo do Participante

| Funcionalidade | Backend | Frontend | Schema |
|---|---|---|---|
| Ver cardápio | `routers/products.ts` | `pages/Menu.tsx` | `products`, `categories` |
| Fazer pedido | `routers/orders.ts` | `pages/Menu.tsx` (CartContext) | `orders`, `orderItems` |
| Pagar com Pix (MP) | `routers/orders.ts`, `mercadopago.ts` | `pages/Menu.tsx` | `orders` |
| Pagar com cartão (MP) | `routers/stripe.ts` (payMpCard) | `components/MercadoPagoCardForm.tsx` | `orders` |
| Pagar com cartão (Stripe) | `routers/stripe.ts` | `components/StripePaymentForm.tsx` | `orders` |
| Apple/Google Pay | `routers/stripe.ts` | `components/ExpressCheckout.tsx` | `orders` |
| Acompanhar pedido | `routers/orders.ts` (queuePosition) | `pages/MyOrders.tsx` | `orders` |
| Retirar item (QR) | `routers/withdrawal.ts` | `pages/Withdrawal.tsx` | `withdrawalTokens` |
| Comprar ingresso | `routers/tickets.ts` | `pages/TicketPurchase.tsx` | `ticketTypes`, `ticketPurchases` |
| Meus ingressos | `routers/tickets.ts` | `pages/MyTickets.tsx` | `ticketPurchases` |
| Push notifications | `pushNotification.ts` | `hooks/usePushNotifications.ts` | `pushSubscriptions` |

---

## Fluxo do Produtor (Admin)

| Funcionalidade | Backend | Frontend | Schema |
|---|---|---|---|
| Mission Control (ao vivo) | `routers/fluxaControl.ts` | `pages/MissionControl.tsx` | múltiplas |
| Criar evento (Syntropy) | `routers/syntropyPlanner.ts` | `pages/Onboarding.tsx`, `SyntropyEventCreator.tsx` | `events` |
| Planejar evento | `routers/eventPlanner.ts` | `pages/AdminEventPlanner.tsx` | `events` |
| Gerenciar eventos | `routers/events.ts` | `pages/AdminEvents.tsx` | `events` |
| Gerenciar produtos | `routers/products.ts` | `pages/AdminProducts.tsx` | `products`, `categories` |
| Gerenciar insumos | `routers/ingredients.ts` | `pages/AdminIngredients.tsx` | `ingredients`, `productIngredients` |
| Monitorar estoque | `routers/fluxaControl.ts` | `pages/AdminStockMonitor.tsx` | `stockMovements`, `ingredients` |
| Reconciliar estoque | `routers/ingredients.ts` | `pages/AdminStockReconciliation.tsx` | `ingredientMovements` |
| Ver pedidos | `routers/orders.ts` | `pages/AdminOrders.tsx` | `orders`, `orderItems` |
| Financeiro | `routers/fluxaControl.ts` | `pages/AdminFinancials.tsx` | `orders`, `splitTransactions` |
| Recebimentos | `routers/stripeConnect.ts` | `pages/AdminRecebimentos.tsx` | `splitConfigs` |
| Split (repasse) | `routers/stripeConnect.ts` | `pages/AdminSplit.tsx` | `splitConfigs`, `splitTransactions` |
| Promoções | `routers/fluxaControl.ts` | `pages/AdminPromos.tsx` | `promos` |
| Ingressos | `routers/tickets.ts` | `pages/AdminTickets.tsx` | `ticketTypes` |
| Check-in | `routers/tickets.ts` | `pages/AdminCheckIn.tsx` | `ticketPurchases`, `eventEntries` |
| Open Bar | `routers/events.ts` | `pages/AdminOpenBar.tsx` | `openBarTracking` |
| CRM | `routers/fluxaControl.ts` | `pages/AdminCRM.tsx` | `participantProfiles` |
| Contratos | `routers/events.ts` | `pages/AdminContracts.tsx`, `ContractSign.tsx` | `contracts` |
| Leads | `routers/events.ts` | `pages/AdminLeads.tsx` | `leads` |
| Analytics | `routers/fluxaControl.ts` | `pages/AdminAnalytics.tsx` | múltiplas |
| Relatório pós-evento | `intelligence-engine.ts` | `pages/AdminPostEvent.tsx` | `aiInsights`, `iaActions` |
| Syntropy Vision | `intelligence-engine.ts` | `pages/AdminSyntropyVision.tsx` | `aiInsights` |
| Inteligência (alertas) | `routers/intelligence.ts` | `pages/AdminIntelligence.tsx` | `aiInsights`, `iaActions` |
| AI Manager | `routers/aiInsights.ts` | `pages/AdminAIManager.tsx` | `aiInsights`, `iaActions` |
| Pontos de venda | `routers/events.ts` | `pages/AdminSalePoints.tsx` | `salePoints` |
| QR Codes | `routers/events.ts` | `pages/AdminQRCodes.tsx` | `tablesQr` |
| Segurança | `routers/auth.ts` | `pages/AdminSecurityDashboard.tsx` | `securityAlerts`, `auditLogs` |
| Planos | `routers/plans.ts` | `pages/AdminPlano.tsx` | — |
| Faturas | `scheduled-invoice-collection.ts` | `pages/AdminFaturas.tsx` | `eventInvoices` |
| Estornos | `routers/refunds.ts` | `pages/AdminRefunds.tsx` | `refundRequests`, `paymentRefunds` |
| Programa piloto | `routers/pilot.ts` | `pages/AdminPilotInvites.tsx` | `pilotInvites`, `pilotFeedback` |

---

## Fluxo do Operador (Staff)

| Funcionalidade | Backend | Frontend | Schema |
|---|---|---|---|
| Console de pedidos | `routers/orders.ts` | `pages/StaffConsole.tsx` | `orders` |
| KDS (Kitchen Display) | `routers/orders.ts`, `stationTokens.ts` | `pages/StaffKDS.tsx`, `StationKDS.tsx` | `orders`, `stationTokens` |
| Retirada (staff) | `routers/withdrawal.ts` | `pages/StaffWithdrawal.tsx` | `withdrawalTokens` |
| Pedidos offline | `routers/offlineOrders.ts` | hooks: `useOfflineStaff.ts` | `offlineOrders` |
| Push (staff) | `pushNotification.ts` | — | `staffPushSubscriptions` |

---

## Inteligência (Syntropy)

| Funcionalidade | Backend | Frontend |
|---|---|---|
| Motor de inteligência | `intelligence-engine.ts` | — |
| Smart Routing | `dispatch.ts` | — |
| Análise periódica | `scheduled-ia-analysis.ts` | — |
| Previsão climática | `weather.ts` | — |
| Onboarding conversacional | `routers/syntropyPlanner.ts` | `pages/Onboarding.tsx` |
| Relatório pós-evento (Vision) | `intelligence-engine.ts` | `pages/AdminPostEvent.tsx` |
| Alertas + sugestões | `routers/intelligence.ts`, `aiInsights.ts` | `pages/AdminIntelligence.tsx` |
| CRV (Customer Revenue Value) | `routers/fluxaControl.ts` | `pages/AdminCRV.tsx` |

---

## Infraestrutura

| Funcionalidade | Arquivo |
|---|---|
| Webhooks MP | `server/_core/index.ts` (rota `/api/webhooks/mercadopago`) |
| Webhooks Stripe | `server/_core/index.ts` (rota `/api/webhooks/stripe`) |
| OAuth | `server/_core/oauth.ts` |
| Push VAPID | `server/pushNotification.ts` |
| Service Worker | `client/public/sw.js` |
| Jobs periódicos | `server/_core/heartbeat.ts` |
| Sentry | `server/sentry.ts` |
| Storage (S3) | `server/storage.ts` |


---


# Backend Architecture

> **Todos os routers, suas responsabilidades e níveis de criticidade.**

---

## Stack

- **Runtime:** Node.js 22 (single process)
- **Framework:** Express 4 + tRPC 11
- **ORM:** Drizzle (MySQL/TiDB)
- **Auth:** Manus OAuth + JWT cookies
- **Serialização:** Superjson (Date, BigInt preservados)

---

## Níveis de Acesso

| Procedure | Quem pode usar | Onde definido |
|---|---|---|
| `publicProcedure` | Qualquer pessoa (sem login) | `server/_core/trpc.ts` |
| `protectedProcedure` | Usuário logado | `server/_core/trpc.ts` |
| `adminProcedure` | Usuário com role=admin | `server/_core/trpc.ts` |
| `staffProcedure` | Staff autenticado por token | `server/routers/shared.ts` |

---

## Routers — Visão Geral

### CRÍTICOS (nunca alterar sem teste completo)

| Router | Responsabilidade | Risco se quebrar |
|---|---|---|
| `orders.ts` | Criar pedido, pagamento Pix/MP, webhook, status | **Perda de receita** |
| `stripe.ts` | Pagamento cartão, MP Card, Express Checkout | **Perda de receita** |
| `fluxaControl.ts` | Dashboard ao vivo, métricas, estoque, CRM | **Produtor cego** |
| `intelligence-engine.ts` | Motor Syntropy (alertas, sugestões, Vision) | **IA para** |
| `dispatch.ts` | Smart Routing (distribuição de pedidos) | **Pedidos perdidos** |
| `stationTokens.ts` | Autenticação de estações KDS | **Bar não recebe pedidos** |
| `withdrawal.ts` | Retirada de itens via QR | **Participante não retira** |

### IMPORTANTES (testar antes de deploy)

| Router | Responsabilidade |
|---|---|
| `events.ts` | CRUD de eventos, pontos de venda, contratos, QR codes, leads |
| `products.ts` | Produtos, categorias, imagens, estoque |
| `ingredients.ts` | Insumos, ficha técnica, movimentações, reconciliação |
| `tickets.ts` | Tipos de ingresso, compra, confirmação, check-in |
| `stripeConnect.ts` | Split de pagamentos, onboarding Stripe Connect |
| `offlineOrders.ts` | Pedidos offline (sync, pagamento posterior) |
| `refunds.ts` | Estornos (request, approve, reject) |
| `auth.ts` | Login, MFA, sessões, segurança |

### AUXILIARES (menor risco)

| Router | Responsabilidade |
|---|---|
| `syntropyPlanner.ts` | Chat conversacional para criar evento |
| `eventPlanner.ts` | Planejamento detalhado de evento |
| `aiInsights.ts` | CRUD de insights IA + ações |
| `intelligence.ts` | Listagem de alertas + sugestões |
| `menuTemplates.ts` | Templates de cardápio reutilizáveis |
| `plans.ts` | Planos de assinatura (Starter, Pro, Enterprise) |
| `pilot.ts` | Programa piloto (convites, feedback) |
| `seed.ts` | Criar dados demo |

---

## Serviços Standalone (fora dos routers)

| Arquivo | Função | Trigger |
|---|---|---|
| `intelligence-engine.ts` | Motor Syntropy completo | Chamado por heartbeat + routers |
| `dispatch.ts` | Smart Routing de pedidos | Chamado por orders.ts ao criar pedido |
| `scheduled-ia-analysis.ts` | Análise IA periódica | Heartbeat (cron) |
| `scheduled-invoice-collection.ts` | Cobrança de faturas | Heartbeat (cron) |
| `mercadopago.ts` | SDK MP (criar pagamento, verificar) | Chamado por orders.ts |
| `stripe.ts` (server/) | SDK Stripe (payment intent) | Chamado por routers/stripe.ts |
| `pushNotification.ts` | Enviar push (VAPID) | Chamado por orders, intelligence |
| `weather.ts` | Buscar previsão do tempo | Chamado por intelligence-engine |
| `plans.ts` (server/) | Definição de planos e limites | Importado por routers/plans.ts |

---

## Webhooks

| Endpoint | Origem | O que faz |
|---|---|---|
| `POST /api/webhooks/mercadopago` | Mercado Pago | Confirma pagamento → atualiza order → push → estoque |
| `POST /api/webhooks/stripe` | Stripe | Confirma payment_intent → atualiza order |

**Localização:** `server/_core/index.ts` (registrados antes do tRPC middleware)

---

## Heartbeat (Jobs Periódicos)

| Job | Frequência | Arquivo |
|---|---|---|
| Análise IA | A cada 5 min (durante evento) | `scheduled-ia-analysis.ts` |
| Cobrança de faturas | Diário | `scheduled-invoice-collection.ts` |

**Config:** `server/_core/heartbeat.ts`

---

## Fluxo de um Request

```
Cliente → Express → Cookie parse → tRPC context (user) → Router → Procedure → DB → Response
```

1. Request chega no Express (`server/_core/index.ts`)
2. Middleware de segurança (HSTS, CSP, rate limit)
3. Se webhook → rota Express direta (não passa pelo tRPC)
4. Se `/api/trpc/*` → tRPC handler
5. Context é criado (`context.ts`) → extrai user do cookie
6. Procedure verifica auth level
7. Input validado via Zod
8. Lógica de negócio executa
9. Resposta serializada via Superjson

---

## Testes

| Tipo | Localização | Comando |
|---|---|---|
| Unitários | `server/*.test.ts` | `pnpm test` |
| E2E | `e2e/smoke.spec.ts` | `pnpm playwright test` |

**Total de arquivos de teste:** 35+

**Regra:** Todo router crítico tem pelo menos 1 arquivo de teste.


---


# Frontend Architecture

> **Páginas, componentes, layouts e fluxos de cada persona.**

---

## Stack

- **Framework:** React 19 (SPA)
- **Build:** Vite 6
- **Styling:** Tailwind CSS 4 + shadcn/ui
- **Routing:** Wouter (leve, sem React Router)
- **Data:** tRPC client (React Query under the hood)
- **State:** React Context (Cart, Theme) + hooks
- **PWA:** Service Worker + manifest + push

---

## Layouts

| Layout | Usado por | Descrição |
|---|---|---|
| `DashboardLayout.tsx` | Todas as páginas `/admin/*` e `/mission-control` | Sidebar + header + auth check |
| Sem layout (full page) | `Home.tsx`, `Menu.tsx`, `Onboarding.tsx`, `Login.tsx` | Páginas públicas |

---

## Páginas por Fluxo

### Participante (público, sem login obrigatório)

```
Home.tsx → Onboarding.tsx → (cria evento)
         → Menu.tsx → (faz pedido) → MyOrders.tsx
         → TicketPurchase.tsx → MyTickets.tsx
         → EventEntry.tsx (entrada no evento)
         → Withdrawal.tsx (retirada de itens)
```

**Detalhe do Menu.tsx:**
- É a página mais complexa do frontend
- Contém: cardápio, carrinho, checkout (Pix + Cartão MP + Stripe)
- Usa `CartContext.tsx` para estado do carrinho
- Integra: `StripePaymentForm`, `MercadoPagoCardForm`, `ExpressCheckout`

### Produtor (logado, role=admin)

```
MissionControl.tsx (dashboard ao vivo)
├── AdminEvents.tsx (listar/criar eventos)
├── AdminProducts.tsx (cardápio)
├── AdminIngredients.tsx (insumos)
├── AdminOrders.tsx (pedidos)
├── AdminFinancials.tsx (financeiro)
├── AdminStockMonitor.tsx (estoque ao vivo)
├── AdminIntelligence.tsx (alertas Syntropy)
├── AdminPostEvent.tsx (relatório pós-evento / Vision)
├── AdminCRM.tsx (participantes)
├── AdminPromos.tsx (promoções)
├── AdminTickets.tsx (ingressos)
├── AdminCheckIn.tsx (check-in)
├── AdminContracts.tsx (contratos)
├── AdminSplit.tsx (repasse)
├── AdminRecebimentos.tsx (recebimentos)
└── ... (30+ páginas admin)
```

### Operador (Staff)

```
StaffConsole.tsx (lista de pedidos para preparar)
StaffKDS.tsx (Kitchen Display System — tela do bar)
StationKDS.tsx (KDS por estação, autenticado por token)
StaffWithdrawal.tsx (confirmar retirada de itens)
```

### Landing / Marketing

```
Home.tsx (landing page principal)
Onboarding.tsx (Syntropy conversacional)
DemoShowcase.tsx (demo interativo)
LiveDemo.tsx (Mission Control em modo demo)
PilotLanding.tsx (página do programa piloto)
HowItWorks.tsx (como funciona)
```

---

## Componentes Reutilizáveis

| Componente | Função | Usado em |
|---|---|---|
| `DashboardLayout.tsx` | Layout admin com sidebar | Todas páginas admin |
| `AIChatBox.tsx` | Chat com Syntropy | Onboarding, EventCreator |
| `StripePaymentForm.tsx` | Formulário de cartão Stripe | Menu (checkout) |
| `MercadoPagoCardForm.tsx` | Formulário de cartão MP | Menu (checkout) |
| `ExpressCheckout.tsx` | Apple/Google Pay | Menu (checkout) |
| `AnimatedQR.tsx` | QR Code animado | Withdrawal, Tickets |
| `FluxaQR.tsx` | QR Code estático | QR Codes admin |
| `QrScanner.tsx` | Scanner de QR | StaffWithdrawal, CheckIn |
| `OfflineBanner.tsx` | Banner de modo offline | Global |
| `OfflineIndicator.tsx` | Indicador offline | Staff pages |
| `SyntropyLiveFeed.tsx` | Feed ao vivo da Syntropy | MissionControl |
| `Full7BlocksLayer.tsx` | Relatório 7 blocos | PostEvent |
| `ComingSoonPanel.tsx` | Placeholder de feature | Várias |
| `ErrorBoundary.tsx` | Captura erros React | App.tsx |
| `DateRangePicker.tsx` | Seletor de período | Analytics |
| `ManusDialog.tsx` | Dialog padrão | Várias |
| `FluxaLogo.tsx` | Logo SVG | Header, Login |
| `Redirect.tsx` | Redirect helper | App.tsx |
| `mission-control/` | Componentes do MC | MissionControl.tsx |
| `ui/` | shadcn/ui (button, card...) | Todas |

---

## Hooks Customizados

| Hook | Função |
|---|---|
| `useAuth.ts` | Estado de autenticação (user, login URL) |
| `useOffline.ts` | Detecta se está offline |
| `useOfflineStaff.ts` | Modo offline para staff (queue local) |
| `useOfflineSync.ts` | Sincronização offline → online |
| `useOfflineWithdrawals.ts` | Retiradas offline |
| `usePushNotifications.ts` | Registrar/receber push |
| `useDocumentTitle.ts` | Título dinâmico da página |
| `useMobile.tsx` | Detecta mobile |
| `useLongPress.ts` | Gesto de long press |
| `useComposition.ts` | Composição de componentes |
| `usePersistFn.ts` | Função persistente (ref) |

---

## Contexts

| Context | Função | Usado em |
|---|---|---|
| `CartContext.tsx` | Estado do carrinho (itens, total, add/remove) | Menu.tsx |
| `ThemeContext.tsx` | Tema (dark/light) | Global |

---

## PWA

| Arquivo | Função |
|---|---|
| `client/public/manifest.json` | Configuração PWA (nome, ícones, cores) |
| `client/public/sw.js` | Service Worker (cache, push, offline) |
| `hooks/usePushNotifications.ts` | Registro de push no frontend |

---

## Padrões de Código

1. **Data fetching:** Sempre via `trpc.*.useQuery()` ou `trpc.*.useMutation()`
2. **Loading states:** Skeleton ou spinner por componente (nunca bloqueia página inteira)
3. **Erro:** `ErrorBoundary` global + toast por operação
4. **Navegação:** `useLocation()` do Wouter (não React Router)
5. **Formulários:** Controlled components + Zod validation no backend
6. **Imagens:** Sempre URL externa (S3) — nunca local


---


# Data Model

> **Tabelas do banco, o que guardam e como se relacionam.**
>
> Schema completo: `drizzle/schema.ts` | Relações: `drizzle/relations.ts`

---

## Diagrama de Dependências (simplificado)

```
users ←──────────────────────────────────────────────┐
  │                                                   │
  ├── companies ←── events ←── categories ←── products
  │                    │            │              │
  │                    │            │              ├── productIngredients → ingredients
  │                    │            │              │
  │                    ├── orders ←─┘              ├── stockMovements
  │                    │     │
  │                    │     └── orderItems
  │                    │
  │                    ├── ticketTypes ←── ticketPurchases
  │                    │
  │                    ├── salePoints
  │                    │
  │                    ├── tablesQr
  │                    │
  │                    ├── promos
  │                    │
  │                    ├── contracts
  │                    │
  │                    ├── eventEntries
  │                    │
  │                    ├── splitConfigs → splitTransactions
  │                    │
  │                    ├── aiInsights → iaActions
  │                    │
  │                    └── iaBaselines
  │
  ├── pushSubscriptions
  ├── withdrawalTokens
  ├── participantProfiles
  └── loginSessions
```

---

## Tabelas Principais

### Core

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `users` | Todos os usuários (participantes, produtores, staff) | — |
| `companies` | Empresas produtoras | `userId` (owner) |
| `events` | Eventos criados | `userId`, `companyId` |

### Cardápio

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `categories` | Categorias de produtos (Drinks, Comida...) | `eventId` |
| `products` | Itens do cardápio | `categoryId`, `eventId` |
| `menuTemplates` | Templates de cardápio reutilizáveis | `userId` |
| `menuTemplateCategories` | Categorias do template | `templateId` |
| `menuTemplateItems` | Itens do template | `categoryId` |

### Pedidos e Pagamentos

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `orders` | Pedidos (status, pagamento, total) | `eventId`, `userId` |
| `orderItems` | Itens de cada pedido | `orderId`, `productId` |
| `offlineOrders` | Pedidos feitos offline (sync posterior) | `eventId`, `userId` |
| `refundRequests` | Solicitações de estorno | `orderId`, `eventId` |
| `paymentRefunds` | Estornos processados | `orderId` |

### Ingressos

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `ticketTypes` | Tipos de ingresso (VIP, Pista...) | `eventId` |
| `ticketPurchases` | Ingressos comprados | `ticketTypeId`, `userId` |
| `eventEntries` | Check-ins realizados | `eventId`, `userId` |

### Estoque e Insumos

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `stockMovements` | Movimentações de estoque de produtos | `productId`, `eventId` |
| `ingredients` | Insumos (limão, gelo, vodka...) | `eventId` |
| `productIngredients` | Ficha técnica (produto → insumos) | `productId`, `ingredientId` |
| `ingredientMovements` | Movimentações de insumos | `ingredientId` |
| `ingredientTemplates` | Templates de insumos | `userId` |
| `ingredientTemplateItems` | Itens do template de insumos | `templateId` |

### Financeiro

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `splitConfigs` | Config de split (% produtor vs plataforma) | `eventId` |
| `splitTransactions` | Transações de split executadas | `splitConfigId`, `orderId` |
| `platformRevenue` | Receita da plataforma | `eventId` |
| `eventInvoices` | Faturas de eventos | `eventId` |
| `platformFixedCosts` | Custos fixos da plataforma | — |
| `platformTaxConfig` | Configuração de impostos | — |

### Inteligência (Syntropy)

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `iaBaselines` | Baselines de métricas (para detectar anomalias) | `eventId` |
| `aiInsights` | Insights gerados pela IA | `eventId` |
| `iaActions` | Ações executadas pela IA | `insightId` |
| `iaAnalysisLog` | Log de análises periódicas | `eventId` |
| `platformIntelligence` | Inteligência cross-evento | — |
| `agentLogs` | Logs do agente IA | `eventId` |

### Participantes e CRM

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `participantProfiles` | Perfil de consumo do participante | `userId`, `eventId` |
| `participantFeedback` | Feedback pós-evento | `eventId`, `userId` |
| `leads` | Leads capturados | `eventId` |

### Operacional

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `salePoints` | Pontos de venda (Bar 1, Bar 2...) | `eventId` |
| `tablesQr` | QR codes de mesas | `eventId` |
| `rounds` | Rodadas (grupo de pedidos) | `eventId` |
| `roundParticipants` | Participantes de rodadas | `roundId`, `userId` |
| `withdrawalTokens` | Tokens de retirada (QR) | `orderId`, `userId` |
| `stationTokens` | Tokens de estação KDS | `eventId`, `salePointId` |
| `openBarTracking` | Tracking de open bar | `eventId`, `userId` |

### Promoções e Auto-consumo

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `promos` | Promoções ativas | `eventId` |
| `autoConsumptionRules` | Regras de consumo automático | `eventId` |
| `autoConsumptionSessions` | Sessões de auto-consumo | `ruleId`, `userId` |

### Segurança

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `securityAlerts` | Alertas de segurança | `eventId` |
| `auditLogs` | Log de auditoria | `userId` |
| `mfaSecrets` | Secrets MFA (2FA) | `userId` |
| `loginSessions` | Sessões ativas | `userId` |
| `bankChangeConfirmations` | Confirmações de troca bancária | `userId` |

### Plataforma

| Tabela | O que guarda | Chave estrangeira |
|---|---|---|
| `pushSubscriptions` | Subscriptions de push (participantes) | `userId` |
| `staffPushSubscriptions` | Subscriptions de push (staff) | `userId` |
| `wallets` | Carteiras (legado) | `userId` |
| `topups` | Recargas (legado) | `walletId` |
| `transactions` | Transações (legado) | `walletId` |
| `pilotInvites` | Convites do programa piloto | — |
| `pilotFeedback` | Feedback do piloto | `inviteId` |
| `pilotFollowups` | Follow-ups do piloto | `inviteId` |
| `userFeedback` | Feedback geral | `userId` |
| `contracts` | Contratos digitais | `eventId` |
| `companyMemberRoles` | Roles de membros da empresa | `companyId`, `userId` |

---

## Notas Importantes

1. **Tabelas legado:** `wallets`, `topups`, `transactions` existem no schema mas não são mais usadas (modelo antigo de recarga). Não deletar — podem ter dados históricos.

2. **Migrações:** 55 migrações aplicadas (0000 a 0054). Nunca editar SQL gerado. Sempre usar `pnpm drizzle-kit generate`.

3. **Banco:** MySQL (TiDB) — serverless, auto-scale.

4. **IDs:** Todos `int` auto-increment (não UUID).

5. **Timestamps:** Armazenados como `bigint` (Unix ms UTC). Frontend converte para local.


---


# Critical Flows

> **Fluxos que nenhum dev pode quebrar. Se quebrar, o evento para.**
>
> Antes de alterar qualquer arquivo listado aqui, rode os testes correspondentes.

---

## 1. Pedido → Pagamento → Webhook → Estoque → KDS → Push

**O fluxo mais crítico da Fluxa. Se quebrar, ninguém compra nada.**

```
Participante                    Backend                         Externo
    │                              │                              │
    ├── Seleciona itens ──────────►│                              │
    │   (Menu.tsx + CartContext)    │                              │
    │                              │                              │
    ├── Confirma pedido ──────────►│ orders.create                │
    │                              │   → valida estoque           │
    │                              │   → cria order (pending)     │
    │                              │   → cria orderItems          │
    │                              │   → debita estoque           │
    │                              │   → cria pagamento MP ──────►│ Mercado Pago
    │                              │                              │
    │◄── QR Code Pix ─────────────│◄── pixQrCode ────────────────│
    │                              │                              │
    │   [paga no banco]            │                              │
    │                              │                              │
    │                              │◄── webhook (payment) ────────│ MP notifica
    │                              │   → verifica assinatura      │
    │                              │   → atualiza order → paid    │
    │                              │   → dispatch (Smart Routing) │
    │                              │   → push para staff          │
    │                              │   → push para participante   │
    │                              │                              │
    │◄── Push "pedido confirmado" ─│                              │
    │                              │                              │
    Staff                          │                              │
    │◄── Push "novo pedido" ───────│                              │
    │   (StaffKDS.tsx)             │                              │
    │                              │                              │
    ├── Marca "pronto" ───────────►│ orders.updateStatus          │
    │                              │   → push para participante   │
    │                              │                              │
    │◄── Push "pronto p/ retirar" ─│                              │
```

**Arquivos envolvidos:**
- `server/routers/orders.ts` (create, updateStatus)
- `server/mercadopago.ts` (createPixPayment)
- `server/_core/index.ts` (webhook handler)
- `server/dispatch.ts` (Smart Routing)
- `server/pushNotification.ts` (push)
- `client/src/pages/Menu.tsx` (UI)
- `client/src/contexts/CartContext.tsx` (carrinho)

**Testes:** `server/payment-flow.test.ts`, `server/mercadopago.test.ts`

---

## 2. Ingresso → Pagamento → QR → Check-in

```
Participante                    Backend                         Externo
    │                              │                              │
    ├── Seleciona ingresso ───────►│ tickets.purchase             │
    │   (TicketPurchase.tsx)        │   → cria ticketPurchase     │
    │                              │   → cria pagamento MP ──────►│ MP
    │                              │                              │
    │   [paga]                     │                              │
    │                              │◄── webhook ──────────────────│
    │                              │   → confirma purchase        │
    │                              │   → gera QR token            │
    │                              │                              │
    │◄── QR do ingresso ───────────│                              │
    │   (MyTickets.tsx)            │                              │
    │                              │                              │
    Staff (check-in)               │                              │
    │── Escaneia QR ──────────────►│ tickets.validateEntry        │
    │   (AdminCheckIn.tsx)         │   → valida token             │
    │                              │   → cria eventEntry          │
    │                              │   → marca used               │
    │◄── ✅ Entrada válida ────────│                              │
```

**Arquivos:** `server/routers/tickets.ts`, `client/src/pages/TicketPurchase.tsx`, `AdminCheckIn.tsx`

**Testes:** `server/tickets.test.ts`

---

## 3. Syntropy → Snapshot → Baseline → Anomalia → Sugestão → Ação

```
Heartbeat (5 min)              intelligence-engine.ts
    │                              │
    ├── trigger ──────────────────►│ analyzeEvent()
    │                              │   → coleta métricas atuais
    │                              │   → compara com baseline
    │                              │   → detecta anomalias
    │                              │   │
    │                              │   ├── Se anomalia:
    │                              │   │   → gera insight (aiInsights)
    │                              │   │   → sugere ação
    │                              │   │   → push para produtor
    │                              │   │
    │                              │   ├── Se confiança > 90%:
    │                              │   │   → executa ação (dispatch)
    │                              │   │   → registra iaAction
    │                              │   │
    │                              │   └── Se confiança < 90%:
    │                              │       → apenas sugere
    │                              │       → aguarda aprovação
    │                              │
    Produtor                       │
    │◄── Push "alerta" ────────────│
    │   (AdminIntelligence.tsx)    │
    │── Aprova/Rejeita ───────────►│ aiInsights.executeAction
    │                              │   → dispatch.ts executa
```

**Arquivos:** `server/intelligence-engine.ts`, `server/scheduled-ia-analysis.ts`, `server/dispatch.ts`, `server/routers/aiInsights.ts`

**Testes:** `server/intelligence-engine.test.ts`, `server/intelligence.test.ts`

---

## 4. Pedidos Offline → Sync → Pagamento Posterior

```
Staff (sem internet)            Local (IndexedDB)              Backend (quando volta)
    │                              │                              │
    ├── Cria pedido offline ──────►│ salva localmente             │
    │   (useOfflineStaff.ts)       │   → status: offline_pending │
    │                              │                              │
    │   [internet volta]           │                              │
    │                              │                              │
    ├── Sync automático ──────────►│──────────────────────────────►│ offlineOrders.sync
    │   (useOfflineSync.ts)        │                              │   → cria orders reais
    │                              │                              │   → gera pagamento
    │                              │                              │   → push para cliente
    │                              │                              │
    │◄── Confirmação ──────────────│◄─────────────────────────────│
```

**Arquivos:** `server/routers/offlineOrders.ts`, `client/src/hooks/useOfflineStaff.ts`, `useOfflineSync.ts`

**Testes:** `server/offline-mode.test.ts`

---

## 5. Split → Produtor Recebe Direto

```
Pagamento confirmado           Backend                         Stripe Connect
    │                              │                              │
    ├── webhook confirma ─────────►│ processPayment               │
    │                              │   → calcula split            │
    │                              │   │  (% produtor vs Fluxa)   │
    │                              │   │                          │
    │                              │   ├── Se Stripe Connect:     │
    │                              │   │   → transfer direto ────►│ conta do produtor
    │                              │   │   → registra splitTx     │
    │                              │   │                          │
    │                              │   └── Se MP:                 │
    │                              │       → acumula              │
    │                              │       → repasse manual       │
    │                              │                              │
```

**Arquivos:** `server/routers/stripeConnect.ts`, `server/routers/orders.ts`

**Testes:** `server/stripe-connect.test.ts`

---

## 6. Retirada de Itens (QR)

```
Participante                    Backend                         Staff
    │                              │                              │
    │── Pedido pago ──────────────►│ gera withdrawalToken         │
    │                              │   → QR com token único       │
    │                              │                              │
    │── Mostra QR no bar ─────────►│──────────────────────────────►│
    │                              │                              │ escaneia
    │                              │                              │
    │                              │◄── validate token ───────────│
    │                              │   → verifica: não usado      │
    │                              │   → verifica: itens corretos │
    │                              │   → marca items retirados    │
    │                              │   → debita do token          │
    │                              │                              │
    │◄── ✅ "Retire seus itens" ───│                              │
```

**Arquivos:** `server/routers/withdrawal.ts`, `client/src/pages/Withdrawal.tsx`, `StaffWithdrawal.tsx`

**Testes:** `server/withdrawal.test.ts`, `server/offline-withdrawal.test.ts`

---

## Regra de Ouro

> **Se você vai alterar qualquer arquivo listado acima:**
>
> 1. Rode `pnpm test` ANTES de começar
> 2. Faça a alteração
> 3. Rode `pnpm test` DEPOIS
> 4. Se quebrou algum teste → reverta
> 5. Se não tem teste para o que você alterou → escreva um antes


---


# Fluxa — Guia do Desenvolvedor

> **Leia isto primeiro.** Este é o ponto de entrada para qualquer dev (humano ou IA) que vai trabalhar no projeto.

---

## O que é a Fluxa

A Fluxa é o **sistema operacional para eventos**. Ela controla pedidos, pagamentos, estoque, equipe e inteligência — tudo em tempo real, durante o evento.

A **Syntropy** é o cérebro da plataforma: uma inteligência que observa, decide e age autonomamente para maximizar o resultado do evento.

**Domínio:** https://fluxa.bar

---

## Ordem de Leitura

| # | Documento | Tempo | O que aprende |
|---|---|---|---|
| 1 | `docs/FLUXA_CANON.md` | 5 min | O que é a Fluxa, missão, visão |
| 2 | `AGENTS.md` | 5 min | Regras invioláveis do projeto |
| 3 | `docs/02_SISTEMA/REPO_MAP.md` | 5 min | Onde está cada coisa no código |
| 4 | `docs/02_SISTEMA/FEATURE_TO_FILE_MAP.md` | 3 min | Feature → arquivo |
| 5 | `docs/02_SISTEMA/CRITICAL_FLOWS.md` | 10 min | O que não pode quebrar |
| 6 | `docs/02_SISTEMA/BACKEND_ARCHITECTURE.md` | 10 min | Routers, procedures, webhooks |
| 7 | `docs/02_SISTEMA/FRONTEND_ARCHITECTURE.md` | 10 min | Páginas, componentes, hooks |
| 8 | `docs/02_SISTEMA/DATA_MODEL.md` | 10 min | Tabelas e relações |
| 9 | `docs/10_SETUP_DEV/DEV_ONBOARDING.md` | 5 min | Como rodar e testar |
| 10 | `docs/10_SETUP_DEV/CHANGE_RULES.md` | 5 min | Regras para alterar código |

**Total: ~70 minutos para entender o projeto inteiro.**

---

## Quick Start

```bash
pnpm install
pnpm dev
# → http://localhost:3000
```

---

## Documentação Completa

```
docs/
├── FLUXA_CANON.md               ← Verdade oficial
├── SYSTEM_MAP.md                ← Mapa visual da plataforma
├── VANTAGEM_COMPETITIVA.md      ← Por que a Fluxa ganha
├── NETWORK_EFFECT.md            ← Efeito de rede
├── FASE1_VISAO_VS_CODIGO.md     ← Gap analysis (visão vs implementação)
│
├── 000_VISAO/                   ← Visão do produto
│   ├── A_EMPRESA.md
│   ├── B_PRODUTO.md
│   ├── C_FILOSOFIA.md
│   ├── D_PRINCIPIOS.md
│   ├── E_O_QUE_NAO_E.md
│   └── F_JORNADA_PRODUTOR.md
│
├── 02_SISTEMA/                  ← Arquitetura técnica
│   ├── REPO_MAP.md
│   ├── FEATURE_TO_FILE_MAP.md
│   ├── BACKEND_ARCHITECTURE.md
│   ├── FRONTEND_ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   └── CRITICAL_FLOWS.md
│
├── 04_SYNTROPY/                 ← Inteligência artificial
│   ├── README.md
│   ├── DECISION_ENGINE.md
│   ├── KNOWLEDGE_GRAPH.md
│   ├── INFERENCE_ENGINE.md
│   ├── LEARNING_ENGINE.md
│   ├── MEMORY_ENGINE.md
│   ├── CONTEXT_ENGINE.md
│   ├── CONFIDENCE_ENGINE.md
│   ├── GOAL_ENGINE.md
│   ├── ETHICS_ENGINE.md
│   ├── SIMULATION_ENGINE.md
│   ├── EVOLUTION.md
│   ├── VISION.md
│   ├── SMART_ROUTING.md
│   ├── FORECAST.md
│   └── PROMOCOES.md
│
└── 10_SETUP_DEV/                ← Setup e regras
    ├── DEV_ONBOARDING.md
    └── CHANGE_RULES.md
```

---

## Regras Rápidas

1. **Rode `pnpm test` antes e depois de qualquer alteração**
2. **Nunca mexer em pagamentos sem teste**
3. **Nunca mexer em estoque sem teste**
4. **Nunca mexer na Syntropy sem atualizar docs**
5. **Imagens → S3 (nunca no repo)**
6. **Secrets → Manus (nunca no código)**

---

## Contato

- **Produto:** Nanda (Maria Fernanda Carmesini Braga)
- **Plataforma:** Manus AI
- **Domínio:** fluxa.bar


---


# Dev Onboarding

> **Como rodar, testar e deployar a Fluxa.**
>
> Tempo estimado de setup: 5 minutos (se tiver acesso ao Manus).

---

## Pré-requisitos

- Node.js 22+
- pnpm (gerenciador de pacotes)
- Acesso ao projeto Manus (para variáveis de ambiente)

---

## Setup Local

```bash
# 1. Clone
git clone <repo-url> base-x
cd base-x

# 2. Instale dependências
pnpm install

# 3. Variáveis de ambiente
# As variáveis são injetadas automaticamente pelo Manus.
# Em desenvolvimento local, crie um .env com:
#   DATABASE_URL=...
#   JWT_SECRET=...
#   MP_ACCESS_TOKEN=...
#   (ver lista completa abaixo)

# 4. Rode
pnpm dev
# → Frontend: http://localhost:5173
# → Backend: http://localhost:3000
```

---

## Variáveis de Ambiente

### Obrigatórias (sistema)

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | Connection string MySQL/TiDB |
| `JWT_SECRET` | Secret para cookies de sessão |
| `VITE_APP_ID` | ID do app Manus OAuth |
| `OAUTH_SERVER_URL` | URL do servidor OAuth |
| `VITE_OAUTH_PORTAL_URL` | URL do portal de login |
| `OWNER_OPEN_ID` | OpenID do owner |
| `BUILT_IN_FORGE_API_URL` | URL da API interna Manus |
| `BUILT_IN_FORGE_API_KEY` | Key da API interna |

### Mercado Pago (PRODUÇÃO — cuidado!)

| Variável | Descrição |
|---|---|
| `MP_ACCESS_TOKEN` | Token de acesso MP (**produção real**) |
| `MP_WEBHOOK_SECRET` | Secret do webhook MP |
| `VITE_MP_PUBLIC_KEY` | Chave pública MP (frontend) |

### Stripe (sandbox)

| Variável | Descrição |
|---|---|
| `STRIPE_SECRET_KEY` | Secret key Stripe (test) |
| `STRIPE_WEBHOOK_SECRET` | Secret do webhook Stripe |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Publishable key (frontend) |

### Push Notifications

| Variável | Descrição |
|---|---|
| `VAPID_PUBLIC_KEY` | Chave pública VAPID |
| `VAPID_PRIVATE_KEY` | Chave privada VAPID |
| `VITE_VAPID_PUBLIC_KEY` | Chave pública (frontend) |

### Outros

| Variável | Descrição |
|---|---|
| `SAKANA_API_KEY` | API de IA (Sakana) |
| `VITE_APP_TITLE` | Título do app |
| `VITE_APP_LOGO` | URL do logo |

---

## Serviços Externos

| Serviço | Ambiente | Cuidado |
|---|---|---|
| **Mercado Pago** | PRODUÇÃO | Pagamentos reais. Testar com R$ 1,00 |
| **Stripe** | Sandbox | Cartão de teste: `4242 4242 4242 4242` |
| **TiDB** | Produção | Banco real. Cuidado com migrations |
| **Manus OAuth** | Produção | Login real |
| **Push (VAPID)** | Produção | Notificações reais |

---

## Como Testar

### Testes unitários
```bash
pnpm test          # Roda todos os testes
pnpm test -- --run # Roda sem watch mode
```

### Testes E2E
```bash
pnpm playwright test
```

### Teste manual de pagamento

**Pix (dinheiro real):**
1. Acesse um evento → cardápio
2. Faça pedido → escolha Pix
3. Pague R$ 1,00 com seu banco
4. Observe webhook confirmar

**Cartão (Stripe sandbox):**
1. Mesmo fluxo → escolha cartão
2. Use `4242 4242 4242 4242`, validade futura, CVC 123
3. Não cobra nada real

---

## Como Deployar

O deploy é automático via Manus:

1. Faça as alterações
2. Rode `pnpm test` — tudo verde
3. Salve checkpoint (`webdev_save_checkpoint`)
4. Clique "Publish" na UI do Manus

**Domínio:** https://fluxa.bar

---

## Banco de Dados

### Ver schema atual
```bash
# O schema está em drizzle/schema.ts
```

### Criar migração
```bash
pnpm drizzle-kit generate
# → Gera SQL em drizzle/XXXX_*.sql
# → Aplique via webdev_execute_sql
```

### Regras
- **Nunca** editar SQL gerado manualmente
- **Nunca** rodar DROP TABLE sem backup
- **Sempre** testar migração em dev antes de prod
- Schema e banco devem estar sempre em sync

---

## Estrutura de Branches

- `main` — produção (auto-deploy)
- Não há branches de feature — desenvolvimento direto no main via Manus

---

## Cuidados Especiais

| Área | Cuidado |
|---|---|
| Mercado Pago | É PRODUÇÃO. Qualquer pagamento é real. |
| Webhooks | Se alterar URL ou handler, pagamentos param de confirmar |
| Estoque | Débito acontece no momento do pedido, não do pagamento |
| Push | Precisa de HTTPS para funcionar |
| Offline | Testar com DevTools → Network → Offline |
| Smart Routing | Se quebrar, pedidos não chegam no bar certo |

---

## Ordem de Leitura Recomendada

Para um dev novo entender o projeto:

1. `docs/FLUXA_CANON.md` — O que é a Fluxa (5 min)
2. `docs/02_SISTEMA/REPO_MAP.md` — Onde está cada coisa (5 min)
3. `docs/02_SISTEMA/FEATURE_TO_FILE_MAP.md` — Feature → arquivo (3 min)
4. `docs/02_SISTEMA/CRITICAL_FLOWS.md` — O que não pode quebrar (10 min)
5. `docs/02_SISTEMA/BACKEND_ARCHITECTURE.md` — Como o backend funciona (10 min)
6. `AGENTS.md` — Regras para trabalhar no projeto (5 min)


---


# Change Rules

> **Regras para qualquer alteração no código da Fluxa.**
>
> Quebre essas regras e o evento pode parar.

---

## Regras Invioláveis

### 1. Nunca mexer em pagamentos sem teste

**Arquivos protegidos:**
- `server/routers/orders.ts`
- `server/routers/stripe.ts`
- `server/mercadopago.ts`
- `server/_core/index.ts` (webhooks)

**Antes de alterar:**
```bash
pnpm test -- payment-flow
pnpm test -- mercadopago
pnpm test -- stripe
```

**Se quebrar qualquer teste → reverta imediatamente.**

---

### 2. Nunca mexer em estoque sem teste

**Arquivos protegidos:**
- Lógica de débito em `server/routers/orders.ts`
- `server/routers/ingredients.ts`
- `server/routers/products.ts` (stock-related)

**Risco:** Débito duplo, estoque negativo, produto vendido sem ter.

---

### 3. Nunca mexer na Syntropy sem atualizar documentação

**Arquivos:**
- `server/intelligence-engine.ts`
- `server/dispatch.ts`
- `server/scheduled-ia-analysis.ts`

**Se alterar lógica de decisão:**
- Atualizar `docs/04_SYNTROPY/DECISION_ENGINE.md`
- Atualizar `docs/02_SISTEMA/CRITICAL_FLOWS.md` (fluxo 3)

---

### 4. Toda feature nova precisa atualizar o mapa

Ao criar nova funcionalidade:
1. Adicionar em `docs/02_SISTEMA/FEATURE_TO_FILE_MAP.md`
2. Se criar novo router → adicionar em `BACKEND_ARCHITECTURE.md`
3. Se criar nova página → adicionar em `FRONTEND_ARCHITECTURE.md`
4. Se criar nova tabela → adicionar em `DATA_MODEL.md`

---

### 5. Toda mudança crítica precisa ter rollback

**Definição de "mudança crítica":**
- Altera schema do banco
- Altera fluxo de pagamento
- Altera webhook
- Altera autenticação
- Altera Smart Routing

**Procedimento:**
1. Salvar checkpoint ANTES
2. Fazer a alteração
3. Testar
4. Se falhar → rollback para o checkpoint

---

### 6. Nunca alterar `server/_core/` sem necessidade extrema

Esses arquivos são framework. Se alterar:
- OAuth pode quebrar
- Autenticação pode quebrar
- Webhooks podem parar
- Deploy pode falhar

**Exceção:** `index.ts` para adicionar middleware de segurança.

---

### 7. Nunca commitar secrets ou .env

- Variáveis de ambiente são gerenciadas pelo Manus
- Nunca hardcodar tokens, keys ou secrets no código
- Se precisar de nova variável → usar `webdev_request_secrets`

---

### 8. Imagens nunca no repositório

- Usar `manus-upload-file --webdev` para upload
- Usar URL retornada no código
- Armazenar original em `/home/ubuntu/webdev-static-assets/`

---

## Checklist Pré-Deploy

```
[ ] pnpm test -- --run (todos passando)
[ ] Nenhum console.log de debug
[ ] Nenhum TODO crítico aberto
[ ] Feature documentada no mapa
[ ] Se mexeu em pagamento → testou manualmente
[ ] Se mexeu em schema → migração aplicada
[ ] Checkpoint salvo
```

---

## Severidade de Áreas

| Área | Severidade | Se quebrar... |
|---|---|---|
| Pagamentos (orders, webhooks) | 🔴 CRÍTICA | Ninguém compra |
| Smart Routing (dispatch) | 🔴 CRÍTICA | Pedidos não chegam no bar |
| Estoque | 🟠 ALTA | Vende sem ter |
| KDS (stationTokens) | 🟠 ALTA | Bar não vê pedidos |
| Push notifications | 🟡 MÉDIA | Cliente não sabe que pedido ficou pronto |
| Syntropy (intelligence) | 🟡 MÉDIA | Produtor perde insights |
| Admin pages | 🟢 BAIXA | Produtor não vê dados (mas evento continua) |
| Landing page | 🟢 BAIXA | Marketing afetado, operação ok |

---

## Comunicação

Ao fazer alteração significativa:
1. Descrever o que mudou no commit/checkpoint
2. Se afeta outro dev → avisar
3. Se afeta produção → testar em staging primeiro (ou com valor mínimo)
