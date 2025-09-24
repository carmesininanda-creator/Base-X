
'use client'

import { useEffect, useState } from 'react'
import { useSession } from 'next-auth/react'
import DashboardLayout from '@/components/Layout/DashboardLayout'
import {
  Calendar,
  MessageCircle,
  Target,
  DollarSign,
  Heart,
  Home,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

interface DashboardStats {
  todayEvents: number
  pendingGoals: number
  monthlyExpenses: number
  healthScore: number
  iotDevicesOnline: number
  unreadNotifications: number
}

export default function DashboardPage() {
  const { data: session } = useSession()
  const [stats, setStats] = useState<DashboardStats>({
    todayEvents: 0,
    pendingGoals: 0,
    monthlyExpenses: 0,
    healthScore: 0,
    iotDevicesOnline: 0,
    unreadNotifications: 0
  })
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simular carregamento de dados do dashboard
    const loadDashboardData = async () => {
      try {
        // Simular dados para demonstração
        setStats({
          todayEvents: 3,
          pendingGoals: 2,
          monthlyExpenses: 2450.80,
          healthScore: 85,
          iotDevicesOnline: 8,
          unreadNotifications: 5
        })

        setRecommendations([
          {
            id: 1,
            title: 'Otimize sua manhã',
            content: 'Você tem 3 reuniões hoje. Sugiro começar 30 minutos mais cedo para se preparar melhor.',
            category: 'agenda',
            priority: 4,
            icon: Calendar
          },
          {
            id: 2,
            title: 'Meta de exercícios',
            content: 'Você está a apenas 2 dias de completar sua meta semanal de exercícios!',
            category: 'health',
            priority: 3,
            icon: Heart
          },
          {
            id: 3,
            title: 'Controle de gastos',
            content: 'Seus gastos este mês estão 15% acima da média. Vamos revisar juntos?',
            category: 'finance',
            priority: 5,
            icon: DollarSign
          }
        ])
      } catch (error) {
        console.error('Erro ao carregar dados do dashboard:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  const statCards = [
    {
      title: 'Eventos Hoje',
      value: stats.todayEvents,
      icon: Calendar,
      color: 'bg-blue-500',
      change: '+2 desde ontem'
    },
    {
      title: 'Metas Ativas',
      value: stats.pendingGoals,
      icon: Target,
      color: 'bg-green-500',
      change: '1 próxima do prazo'
    },
    {
      title: 'Gastos do Mês',
      value: `R$ ${stats.monthlyExpenses.toFixed(2)}`,
      icon: DollarSign,
      color: 'bg-yellow-500',
      change: '+15% vs mês anterior'
    },
    {
      title: 'Score de Saúde',
      value: `${stats.healthScore}%`,
      icon: Heart,
      color: 'bg-red-500',
      change: '+5% esta semana'
    },
    {
      title: 'Dispositivos IoT',
      value: `${stats.iotDevicesOnline}/10`,
      icon: Home,
      color: 'bg-purple-500',
      change: '2 offline'
    },
    {
      title: 'Notificações',
      value: stats.unreadNotifications,
      icon: AlertCircle,
      color: 'bg-orange-500',
      change: '3 importantes'
    }
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white">
          <h2 className="text-2xl font-bold mb-2">
            Bom dia, {session?.user?.name}! 👋
          </h2>
          <p className="text-blue-100 mb-4">
            Aqui está um resumo do seu dia. A BazeX está aqui para te ajudar a ser mais produtivo!
          </p>
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-1">
              <Clock className="h-4 w-4" />
              <span>Última atualização: agora</span>
            </div>
            <div className="flex items-center space-x-1">
              <CheckCircle className="h-4 w-4" />
              <span>Sistema funcionando normalmente</span>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {statCards.map((card, index) => (
            <div
              key={index}
              className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${card.color}`}>
                  <card.icon className="h-6 w-6 text-white" />
                </div>
                <TrendingUp className="h-4 w-4 text-green-500" />
              </div>
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                {card.title}
              </h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {card.value}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {card.change}
              </p>
            </div>
          ))}
        </div>

        {/* Recommendations Section */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Recomendações Proativas
            </h3>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Baseado no seu perfil e atividades
            </span>
          </div>

          <div className="space-y-4">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                className="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
              >
                <div className="p-2 bg-white dark:bg-gray-800 rounded-lg">
                  <rec.icon className="h-5 w-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-1">
                    {rec.title}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {rec.content}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400 px-2 py-1 rounded">
                    Prioridade {rec.priority}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow text-left">
            <MessageCircle className="h-8 w-8 text-blue-600 mb-2" />
            <h4 className="font-medium text-gray-900 dark:text-white">Chat com IA</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">Converse com a BazeX</p>
          </button>

          <button className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow text-left">
            <Calendar className="h-8 w-8 text-green-600 mb-2" />
            <h4 className="font-medium text-gray-900 dark:text-white">Nova Agenda</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">Agendar compromisso</p>
          </button>

          <button className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow text-left">
            <Target className="h-8 w-8 text-purple-600 mb-2" />
            <h4 className="font-medium text-gray-900 dark:text-white">Nova Meta</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">Definir objetivo</p>
          </button>

          <button className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow text-left">
            <DollarSign className="h-8 w-8 text-yellow-600 mb-2" />
            <h4 className="font-medium text-gray-900 dark:text-white">Novo Gasto</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">Registrar despesa</p>
          </button>
        </div>
      </div>
    </DashboardLayout>
  )
}
