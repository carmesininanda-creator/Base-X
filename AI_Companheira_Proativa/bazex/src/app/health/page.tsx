
'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/Layout/DashboardLayout'
import { Heart, Activity, Droplets, Moon, Footprints, Plus, TrendingUp, Calendar } from 'lucide-react'

interface HealthData {
  id: string
  type: string
  value: number
  unit: string
  date: string
  notes?: string
}

export default function HealthPage() {
  const [healthData, setHealthData] = useState<HealthData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState<string>('all')

  useEffect(() => {
    loadHealthData()
  }, [])

  const loadHealthData = async () => {
    try {
      // Simular dados para demonstração
      const mockData: HealthData[] = [
        {
          id: '1',
          type: 'weight',
          value: 75.2,
          unit: 'kg',
          date: '2024-08-17',
          notes: 'Após exercício matinal'
        },
        {
          id: '2',
          type: 'steps',
          value: 8500,
          unit: 'passos',
          date: '2024-08-17'
        },
        {
          id: '3',
          type: 'water',
          value: 2.1,
          unit: 'litros',
          date: '2024-08-17'
        },
        {
          id: '4',
          type: 'sleep',
          value: 7.5,
          unit: 'horas',
          date: '2024-08-16',
          notes: 'Sono reparador'
        },
        {
          id: '5',
          type: 'exercise',
          value: 45,
          unit: 'minutos',
          date: '2024-08-17',
          notes: 'Corrida no parque'
        },
        {
          id: '6',
          type: 'weight',
          value: 75.5,
          unit: 'kg',
          date: '2024-08-16'
        },
        {
          id: '7',
          type: 'steps',
          value: 12000,
          unit: 'passos',
          date: '2024-08-16'
        }
      ]
      setHealthData(mockData)
    } catch (error) {
      console.error('Erro ao carregar dados de saúde:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const metrics = [
    { id: 'all', name: 'Todos', icon: Heart, color: 'bg-red-500' },
    { id: 'weight', name: 'Peso', icon: Activity, color: 'bg-blue-500' },
    { id: 'steps', name: 'Passos', icon: Footprints, color: 'bg-green-500' },
    { id: 'water', name: 'Água', icon: Droplets, color: 'bg-cyan-500' },
    { id: 'sleep', name: 'Sono', icon: Moon, color: 'bg-purple-500' },
    { id: 'exercise', name: 'Exercício', icon: Activity, color: 'bg-orange-500' }
  ]

  const filteredData = selectedMetric === 'all' 
    ? healthData 
    : healthData.filter(data => data.type === selectedMetric)

  // Calcular estatísticas
  const todaySteps = healthData.find(d => d.type === 'steps' && d.date === '2024-08-17')?.value || 0
  const todayWater = healthData.find(d => d.type === 'water' && d.date === '2024-08-17')?.value || 0
  const lastSleep = healthData.find(d => d.type === 'sleep')?.value || 0
  const currentWeight = healthData.find(d => d.type === 'weight' && d.date === '2024-08-17')?.value || 0

  const getMetricIcon = (type: string) => {
    const metric = metrics.find(m => m.id === type)
    return metric?.icon || Heart
  }

  const getMetricColor = (type: string) => {
    const metric = metrics.find(m => m.id === type)
    return metric?.color || 'bg-gray-500'
  }

  const getHealthScore = () => {
    let score = 0
    if (todaySteps >= 10000) score += 25
    else if (todaySteps >= 8000) score += 20
    else if (todaySteps >= 5000) score += 15
    
    if (todayWater >= 2.5) score += 25
    else if (todayWater >= 2.0) score += 20
    else if (todayWater >= 1.5) score += 15
    
    if (lastSleep >= 8) score += 25
    else if (lastSleep >= 7) score += 20
    else if (lastSleep >= 6) score += 15
    
    const hasExercise = healthData.some(d => d.type === 'exercise' && d.date === '2024-08-17')
    if (hasExercise) score += 25
    
    return Math.min(score, 100)
  }

  const healthScore = getHealthScore()

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Saúde & Bem-estar
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Acompanhe sua saúde com insights personalizados da IA
            </p>
          </div>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
            <Plus className="h-4 w-4" />
            <span>Registrar Dados</span>
          </button>
        </div>

        {/* Health Score */}
        <div className="bg-gradient-to-r from-green-500 to-blue-500 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">Score de Saúde Hoje</h2>
              <p className="text-green-100">
                Baseado nos seus dados de atividade, hidratação, sono e exercícios
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold mb-2">{healthScore}</div>
              <div className="text-sm text-green-100">de 100 pontos</div>
            </div>
          </div>
          <div className="mt-4 w-full bg-white/20 rounded-full h-3">
            <div
              className="bg-white h-3 rounded-full transition-all duration-500"
              style={{ width: `${healthScore}%` }}
            ></div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                <Footprints className="h-6 w-6 text-green-600" />
              </div>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              Passos Hoje
            </h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {todaySteps.toLocaleString()}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Meta: 10.000 passos
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-cyan-100 dark:bg-cyan-900 rounded-lg">
                <Droplets className="h-6 w-6 text-cyan-600" />
              </div>
              <Calendar className="h-4 w-4 text-blue-500" />
            </div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              Água Hoje
            </h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {todayWater}L
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Meta: 2.5L por dia
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <Moon className="h-6 w-6 text-purple-600" />
              </div>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              Sono Ontem
            </h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {lastSleep}h
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Meta: 8h por noite
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Activity className="h-6 w-6 text-blue-600" />
              </div>
              <Heart className="h-4 w-4 text-red-500" />
            </div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              Peso Atual
            </h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {currentWeight}kg
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              -0.3kg esta semana
            </p>
          </div>
        </div>

        {/* AI Health Insights */}
        <div className="bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/20 dark:to-purple-900/20 rounded-xl p-6 border border-pink-200 dark:border-pink-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            🏥 Insights de Saúde da IA
          </h3>
          <div className="space-y-2">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              • Parabéns! Você está mantendo uma rotina consistente de exercícios. Continue assim!
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              • Sua hidratação está boa, mas tente beber mais água pela manhã para melhor absorção.
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              • Baseado no seu sono, sugiro evitar telas 1h antes de dormir para melhor qualidade.
            </p>
          </div>
        </div>

        {/* Metric Filter */}
        <div className="flex flex-wrap gap-2">
          {metrics.map((metric) => {
            const MetricIcon = metric.icon
            return (
              <button
                key={metric.id}
                onClick={() => setSelectedMetric(metric.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2 ${
                  selectedMetric === metric.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                <MetricIcon className="h-4 w-4" />
                <span>{metric.name}</span>
              </button>
            )
          })}
        </div>

        {/* Health Data List */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Registros Recentes
            </h3>
          </div>
          
          <div className="p-6">
            <div className="space-y-4">
              {filteredData.slice(0, 10).map((data) => {
                const MetricIcon = getMetricIcon(data.type)
                return (
                  <div
                    key={data.id}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                  >
                    <div className="flex items-center space-x-4">
                      <div className={`p-3 rounded-lg ${getMetricColor(data.type)}`}>
                        <MetricIcon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white capitalize">
                          {metrics.find(m => m.id === data.type)?.name || data.type}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {new Date(data.date).toLocaleDateString('pt-BR')}
                          {data.notes && ` • ${data.notes}`}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-gray-900 dark:text-white">
                        {data.value.toLocaleString()} {data.unit}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>

            {filteredData.length === 0 && (
              <div className="text-center py-12">
                <Heart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Nenhum registro encontrado
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Comece registrando seus dados de saúde para acompanhar seu progresso.
                </p>
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors">
                  Registrar primeiro dado
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
