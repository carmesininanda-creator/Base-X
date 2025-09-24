
import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Iniciando seed do banco de dados...')

  // Criar usuário de demonstração
  const hashedPassword = await bcrypt.hash('123456', 12)
  
  const user = await prisma.user.upsert({
    where: { email: 'demo@bazex.com' },
    update: {},
    create: {
      name: 'Usuário Demo',
      email: 'demo@bazex.com',
      password: hashedPassword,
    },
  })

  console.log('👤 Usuário criado:', user.email)

  // Criar perfil do usuário
  await prisma.userProfile.upsert({
    where: { userId: user.id },
    update: {},
    create: {
      userId: user.id,
      preferences: JSON.stringify({
        theme: 'dark',
        notifications: true,
        proactiveMode: true,
        language: 'pt-BR'
      }),
      timezone: 'America/Sao_Paulo',
      language: 'pt-BR',
      workHours: JSON.stringify({ start: '09:00', end: '18:00' }),
      sleepHours: JSON.stringify({ bedtime: '23:00', wakeup: '07:00' }),
      location: 'São Paulo, SP',
      interests: JSON.stringify(['tecnologia', 'saúde', 'produtividade', 'finanças'])
    },
  })

  console.log('📋 Perfil do usuário criado')

  // Criar eventos da agenda
  const agendaItems = [
    {
      title: 'Reunião de equipe',
      description: 'Discussão sobre o projeto Q4',
      startTime: new Date(Date.now() + 2 * 60 * 60 * 1000),
      endTime: new Date(Date.now() + 3 * 60 * 60 * 1000),
      location: 'Sala de conferências',
      category: 'work',
      priority: 'high',
      status: 'scheduled'
    },
    {
      title: 'Consulta médica',
      description: 'Check-up anual',
      startTime: new Date(Date.now() + 24 * 60 * 60 * 1000),
      endTime: new Date(Date.now() + 25 * 60 * 60 * 1000),
      location: 'Hospital São Lucas',
      category: 'health',
      priority: 'medium',
      status: 'scheduled'
    },
    {
      title: 'Academia',
      description: 'Treino de força',
      startTime: new Date(Date.now() + 48 * 60 * 60 * 1000),
      endTime: new Date(Date.now() + 49.5 * 60 * 60 * 1000),
      location: 'Smart Fit',
      category: 'health',
      priority: 'medium',
      status: 'scheduled'
    }
  ]

  for (const item of agendaItems) {
    await prisma.agendaItem.create({
      data: {
        ...item,
        userId: user.id
      }
    })
  }

  console.log('📅 Eventos da agenda criados')

  // Criar metas
  const goals = [
    {
      title: 'Perder 5kg',
      description: 'Meta de emagrecimento saudável',
      category: 'health',
      targetValue: 5,
      currentValue: 2.3,
      unit: 'kg',
      deadline: new Date('2024-12-31'),
      status: 'active'
    },
    {
      title: 'Economizar R$ 10.000',
      description: 'Reserva de emergência',
      category: 'financial',
      targetValue: 10000,
      currentValue: 6500,
      unit: 'reais',
      deadline: new Date('2024-12-31'),
      status: 'active'
    },
    {
      title: 'Ler 24 livros',
      description: '2 livros por mês durante o ano',
      category: 'personal',
      targetValue: 24,
      currentValue: 18,
      unit: 'livros',
      deadline: new Date('2024-12-31'),
      status: 'active'
    }
  ]

  for (const goal of goals) {
    await prisma.goal.create({
      data: {
        ...goal,
        userId: user.id
      }
    })
  }

  console.log('🎯 Metas criadas')

  // Criar despesas
  const expenses = [
    {
      amount: 1200.00,
      description: 'Aluguel',
      category: 'moradia',
      date: new Date('2024-08-01'),
      isRecurring: true
    },
    {
      amount: 350.50,
      description: 'Supermercado',
      category: 'alimentacao',
      date: new Date('2024-08-15'),
      isRecurring: false
    },
    {
      amount: 89.90,
      description: 'Internet',
      category: 'utilidades',
      date: new Date('2024-08-05'),
      isRecurring: true
    },
    {
      amount: 120.00,
      description: 'Academia',
      category: 'saude',
      date: new Date('2024-08-01'),
      isRecurring: true
    }
  ]

  for (const expense of expenses) {
    await prisma.expense.create({
      data: {
        ...expense,
        userId: user.id
      }
    })
  }

  console.log('💰 Despesas criadas')

  // Criar dados de saúde
  const healthData = [
    {
      type: 'weight',
      value: 75.2,
      unit: 'kg',
      date: new Date(),
      notes: 'Após exercício matinal'
    },
    {
      type: 'steps',
      value: 8500,
      unit: 'passos',
      date: new Date()
    },
    {
      type: 'water',
      value: 2.1,
      unit: 'litros',
      date: new Date()
    },
    {
      type: 'sleep',
      value: 7.5,
      unit: 'horas',
      date: new Date(Date.now() - 24 * 60 * 60 * 1000),
      notes: 'Sono reparador'
    }
  ]

  for (const data of healthData) {
    await prisma.healthData.create({
      data: {
        ...data,
        userId: user.id
      }
    })
  }

  console.log('🏥 Dados de saúde criados')

  // Criar dispositivos IoT
  const iotDevices = [
    {
      name: 'Lâmpada Principal',
      type: 'light',
      room: 'sala',
      status: 'online',
      properties: JSON.stringify({ brightness: 80, color: '#ffffff', isOn: true })
    },
    {
      name: 'Ar Condicionado',
      type: 'thermostat',
      room: 'quarto',
      status: 'online',
      properties: JSON.stringify({ temperature: 22, targetTemp: 24, mode: 'cool', isOn: true })
    },
    {
      name: 'Câmera de Segurança',
      type: 'security',
      room: 'entrada',
      status: 'online',
      properties: JSON.stringify({ recording: true, motionDetection: true, nightVision: false })
    },
    {
      name: 'Smart TV',
      type: 'appliance',
      room: 'sala',
      status: 'offline',
      properties: JSON.stringify({ volume: 25, channel: 'Netflix', isOn: false })
    }
  ]

  for (const device of iotDevices) {
    await prisma.ioTDevice.create({
      data: {
        ...device,
        userId: user.id
      }
    })
  }

  console.log('🏠 Dispositivos IoT criados')

  // Criar notificações
  const notifications = [
    {
      title: 'Reunião em 30 minutos',
      message: 'Sua reunião de equipe começará em 30 minutos. Prepare-se!',
      type: 'reminder',
      category: 'agenda',
      isRead: false
    },
    {
      title: 'Meta de passos atingida!',
      message: 'Parabéns! Você atingiu sua meta de 8.000 passos hoje.',
      type: 'info',
      category: 'health',
      isRead: false
    },
    {
      title: 'Lembrete de hidratação',
      message: 'Que tal beber um copo de água agora?',
      type: 'suggestion',
      category: 'health',
      isRead: true
    }
  ]

  for (const notification of notifications) {
    await prisma.notification.create({
      data: {
        ...notification,
        userId: user.id
      }
    })
  }

  console.log('🔔 Notificações criadas')

  // Criar recomendações
  const recommendations = [
    {
      userId: user.id,
      title: 'Otimize sua manhã',
      content: 'Baseado no seu histórico, você é mais produtivo pela manhã. Que tal agendar suas tarefas mais importantes antes das 10h?',
      category: 'productivity',
      priority: 4,
      isActive: true
    },
    {
      userId: user.id,
      title: 'Controle de gastos',
      content: 'Seus gastos este mês estão 15% acima da média. Vamos revisar juntos?',
      category: 'finance',
      priority: 5,
      isActive: true
    }
  ]

  for (const rec of recommendations) {
    await prisma.recommendation.create({
      data: rec
    })
  }

  console.log('💡 Recomendações criadas')

  // Criar mensagens de chat iniciais
  const chatMessages = [
    {
      message: 'Olá! Bem-vindo à BazeX! Como posso ajudá-lo hoje?',
      isUser: false,
      context: JSON.stringify({ type: 'welcome' })
    },
    {
      message: 'Oi BazeX! Estou animado para começar a usar seus recursos.',
      isUser: true
    },
    {
      message: 'Que ótimo! Vou te ajudar a organizar sua vida de forma mais inteligente. Posso começar analisando sua agenda e sugerindo otimizações. Você tem alguma preferência específica?',
      isUser: false,
      context: JSON.stringify({ type: 'onboarding' })
    }
  ]

  for (const msg of chatMessages) {
    await prisma.chatMessage.create({
      data: {
        ...msg,
        userId: user.id
      }
    })
  }

  console.log('💬 Mensagens de chat criadas')

  console.log('✅ Seed concluído com sucesso!')
  console.log('📧 Email de login: demo@bazex.com')
  console.log('🔑 Senha: 123456')
}

main()
  .then(async () => {
    await prisma.$disconnect()
  })
  .catch(async (e) => {
    console.error(e)
    await prisma.$disconnect()
    process.exit(1)
  })
