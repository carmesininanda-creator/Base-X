
'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/Layout/DashboardLayout'
import { Home, Lightbulb, Thermometer, Shield, Tv, Power, Settings, Plus, Wifi, WifiOff } from 'lucide-react'

interface IoTDevice {
  id: string
  name: string
  type: string
  room: string
  status: 'online' | 'offline' | 'error'
  properties: any
  lastUpdated: string
}

export default function IoTPage() {
  const [devices, setDevices] = useState<IoTDevice[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedRoom, setSelectedRoom] = useState<string>('all')

  useEffect(() => {
    loadDevices()
  }, [])

  const loadDevices = async () => {
    try {
      // Simular dados para demonstração
      const mockDevices: IoTDevice[] = [
        {
          id: '1',
          name: 'Lâmpada Principal',
          type: 'light',
          room: 'sala',
          status: 'online',
          properties: { brightness: 80, color: '#ffffff', isOn: true },
          lastUpdated: new Date().toISOString()
        },
        {
          id: '2',
          name: 'Ar Condicionado',
          type: 'thermostat',
          room: 'quarto',
          status: 'online',
          properties: { temperature: 22, targetTemp: 24, mode: 'cool', isOn: true },
          lastUpdated: new Date().toISOString()
        },
        {
          id: '3',
          name: 'Câmera de Segurança',
          type: 'security',
          room: 'entrada',
          status: 'online',
          properties: { recording: true, motionDetection: true, nightVision: false },
          lastUpdated: new Date().toISOString()
        },
        {
          id: '4',
          name: 'Smart TV',
          type: 'appliance',
          room: 'sala',
          status: 'offline',
          properties: { volume: 25, channel: 'Netflix', isOn: false },
          lastUpdated: new Date(Date.now() - 30 * 60 * 1000).toISOString()
        },
        {
          id: '5',
          name: 'Lâmpada do Quarto',
          type: 'light',
          room: 'quarto',
          status: 'online',
          properties: { brightness: 40, color: '#ffaa00', isOn: true },
          lastUpdated: new Date().toISOString()
        },
        {
          id: '6',
          name: 'Sensor de Porta',
          type: 'security',
          room: 'entrada',
          status: 'error',
          properties: { isOpen: false, batteryLevel: 15 },
          lastUpdated: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
        }
      ]
      setDevices(mockDevices)
    } catch (error) {
      console.error('Erro ao carregar dispositivos:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const rooms = [
    { id: 'all', name: 'Todos os Cômodos' },
    { id: 'sala', name: 'Sala' },
    { id: 'quarto', name: 'Quarto' },
    { id: 'cozinha', name: 'Cozinha' },
    { id: 'entrada', name: 'Entrada' }
  ]

  const filteredDevices = selectedRoom === 'all' 
    ? devices 
    : devices.filter(device => device.room === selectedRoom)

  const onlineDevices = devices.filter(device => device.status === 'online').length
  const offlineDevices = devices.filter(device => device.status === 'offline').length
  const errorDevices = devices.filter(device => device.status === 'error').length

  const getDeviceIcon = (type: string) => {
    const icons = {
      light: Lightbulb,
      thermostat: Thermometer,
      security: Shield,
      appliance: Tv
    }
    return icons[type as keyof typeof icons] || Home
  }

  const getStatusColor = (status: string) => {
    const colors = {
      online: 'text-green-500',
      offline: 'text-gray-500',
      error: 'text-red-500'
    }
    return colors[status as keyof typeof colors] || 'text-gray-500'
  }

  const getStatusBg = (status: string) => {
    const colors = {
      online: 'bg-green-100 dark:bg-green-900',
      offline: 'bg-gray-100 dark:bg-gray-700',
      error: 'bg-red-100 dark:bg-red-900'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 dark:bg-gray-700'
  }

  const toggleDevice = async (deviceId: string) => {
    setDevices(prev => prev.map(device => {
      if (device.id === deviceId) {
        const newStatus = device.status === 'online' ? 'offline' : 'online'
        return {
          ...device,
          status: newStatus,
          properties: {
            ...device.properties,
            isOn: newStatus === 'online'
          },
          lastUpdated: new Date().toISOString()
        }
      }
      return device
    }))
  }

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
              Controle IoT Casa
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Gerencie todos os dispositivos inteligentes da sua casa
            </p>
          </div>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
            <Plus className="h-4 w-4" />
            <span>Adicionar Dispositivo</span>
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                <Wifi className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              Online
            </h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {onlineDevices}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <WifiOff className="h-6 w-6 text-gray-600" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              Offline
            </h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {offlineDevices}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-red-100 dark:bg-red-900 rounded-lg">
                <Shield className="h-6 w-6 text-red-600" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              Com Erro
            </h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {errorDevices}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Home className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              Total
            </h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {devices.length}
            </p>
          </div>
        </div>

        {/* AI Automation Suggestions */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            🏠 Automações Inteligentes
          </h3>
          <div className="space-y-2">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              • Detectei que você sempre liga as luzes da sala às 18h. Quer que eu automatize isso?
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              • O sensor da porta está com bateria baixa (15%). Sugiro trocar em breve.
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              • Baseado no clima, posso ajustar automaticamente o ar condicionado para economizar energia.
            </p>
          </div>
        </div>

        {/* Room Filter */}
        <div className="flex flex-wrap gap-2">
          {rooms.map((room) => (
            <button
              key={room.id}
              onClick={() => setSelectedRoom(room.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedRoom === room.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {room.name}
            </button>
          ))}
        </div>

        {/* Devices Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDevices.map((device) => {
            const DeviceIcon = getDeviceIcon(device.type)
            return (
              <div
                key={device.id}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`p-3 rounded-lg ${getStatusBg(device.status)}`}>
                      <DeviceIcon className={`h-6 w-6 ${getStatusColor(device.status)}`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {device.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                        {device.room}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      device.status === 'online' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : device.status === 'error'
                        ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                    }`}>
                      {device.status === 'online' ? 'Online' : device.status === 'error' ? 'Erro' : 'Offline'}
                    </span>
                  </div>
                </div>

                {/* Device Properties */}
                <div className="space-y-3 mb-4">
                  {device.type === 'light' && (
                    <>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Brilho:</span>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {device.properties.brightness}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${device.properties.brightness}%` }}
                        ></div>
                      </div>
                    </>
                  )}

                  {device.type === 'thermostat' && (
                    <>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Temperatura:</span>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {device.properties.temperature}°C
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Meta:</span>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {device.properties.targetTemp}°C
                        </span>
                      </div>
                    </>
                  )}

                  {device.type === 'security' && device.properties.batteryLevel && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Bateria:</span>
                      <span className={`text-sm font-medium ${
                        device.properties.batteryLevel < 20 ? 'text-red-600' : 'text-gray-900 dark:text-white'
                      }`}>
                        {device.properties.batteryLevel}%
                      </span>
                    </div>
                  )}
                </div>

                {/* Controls */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={() => toggleDevice(device.id)}
                    disabled={device.status === 'error'}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      device.properties.isOn && device.status === 'online'
                        ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900 dark:text-green-200'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    <Power className="h-4 w-4" />
                    <span>
                      {device.properties.isOn && device.status === 'online' ? 'Desligar' : 'Ligar'}
                    </span>
                  </button>

                  <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                    <Settings className="h-4 w-4" />
                  </button>
                </div>

                {/* Last Updated */}
                <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                  Atualizado: {new Date(device.lastUpdated).toLocaleString('pt-BR')}
                </div>
              </div>
            )
          })}
        </div>

        {filteredDevices.length === 0 && (
          <div className="text-center py-12">
            <Home className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Nenhum dispositivo encontrado
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Adicione dispositivos IoT para começar a controlar sua casa inteligente.
            </p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors">
              Adicionar primeiro dispositivo
            </button>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
