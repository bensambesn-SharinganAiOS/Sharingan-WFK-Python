import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import ChatInterface from './components/ChatInterface'
import GenomeVisualizer from './components/GenomeVisualizer'
import BrowserControl from './components/BrowserControl'
import KaliToolsPanel from './components/KaliToolsPanel'
import Monitoring from './components/Monitoring'
import './App.css'

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-dark text-text">
        <Sidebar />
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/chat" element={<ChatInterface />} />
            <Route path="/genome" element={<GenomeVisualizer />} />
            <Route path="/browser" element={<BrowserControl />} />
            <Route path="/kali" element={<KaliToolsPanel />} />
            <Route path="/monitoring" element={<Monitoring />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App