# 🖥️ Sharingan OS - Interface Web React

Interface utilisateur moderne et réactive pour Sharingan OS, développée avec React, TypeScript et TailwindCSS.

## 🚀 Démarrage Rapide

### Prérequis
- Node.js 20+
- Backend Sharingan OS en cours d'exécution (port 8181)

### Installation
```bash
cd sharingan-ui
npm install
```

### Développement
```bash
# Mode développement avec hot reload
npm run dev

# L'interface sera accessible sur http://localhost:3737
```

### Build de production
```bash
npm run build
npm run preview
```

## 🏗️ Architecture

### Structure des dossiers
```
sharingan-ui/
├── src/
│   ├── components/     # Composants React
│   ├── hooks/         # Hooks personnalisés
│   ├── services/      # Services API
│   ├── types/         # Types TypeScript
│   └── utils/         # Utilitaires
├── public/            # Assets statiques
├── package.json       # Dépendances
├── vite.config.ts     # Configuration Vite
├── tailwind.config.js # Configuration Tailwind
└── tsconfig.json      # Configuration TypeScript
```

### Technologies utilisées
- **React 18** - Framework UI moderne
- **TypeScript** - Typage statique
- **Vite** - Build tool ultra-rapide
- **TailwindCSS** - Framework CSS utilitaire
- **Socket.IO** - Communication temps réel
- **React Router** - Routing SPA
- **Recharts** - Graphiques et métriques
- **Lucide React** - Icônes modernes

## 🎨 Fonctionnalités

### Dashboard Principal
- **Métriques temps réel** : CPU, RAM, Disque, Connexions
- **État des systèmes** : AI Core, Memory, Consciousness, Kali Tools, VPN/Tor
- **Activités récentes** : Historique des actions système
- **Console système** : Logs et messages temps réel

### Interface Chat IA
- **Conversation avec Soul** : Intégration directe avec Sharingan Soul
- **Émotions et motivations** : Affichage des états émotionnels
- **Actions exécutées** : Suivi des actions réalisées
- **Historique conversationnel** : Persistance des échanges

### Visualisateur Genome Memory
- **Arbre généalogique** : Représentation visuelle des gènes
- **Graphiques évolution** : Courbes de performance et mutations
- **Recherche et filtrage** : Exploration interactive
- **Historique mutations** : Timeline des changements

### Panneau Contrôle Navigateurs
- **Navigateurs actifs** : Liste et statut temps réel
- **Contrôles navigation** : Boutons pour actions courantes
- **Screenshots** : Captures d'écran à la demande
- **Historique actions** : Logs des interactions

### Panneau Outils Kali
- **État des outils** : Installation et disponibilité
- **Lancement rapide** : Interface pour exécuter des scans
- **Résultats temps réel** : Affichage des outputs
- **Gestion ressources** : Monitoring CPU/RAM des outils

### Monitoring Système
- **Graphiques avancés** : Métriques détaillées avec Recharts
- **Logs système** : Historique complet des événements
- **Diagnostics** : Outils de débogage intégrés
- **Alertes** : Notifications temps réel des anomalies

## 🔌 APIs Utilisées

### Endpoints Backend
```typescript
// Métriques système
GET /api/status          // État général du système
GET /api/metrics         // Métriques détaillées
GET /api/logs           // Logs système

// Chat IA
POST /api/chat          // Conversation avec Soul
GET /api/chat/history   // Historique conversationnel

// Genome Memory
GET /api/genome/genes   // Liste des gènes
GET /api/genome/mutations // Historique mutations
GET /api/genome/evolution // Métriques évolution

// Kali Tools
GET /api/kali/status    // État des outils
POST /api/kali/execute  // Exécution d'outil
GET /api/kali/results   // Résultats d'exécution

// Browser Control
GET /api/browser/status // Navigateurs actifs
POST /api/browser/navigate // Navigation
POST /api/browser/screenshot // Capture d'écran
```

### Communication Temps Réel
```typescript
// Socket.IO events
socket.on('system_metrics', (data) => {
  // Mise à jour métriques temps réel
});

socket.on('activity_update', (activity) => {
  // Nouvelle activité système
});

socket.on('chat_response', (message) => {
  // Réponse IA reçue
});
```

## 🎨 Thème et Design

