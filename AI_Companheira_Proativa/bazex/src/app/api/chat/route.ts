
import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { generateAIResponse } from '@/lib/openai'

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Não autorizado' }, { status: 401 })
    }

    const { message } = await request.json()

    if (!message) {
      return NextResponse.json({ error: 'Mensagem é obrigatória' }, { status: 400 })
    }

    // Salvar mensagem do usuário
    await prisma.chatMessage.create({
      data: {
        userId: session.user.id,
        message,
        isUser: true
      }
    })

    // Buscar contexto do usuário
    const userProfile = await prisma.userProfile.findUnique({
      where: { userId: session.user.id }
    })

    const recentAgenda = await prisma.agendaItem.findMany({
      where: { 
        userId: session.user.id,
        startTime: {
          gte: new Date(),
          lte: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // próximos 7 dias
        }
      },
      take: 5
    })

    const context = {
      profile: userProfile,
      upcomingEvents: recentAgenda
    }

    // Gerar resposta da IA
    const aiResponse = await generateAIResponse(message, context)

    // Salvar resposta da IA
    await prisma.chatMessage.create({
      data: {
        userId: session.user.id,
        message: aiResponse,
        isUser: false,
        context: JSON.stringify(context)
      }
    })

    return NextResponse.json({ response: aiResponse })
  } catch (error) {
    console.error('Erro no chat:', error)
    return NextResponse.json({ error: 'Erro interno do servidor' }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Não autorizado' }, { status: 401 })
    }

    const messages = await prisma.chatMessage.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'asc' },
      take: 50
    })

    return NextResponse.json({ messages })
  } catch (error) {
    console.error('Erro ao buscar mensagens:', error)
    return NextResponse.json({ error: 'Erro interno do servidor' }, { status: 500 })
  }
}
