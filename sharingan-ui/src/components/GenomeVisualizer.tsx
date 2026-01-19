import React, { useState, useEffect } from 'react'
import { useAPI } from '../hooks/useSystemStatus'
import {
  Dna,
  Database,
  TrendingUp,
  Activity,
  Clock,
  Tag,
  BarChart3,
  Target,
  Zap
} from 'lucide-react'

interface GenomeVisualizerProps {}

interface Gene {
  key: string
  category: string
  priority: number
  created_at: string
  updated_at: string
  success_rate: number
  usage_count: number
  mutations: number
  tags: string[]
  source: string
}

interface EvolutionStats {
  total_genes: number
  total_mutations: number
  categories: Record<string, number>
  avg_success_rate: number
  most_used_gene: {
    key: string
    usage_count: number
    category: string
  } | null
  recent_mutations: number
}

const GenomeVisualizer: React.FC<GenomeVisualizerProps> = () => {
  const { apiCall, loading, error } = useAPI()
  const [genes, setGenes] = useState<Gene[]>([])
  const [evolutionStats, setEvolutionStats] = useState<EvolutionStats | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedGene, setSelectedGene] = useState<Gene | null>(null)

  useEffect(() => {
    loadGenomeData()
  }, [])

  const loadGenomeData = async () => {
    try {
      const [genesResponse, evolutionResponse] = await Promise.all([
        apiCall('/api/genome/genes'),
        apiCall('/api/genome/evolution')
      ])

      if (genesResponse) {
        setGenes(genesResponse.genes || [])
      }

      if (evolutionResponse) {
        setEvolutionStats(evolutionResponse)
      }
    } catch (err) {
      console.error('Failed to load genome data:', err)
    }
  }

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      core: 'bg-red-500',
      security: 'bg-yellow-500',
      performance: 'bg-blue-500',
      feature: 'bg-green-500',
      knowledge: 'bg-purple-500',
      conversation: 'bg-gray-500',
      experimental: 'bg-orange-500'
    }
    return colors[category] || 'bg-gray-400'
  }

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, any> = {
      core: Database,
      security: Shield,
      performance: TrendingUp,
      feature: Zap,
      knowledge: Dna,
      conversation: Activity,
      experimental: Target
    }
    return icons[category] || Database
  }

  const filteredGenes = selectedCategory === 'all'
    ? genes
    : genes.filter(gene => gene.category === selectedCategory)

  const categories = Array.from(new Set(genes.map(gene => gene.category)))

  if (loading && !genes.length) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-card-bg rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="h-32 bg-card-bg rounded"></div>
            <div className="h-32 bg-card-bg rounded"></div>
            <div className="h-32 bg-card-bg rounded"></div>
          </div>
          <div className="h-64 bg-card-bg rounded"></div>
        </div>
      </div>
    )
  }

  if (error && !genes.length) {
    return (
      <div className="p-6">
        <div className="text-center">
          <div className="text-danger text-lg mb-2">Erreur de chargement</div>
          <div className="text-text-muted">{error}</div>
          <button
            onClick={loadGenomeData}
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
          <h1 className="text-3xl font-bold text-gradient mb-1">Genome Memory</h1>
          <p className="text-text-muted">ADN évolutif du système Sharingan</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-card-bg rounded-lg border border-gray-700">
            <Dna className="text-primary" size={16} />
            <span className="font-medium">{genes.length} Gènes</span>
          </div>
          <button
            onClick={loadGenomeData}
            className="btn-secondary"
            disabled={loading}
          >
            <Activity size={16} className="mr-2" />
            Actualiser
          </button>
        </div>
      </div>

      {/* Evolution Stats */}
      {evolutionStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <div className="metric-label">Total Gènes</div>
                <div className="text-2xl font-bold text-primary">{evolutionStats.total_genes}</div>
              </div>
              <Dna className="text-primary" size={24} />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <div className="metric-label">Mutations</div>
                <div className="text-2xl font-bold text-warning">{evolutionStats.total_mutations}</div>
              </div>
              <Activity className="text-warning" size={24} />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <div className="metric-label">Taux Succès</div>
                <div className="text-2xl font-bold text-success">
                  {(evolutionStats.avg_success_rate * 100).toFixed(1)}%
                </div>
              </div>
              <TrendingUp className="text-success" size={24} />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <div className="metric-label">Mutations Récentes</div>
                <div className="text-2xl font-bold text-blue-400">{evolutionStats.recent_mutations}</div>
              </div>
              <Clock className="text-blue-400" size={24} />
            </div>
          </div>
        </div>
      )}

      {/* Category Filter */}
      <div className="card">
        <div className="card-header">Filtrer par Catégorie</div>
        <div className="card-body">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedCategory === 'all'
                  ? 'bg-primary text-white'
                  : 'bg-card-bg text-text hover:bg-gray-700'
              }`}
            >
              Toutes ({genes.length})
            </button>
            {categories.map(category => {
              const count = genes.filter(g => g.category === category).length
              const IconComponent = getCategoryIcon(category)
              return (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                    selectedCategory === category
                      ? 'bg-primary text-white'
                      : 'bg-card-bg text-text hover:bg-gray-700'
                  }`}
                >
                  <IconComponent size={16} />
                  {category} ({count})
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Genes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredGenes.map((gene) => {
          const IconComponent = getCategoryIcon(gene.category)
          return (
            <div
              key={`${gene.category}_${gene.key}`}
              className="card cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => setSelectedGene(selectedGene?.key === gene.key ? null : gene)}
            >
              <div className="card-header flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${getCategoryColor(gene.category)}`}>
                    <IconComponent size={20} className="text-white" />
                  </div>
                  <div>
                    <div className="font-semibold">{gene.key}</div>
                    <div className="text-xs text-text-muted capitalize">{gene.category}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">{gene.priority}/100</div>
                  <div className="text-xs text-text-muted">Priorité</div>
                </div>
              </div>

              <div className="card-body space-y-3">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-text-muted">Succès</div>
                    <div className="font-medium text-success">
                      {(gene.success_rate * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-text-muted">Utilisations</div>
                    <div className="font-medium">{gene.usage_count}</div>
                  </div>
                  <div>
                    <div className="text-text-muted">Mutations</div>
                    <div className="font-medium text-warning">{gene.mutations}</div>
                  </div>
                  <div>
                    <div className="text-text-muted">Source</div>
                    <div className="font-medium text-xs">{gene.source}</div>
                  </div>
                </div>

                {gene.tags.length > 0 && (
                  <div>
                    <div className="text-text-muted text-sm mb-2">Tags</div>
                    <div className="flex flex-wrap gap-1">
                      {gene.tags.slice(0, 3).map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-primary/20 text-primary text-xs rounded-full flex items-center gap-1"
                        >
                          <Tag size={10} />
                          {tag}
                        </span>
                      ))}
                      {gene.tags.length > 3 && (
                        <span className="text-xs text-text-muted">
                          +{gene.tags.length - 3} autres
                        </span>
                      )}
                    </div>
                  </div>
                )}

                <div className="text-xs text-text-muted">
                  Créé: {new Date(gene.created_at).toLocaleDateString()}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {filteredGenes.length === 0 && (
        <div className="text-center py-12">
          <Dna className="mx-auto text-text-muted mb-4" size={48} />
          <div className="text-text-muted">Aucun gène trouvé</div>
        </div>
      )}

      {/* Gene Detail Modal */}
      {selectedGene && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-dark rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-3 rounded-lg ${getCategoryColor(selectedGene.category)}`}>
                    {React.createElement(getCategoryIcon(selectedGene.category), {
                      size: 24,
                      className: "text-white"
                    })}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">{selectedGene.key}</h3>
                    <p className="text-text-muted capitalize">{selectedGene.category}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedGene(null)}
                  className="text-text-muted hover:text-text"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">{selectedGene.priority}</div>
                  <div className="text-sm text-text-muted">Priorité</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-success">
                    {(selectedGene.success_rate * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-text-muted">Succès</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-400">{selectedGene.usage_count}</div>
                  <div className="text-sm text-text-muted">Utilisations</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-warning">{selectedGene.mutations}</div>
                  <div className="text-sm text-text-muted">Mutations</div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Données du Gène</h4>
                <pre className="bg-card-bg p-4 rounded-lg text-sm overflow-x-auto">
                  {JSON.stringify(selectedGene.data, null, 2)}
                </pre>
              </div>

              {selectedGene.tags.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedGene.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-text-muted">Créé:</span>
                  <span className="ml-2">{new Date(selectedGene.created_at).toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-text-muted">Modifié:</span>
                  <span className="ml-2">{new Date(selectedGene.updated_at).toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-text-muted">Source:</span>
                  <span className="ml-2">{selectedGene.source}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default GenomeVisualizer