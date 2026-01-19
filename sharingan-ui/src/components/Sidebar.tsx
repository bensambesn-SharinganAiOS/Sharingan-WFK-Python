import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Cpu,
  MessageSquare,
  Database,
  Globe,
  Bug,
  Activity,
  Home,
  Brain
} from 'lucide-react'

interface SidebarProps {}

const Sidebar: React.FC<SidebarProps> = () => {
  const location = useLocation()

  const menuItems = [
    { path: '/', icon: Home, label: 'Dashboard', description: 'Vue d\'ensemble' },
    { path: '/chat', icon: MessageSquare, label: 'Chat IA', description: 'Conversation avec Soul' },
    { path: '/genome', icon: Brain, label: 'Genome Memory', description: 'Mémoire évolutive' },
    { path: '/browser', icon: Globe, label: 'Navigateurs', description: 'Contrôle hybride' },
    { path: '/kali', icon: Bug, label: 'Kali Tools', description: 'Outils cybersécurité' },
    { path: '/monitoring', icon: Activity, label: 'Monitoring', description: 'Métriques système' }
  ]

  return (
    <div className="w-64 bg-dark h-screen fixed left-0 top-0 border-r border-gray-700 overflow-y-auto">
      {/* Header */}
      <div className="p-6 border-b border-gray-700">
        <div className="text-primary font-bold text-xl mb-1">SHARINGAN OS</div>
        <div className="text-text-muted text-xs uppercase tracking-wide">AI Cybersecurity</div>
        <div className="flex items-center gap-2 mt-3">
          <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
          <span className="text-success text-xs font-medium">Système Opérationnel</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4">
        <div className="text-text-muted text-xs uppercase tracking-wide mb-3 font-medium">
          Navigation
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center gap-3 px-3 py-3 rounded-lg mb-2 transition-all duration-200
                ${isActive
                  ? 'bg-primary/20 text-primary border-l-2 border-primary'
                  : 'text-text hover:bg-card-bg hover:text-primary'
                }
              `}
            >
              <Icon size={18} />
              <div className="flex-1">
                <div className="font-medium text-sm">{item.label}</div>
                <div className="text-xs text-text-muted">{item.description}</div>
              </div>
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700">
        <div className="text-center">
          <div className="text-text-muted text-xs">Version 1.0.0</div>
          <div className="text-text-muted text-xs mt-1">Consciousness Level: 4.0</div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar