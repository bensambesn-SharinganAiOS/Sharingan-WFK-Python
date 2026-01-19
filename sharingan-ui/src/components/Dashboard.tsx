import React from 'react'
import { useSystemStatus } from '../hooks/useSystemStatus'
import {
  Cpu,
  HardDrive,
  MemoryStick,
  Network,
  Activity,
  Clock,
  Zap,
  Shield,
  Brain,
  Bug,
  Globe,
  Database
} from 'lucide-react'

interface DashboardProps {}

const Dashboard: React.FC<DashboardProps> = () => {
  const { metrics, systems, activities, logs, loading, error, refreshData } = useSystemStatus()

  // Mock data for demonstration (will be replaced with real data)
  const mockSystems = [
    { name: 'AI Core', icon: 'Brain', status: 'OK' },
    { name: 'Memory', icon: 'Database', status: 'OK' },
    { name: 'Consciousness', icon: 'Brain', status: 'Active' },
    { name: 'Kali Tools', icon: 'Bug', status: 'Ready' },
    { name: 'VPN/Tor', icon: 'Shield', status: 'Active' },
    { name: 'Cloud', icon: 'Globe', status: 'OK' },
    { name: 'Permissions', icon: 'Shield', status: 'Root' },
    { name: 'Auto-Scale', icon: 'Activity', status: 'OK' },
    { name: 'Psychic Locks', icon: 'Shield', status: 'Active' },
    { name: 'Mission', icon: 'Zap', status: 'Ready' }
  ]

  const mockActivities = [
    { type: 'system', icon: 'Activity', text: 'Système démarré avec succès', time: '12:30:15' },
    { type: 'ai', icon: 'Brain', text: 'Soul consciousness level: 4.0', time: '12:29:45' },
    { type: 'genome', icon: 'Database', text: 'Genome evolution completed', time: '12:28:30' },
    { type: 'kali', icon: 'Bug', text: 'Kali tools synchronized', time: '12:27:15' },
    { type: 'security', icon: 'Shield', text: 'Security audit passed', time: '12:26:00' }
  ]

  const mockLogs = [
    '[INFO] System initialization completed',
    '[INFO] AI providers loaded: 4',
    '[INFO] Genome memory: 1,247 genes active',
    '[INFO] Kali tools: 89/100 tools available',
    '[INFO] WebSocket connections established'
  ]

  const systems = mockSystems
  const activities = mockActivities
  const logs = mockLogs

  const getSystemIcon = (iconName: string) => {
    const icons: Record<string, any> = {
      Brain, Database, Bug, Shield, Globe, Activity, Zap, Cpu
    }
    return icons[iconName] || Activity
  }

  const getActivityIcon = (iconName: string) => {
    const icons: Record<string, any> = {
      Activity, Brain, Database, Bug, Shield
    }
    return icons[iconName] || Activity
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-danger text-lg mb-2">Erreur de connexion</div>
          <div className="text-text-muted">{error}</div>
          <button
            onClick={refreshData}
            className="btn-primary mt-4"
          >
            Réessayer
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gradient">Dashboard</h1>
          <p className="text-text-muted mt-1">Vue d'ensemble du système Sharingan OS</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-card-bg rounded-lg border border-gray-700">
            <div className="status-indicator status-online"></div>
            <span className="text-success font-medium">Système Opérationnel</span>
          </div>
          <button
            onClick={refreshData}
            className="btn-secondary"
          >
            <Activity size={16} className="mr-2" />
            Actualiser
          </button>
        </div>
      </div>

      {/* Métriques principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="metric-card card">
          <div className="flex items-center justify-between">
            <div>
              <div className="metric-label">CPU</div>
              <div className="metric-value">{metrics?.cpu_percent?.toFixed(1) || '0.0'}%</div>
            </div>
            <Cpu className="text-primary" size={32} />
          </div>
          <div className="progress mt-3">
            <div
              className="progress-bar"
              style={{ width: `${metrics?.cpu_percent || 0}%` }}
            ></div>
          </div>
        </div>

        <div className="metric-card card">
          <div className="flex items-center justify-between">
            <div>
              <div className="metric-label">Mémoire</div>
              <div className="metric-value">{metrics?.memory_percent?.toFixed(1) || '0.0'}%</div>
            </div>
            <MemoryStick className="text-primary" size={32} />
          </div>
          <div className="progress mt-3">
            <div
              className="progress-bar"
              style={{ width: `${metrics?.memory_percent || 0}%` }}
            ></div>
          </div>
        </div>

        <div className="metric-card card">
          <div className="flex items-center justify-between">
            <div>
              <div className="metric-label">Disque</div>
              <div className="metric-value">{metrics?.disk_percent?.toFixed(1) || '0.0'}%</div>
            </div>
            <HardDrive className="text-primary" size={32} />
          </div>
          <div className="progress mt-3">
            <div
              className="progress-bar"
              style={{ width: `${metrics?.disk_percent || 0}%` }}
            ></div>
          </div>
        </div>

        <div className="metric-card card">
          <div className="flex items-center justify-between">
            <div>
              <div className="metric-label">Connexions</div>
              <div className="metric-value">{metrics?.network_connections || 0}</div>
            </div>
            <Network className="text-primary" size={32} />
          </div>
        </div>
      </div>

      {/* État des systèmes */}
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <span>État des Systèmes</span>
          <div className="flex items-center gap-2 text-xs text-text-muted">
            <Clock size={14} />
            Dernière mise à jour: {new Date().toLocaleTimeString()}
          </div>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {systems.map((system, index) => {
              const IconComponent = getSystemIcon(system.icon)
              return (
                <div key={index} className="system-item">
                  <div className="system-icon">
                    <IconComponent
                      className={system.status === 'Active' || system.status === 'OK' ? 'text-success' : 'text-text-muted'}
                      size={20}
                    />
                  </div>
                  <div className="system-name">{system.name}</div>
                  <div className={`system-status ${
                    system.status === 'Active' || system.status === 'OK' || system.status === 'Ready'
                      ? 'text-success'
                      : system.status === 'Root'
                      ? 'text-primary'
                      : 'text-text-muted'
                  }`}>
                    {system.status}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Activités et Console */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activités récentes */}
        <div className="lg:col-span-2 card">
          <div className="card-header">Activités Récentes</div>
          <div className="card-body">
            <div className="space-y-3 max-h-80 overflow-y-auto scrollbar-thin">
              {activities.map((activity, index) => {
                const IconComponent = getActivityIcon(activity.icon)
                return (
                  <div key={index} className="activity-item">
                    <div className="activity-icon">
                      <IconComponent size={16} />
                    </div>
                    <div>
                      <div className="activity-text">{activity.text}</div>
                      <div className="activity-time">{activity.time}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Console système */}
        <div className="card">
          <div className="card-header">Console Système</div>
          <div className="card-body">
            <div className="console scrollbar-thin">
              {logs.slice(0, 10).map((log, index) => (
                <div key={index} className="console-line info">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Actions rapides */}
      <div className="card">
        <div className="card-header">Actions Rapides</div>
        <div className="card-body">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="btn-secondary flex items-center justify-center gap-2 py-3">
              <Network size={16} />
              Scan Ports
            </button>
            <button className="btn-secondary flex items-center justify-center gap-2 py-3">
              <Activity size={16} />
              Reconnaissance
            </button>
            <button className="btn-secondary flex items-center justify-center gap-2 py-3">
              <Shield size={16} />
              Vulnérabilités
            </button>
            <button className="btn-secondary flex items-center justify-center gap-2 py-3">
              <Brain size={16} />
              Chat IA
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard