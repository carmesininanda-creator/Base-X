
# BazeX - AI Companheira Proativa

Uma aplicação web completa que demonstra as capacidades de uma IA companheira proativa, desenvolvida com NextJS, TypeScript, PostgreSQL e integração GPT.

## 🚀 Funcionalidades Principais

### 🤖 Interface Conversacional
- Chat inteligente com IA integrada
- Respostas contextuais baseadas no perfil do usuário
- Histórico de conversas persistente

### 📅 Agenda Inteligente
- Visualização em dia e semana
- Sugestões proativas de otimização
- Categorização automática de eventos
- Lembretes inteligentes

### 🎯 Coaching Pessoal
- Definição e acompanhamento de metas
- Progresso visual com gráficos
- Insights personalizados da IA
- Categorias: saúde, financeiro, pessoal, carreira

### 🏠 Controle IoT
- Painel de controle de dispositivos inteligentes
- Automações baseadas em padrões de uso
- Status em tempo real
- Sugestões de economia de energia

### 💰 Assistente Financeiro
- Categorização automática de gastos
- Análise de padrões de consumo
- Sugestões de economia
- Relatórios visuais por categoria

### 🏥 Saúde & Bem-estar
- Acompanhamento de métricas de saúde
- Score de saúde diário
- Lembretes de hidratação e exercícios
- Insights baseados em dados

### ⚙️ Configurações Avançadas
- Tema escuro/claro
- Preferências de notificação
- Configurações de privacidade
- Personalização completa

## 🛠️ Tecnologias Utilizadas

- **Frontend**: NextJS 15, TypeScript, TailwindCSS
- **Backend**: NextJS API Routes, Node.js
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **ORM**: Prisma
- **Autenticação**: NextAuth.js
- **IA**: OpenAI GPT-4 (simulado para desenvolvimento)
- **UI Components**: Lucide React, Headless UI

## 📦 Instalação e Configuração

### Pré-requisitos
- Node.js 18+ 
- npm ou yarn

### Passos de Instalação

1. **Clone o repositório**
```bash
git clone <repository-url>
cd bazex
```

2. **Instale as dependências**
```bash
npm install
```

3. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```env
DATABASE_URL="file:./dev.db"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-here"
OPENAI_API_KEY="your-openai-api-key-here"
```

4. **Configure o banco de dados**
```bash
npx prisma generate
npx prisma migrate dev --name init
```

5. **Popule o banco com dados de demonstração**
```bash
npm run db:seed
```

6. **Execute o servidor de desenvolvimento**
```bash
npm run dev
```

7. **Acesse a aplicação**
Abra [http://localhost:3000](http://localhost:3000) no seu navegador.

## 👤 Login de Demonstração

Use as credenciais abaixo para testar a aplicação:

- **Email**: demo@bazex.com
- **Senha**: 123456

## 🏗️ Estrutura do Projeto

```
bazex/
├── src/
│   ├── app/                    # App Router (NextJS 13+)
│   │   ├── api/               # API Routes
│   │   ├── auth/              # Páginas de autenticação
│   │   ├── dashboard/         # Dashboard principal
│   │   ├── chat/              # Interface de chat
│   │   ├── agenda/            # Módulo de agenda
│   │   ├── coaching/          # Módulo de coaching
│   │   ├── iot/               # Controle IoT
│   │   ├── finance/           # Assistente financeiro
│   │   ├── health/            # Saúde e bem-estar
│   │   └── settings/          # Configurações
│   ├── components/            # Componentes React
│   │   ├── Layout/            # Componentes de layout
│   │   └── ...
│   └── lib/                   # Utilitários e configurações
├── prisma/                    # Schema e migrações do banco
├── public/                    # Arquivos estáticos
└── ...
```

## 🔧 Scripts Disponíveis

- `npm run dev` - Inicia o servidor de desenvolvimento
- `npm run build` - Gera build de produção
- `npm run start` - Inicia servidor de produção
- `npm run lint` - Executa linting
- `npm run db:seed` - Popula banco com dados de teste
- `npm run db:reset` - Reseta banco e executa seed

## 🌟 Funcionalidades Demonstradas

### IA Proativa
- Sugestões contextuais baseadas no comportamento do usuário
- Análise de padrões para otimização de rotina
- Recomendações personalizadas em tempo real

### Automação Inteligente
- Detecção automática de padrões de uso
- Sugestões de automação para dispositivos IoT
- Otimização de agenda baseada em histórico

### Insights Personalizados
- Análise de dados de saúde e bem-estar
- Relatórios financeiros com sugestões de economia
- Acompanhamento de progresso de metas

## 🔒 Segurança

- Autenticação segura com NextAuth.js
- Senhas criptografadas com bcrypt
- Validação de dados no frontend e backend
- Proteção contra ataques comuns (CSRF, XSS)

## 📱 Responsividade

A aplicação é totalmente responsiva e funciona perfeitamente em:
- Desktop (1920px+)
- Tablet (768px - 1024px)
- Mobile (320px - 767px)

## 🚀 Deploy

Para deploy em produção:

1. Configure as variáveis de ambiente de produção
2. Use PostgreSQL ao invés de SQLite
3. Execute `npm run build`
4. Deploy em plataformas como Vercel, Netlify ou AWS

## 🤝 Contribuição

Este é um projeto de demonstração das capacidades da BazeX. Para contribuições:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é uma demonstração e está disponível sob licença MIT.

## 📞 Suporte

Para dúvidas ou suporte, entre em contato através dos canais oficiais da BazeX.

---

**BazeX - Sua IA Companheira Proativa** 🤖✨
