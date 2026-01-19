import { useState, useEffect } from 'react'
import { io, Socket } from 'socket.io-client'

interface SystemMetrics {
  cpu_percent: number
  memory_percent: number
  disk_percent: number
  network_connections: number
  timestamp: string
}

interface SystemStatus {
  metrics: SystemMetrics | null
  systems: Array<{
    name: string
    status: string
    icon: string
  }>
  activities: Array<{
    type: string
    icon: string
    text: string
    time: string
  }>
  logs: string[]
  loading: boolean
  error: string | null
}

export const useSystemStatus = () => {
  const [status, setStatus] = useState<SystemStatus>({
    metrics: null,
    systems: [],
    activities: [],
    logs: [],
    loading: true,
    error: null
  })

  const [socket, setSocket] = useState<Socket | null>(null)

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io('http://localhost:8181', {
      transports: ['websocket', 'polling']
    })

    setSocket(newSocket)

    // Socket event handlers
    newSocket.on('connect', () => {
      console.log('Connected to Sharingan OS')
      setStatus(prev => ({ ...prev, loading: false }))
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from Sharingan OS')
    })

    newSocket.on('system_metrics', (data: SystemMetrics) => {
      setStatus(prev => ({
        ...prev,
        metrics: data,
        loading: false
      }))
    })

    newSocket.on('activity_update', (activity: any) => {
      setStatus(prev => ({
        ...prev,
        activities: [activity, ...prev.activities.slice(0, 9)] // Keep last 10
      }))
    })

    newSocket.on('system_log', (log: string) => {
      setStatus(prev => ({
        ...prev,
        logs: [log, ...prev.logs.slice(0, 19)] // Keep last 20
      }))
    })

    // Initial data fetch
    fetchSystemData()

    return () => {
      newSocket.disconnect()
    }
  }, [])

  const fetchSystemData = async () => {
    try {
      const [metricsRes, systemsRes] = await Promise.all([
        fetch('/api/status'),
        fetch('/api/systems')
      ])

      if (metricsRes.ok) {
        const metrics = await metricsRes.json()
        setStatus(prev => ({ ...prev, metrics }))
      }

      if (systemsRes.ok) {
        const systems = await systemsRes.json()
        setStatus(prev => ({ ...prev, systems }))
      }
    } catch (error) {
      setStatus(prev => ({
        ...prev,
        error: 'Failed to fetch system data',
        loading: false
      }))
    }
  }

  const refreshData = () => {
    fetchSystemData()
  }

  return {
    ...status,
    refreshData,
    socket
  }
}

export const useAPI = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { apiCall, loading, error }
}