### Palette de couleurs
```css
--primary: #6366f1      /* Bleu principal */
--success: #10b981      /* Vert succès */
--dark: #0f172a        /* Fond sombre */
--card-bg: #1e293b     /* Fond cartes */
--text: #e2e8f0        /* Texte principal */
--text-muted: #94a3b8  /* Texte secondaire */
```

### Composants de base
```typescript
// Boutons
<button className="btn-primary">Action principale</button>
<button className="btn-secondary">Action secondaire</button>

// Cartes
<div className="card">
  <div className="card-header">Titre</div>
  <div className="card-body">Contenu</div>
</div>

// Inputs
<input className="input" placeholder="Texte..." />

// Indicateurs de statut
<div className="status-indicator status-online"></div>
<div className="status-indicator status-offline"></div>
```

## 🔧 Développement

### Scripts disponibles
```bash
npm run dev      # Développement avec hot reload
npm run build    # Build de production
npm run preview  # Prévisualisation build
npm run lint     # Vérification ESLint
```

### Ajout de nouveaux composants
```typescript
// src/components/MyComponent.tsx
import React from 'react'

interface MyComponentProps {
  title: string
  data?: any[]
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, data = [] }) => {
  return (
    <div className="card">
      <div className="card-header">{title}</div>
      <div className="card-body">
        {/* Composant content */}
      </div>
    </div>
  )
}
```

### Utilisation des hooks personnalisés
```typescript
// src/hooks/useSystemMetrics.ts
import { useState, useEffect } from 'react'
import { io } from 'socket.io-client'

export const useSystemMetrics = () => {
  const [metrics, setMetrics] = useState(null)

  useEffect(() => {
    const socket = io('http://localhost:8181')

    socket.on('system_metrics', (data) => {
      setMetrics(data)
    })

    return () => socket.disconnect()
  }, [])

  return metrics
}
```

## 🚀 Déploiement

### Configuration de production
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser'
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8181',
        changeOrigin: true
      }
    }
  }
})
```

### Variables d'environnement
```env
# .env.production
VITE_API_URL=https://api.sharingan-os.com
VITE_WS_URL=wss://api.sharingan-os.com
VITE_APP_TITLE=Sharingan OS - Production
```

### Docker (optionnel)
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3737
CMD ["npm", "run", "preview"]
```

## 🔒 Sécurité

### Mesures implémentées
- **TypeScript strict** : Prévention des erreurs runtime
- **Validation des inputs** : Sanitisation côté client
- **HTTPS obligatoire** : Communication chiffrée
- **CORS configuré** : Restrictions d'origine
- **Authentification** : Sessions sécurisées

### Bonnes pratiques
```typescript
// Validation des données
const validateInput = (input: string): boolean => {
  return input.length > 0 && input.length < 1000
}

// Sanitisation
const sanitizeHtml = (html: string): string => {
  return DOMPurify.sanitize(html)
}

// Gestion d'erreurs
try {
  const result = await apiCall()
} catch (error) {
  console.error('API Error:', error)
  // Afficher message d'erreur utilisateur
}
```

## 📱 Responsive Design

### Breakpoints
```css
/* Mobile */
@media (max-width: 640px) { /* sm */ }

/* Tablette */
@media (min-width: 641px) and (max-width: 1024px) { /* md */ }

/* Desktop */
@media (min-width: 1025px) { /* lg */ }
```

### Composants adaptatifs
```typescript
const ResponsiveGrid = ({ children }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    {children}
  </div>
)
```

## 🧪 Tests

### Configuration des tests
```typescript
// src/setupTests.ts
import '@testing-library/jest-dom'

// Configuration des mocks API
global.fetch = jest.fn()
```

### Tests de composants
```typescript
// src/components/Dashboard.test.tsx
import { render, screen } from '@testing-library/react'
import Dashboard from './Dashboard'

test('renders dashboard title', () => {
  render(<Dashboard />)
  expect(screen.getByText('Dashboard')).toBeInTheDocument()
})
```

## 📚 Ressources

### Documentation
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [Vite Guide](https://vitejs.dev/guide/)

### Outils de développement
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [Redux DevTools](https://github.com/reduxjs/redux-devtools)
- [ESLint](https://eslint.org/docs/user-guide/getting-started)

---

*Cette interface web apporte une expérience utilisateur moderne et intuitive tout en préservant toutes les capacités avancées de Sharingan OS.*