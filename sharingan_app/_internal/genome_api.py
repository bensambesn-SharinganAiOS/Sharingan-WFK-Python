# -*- coding: utf-8 -*-
"""Sharingan OS - Genome Memory API Routes"""

#!/usr/bin/env python3

import logging
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify

# Get internal directory
_internal_dir = Path(__file__).parent
sys.path.insert(0, str(_internal_dir))

get_genome_memory = None
try:
    from genome_memory import get_genome_memory
    GENOME_AVAILABLE = True
except ImportError:
    GENOME_AVAILABLE = False

logger = logging.getLogger("genome_api")

# Create blueprint for genome APIs
genome_bp = Blueprint('genome', __name__, url_prefix='/api/genome')

@genome_bp.route('/genes', methods=['GET'])
def api_genome_genes():
    """Get all genome genes"""
    try:
        if not GENOME_AVAILABLE:
            return jsonify({"error": "Genome memory not available"}), 503

        genome = get_genome_memory()
        if hasattr(genome, 'genes'):
            genes = []
            for gene_key, gene in genome.genes.items():
                genes.append({
                    'key': gene.key,
                    'category': gene.category,
                    'priority': gene.priority,
                    'created_at': gene.created_at,
                    'updated_at': gene.updated_at,
                    'success_rate': gene.success_rate,
                    'usage_count': gene.usage_count,
                    'mutations': gene.mutations,
                    'tags': gene.tags,
                    'source': gene.source
                })
            return jsonify({'genes': genes, 'total': len(genes)})
        else:
            return jsonify({'genes': [], 'total': 0})
    except Exception as e:
        logger.error(f"Genome genes API error: {e}")
        return jsonify({"error": str(e)}), 500

@genome_bp.route('/genes/<gene_key>', methods=['GET'])
def api_genome_gene_detail(gene_key):
    """Get specific gene details"""
    try:
        if not GENOME_AVAILABLE:
            return jsonify({"error": "Genome memory not available"}), 503

        genome = get_genome_memory()
        if hasattr(genome, 'genes') and gene_key in genome.genes:
            gene = genome.genes[gene_key]
            return jsonify({
                'key': gene.key,
                'data': gene.data,
                'category': gene.category,
                'priority': gene.priority,
                'created_at': gene.created_at,
                'updated_at': gene.updated_at,
                'success_rate': gene.success_rate,
                'usage_count': gene.usage_count,
                'mutations': gene.mutations,
                'tags': gene.tags,
                'source': gene.source
            })
        else:
            return jsonify({"error": "Gene not found"}), 404
    except Exception as e:
        logger.error(f"Genome gene detail API error: {e}")
        return jsonify({"error": str(e)}), 500

@genome_bp.route('/genes', methods=['POST'])
def api_genome_create_gene():
    """Create new gene"""
    try:
        if not GENOME_AVAILABLE:
            return jsonify({"error": "Genome memory not available"}), 503

        data = request.get_json()
        if not data or 'key' not in data:
            return jsonify({"error": "Missing gene key"}), 400

        genome = get_genome_memory()
        gene_data = {
            'key': data['key'],
            'data': data.get('data', {}),
            'category': data.get('category', 'feature'),
            'priority': data.get('priority', 50),
            'tags': data.get('tags', []),
            'source': data.get('source', 'api')
        }

        # Store gene directly in genes dict
        if hasattr(genome, 'genes'):
            from genome_memory import Gene
            gene_key = f"{gene_data['category']}_{gene_data['key']}"
            new_gene = Gene(
                key=gene_data['key'],
                data=gene_data['data'],
                category=gene_data['category'],
                priority=gene_data['priority'],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tags=gene_data['tags'],
                source=gene_data['source']
            )
            genome.genes[gene_key] = new_gene
            genome._save_genome()
            return jsonify({"message": "Gene created", "gene": gene_data}), 201
        else:
            return jsonify({"error": "Genome storage not available"}), 500

    except Exception as e:
        logger.error(f"Genome create gene API error: {e}")
        return jsonify({"error": str(e)}), 500

@genome_bp.route('/mutations', methods=['GET'])
def api_genome_mutations():
    """Get mutation history"""
    try:
        if not GENOME_AVAILABLE:
            return jsonify({"error": "Genome memory not available"}), 503

        genome = get_genome_memory()
        if hasattr(genome, 'mutations'):
            mutations = []
            for mutation in genome.mutations[-50:]:  # Last 50 mutations
                mutations.append({
                    'gene_key': mutation.gene_key,
                    'old_value': str(mutation.old_value)[:100],  # Truncate for API
                    'new_value': str(mutation.new_value)[:100],
                    'reason': mutation.reason,
                    'timestamp': mutation.timestamp,
                    'validated': mutation.validated
                })
            return jsonify({'mutations': mutations, 'total': len(genome.mutations)})
        else:
            return jsonify({'mutations': [], 'total': 0})
    except Exception as e:
        logger.error(f"Genome mutations API error: {e}")
        return jsonify({"error": str(e)}), 500

@genome_bp.route('/evolution', methods=['GET'])
def api_genome_evolution():
    """Get evolution statistics"""
    try:
        if not GENOME_AVAILABLE:
            return jsonify({"error": "Genome memory not available"}), 503

        genome = get_genome_memory()
        evolution_stats = {
            'total_genes': len(getattr(genome, 'genes', {})),
            'total_mutations': len(getattr(genome, 'mutations', [])),
            'categories': {},
            'avg_success_rate': 0.0,
            'most_used_gene': None,
            'recent_mutations': 0
        }

        # Category breakdown
        if hasattr(genome, 'genes'):
            for gene in genome.genes.values():
                cat = gene.category
                if cat not in evolution_stats['categories']:
                    evolution_stats['categories'][cat] = 0
                evolution_stats['categories'][cat] += 1

        # Average success rate
        if hasattr(genome, 'genes') and genome.genes:
            total_rate = sum(gene.success_rate for gene in genome.genes.values())
            evolution_stats['avg_success_rate'] = total_rate / len(genome.genes)

        # Most used gene
        if hasattr(genome, 'genes') and genome.genes:
            most_used = max(genome.genes.values(), key=lambda g: g.usage_count)
            evolution_stats['most_used_gene'] = {
                'key': most_used.key,
                'usage_count': most_used.usage_count,
                'category': most_used.category
            }

        # Recent mutations (last 24h)
        if hasattr(genome, 'mutations'):
            recent_cutoff = time.time() - (24 * 60 * 60)  # 24 hours ago
            recent = [m for m in genome.mutations if isinstance(m.timestamp, str) and m.timestamp]
            evolution_stats['recent_mutations'] = len(recent)

        return jsonify(evolution_stats)

    except Exception as e:
        logger.error(f"Genome evolution API error: {e}")
        return jsonify({"error": str(e)}), 500

# Function to register blueprint
def register_genome_apis(app):
    """Register genome API blueprint with Flask app"""
    app.register_blueprint(genome_bp)
    logger.info("[GENOME API] Genome APIs registered")

if __name__ == "__main__":
    print("[GENOME API] Genome Memory API Routes")
    print("=" * 50)
    print("Routes disponibles :")
    print("GET  /api/genome/genes        - Liste des gènes")
    print("GET  /api/genome/genes/<key>  - Détails d'un gène")
    print("POST /api/genome/genes        - Créer un gène")
    print("GET  /api/genome/mutations    - Historique mutations")
    print("GET  /api/genome/evolution    - Statistiques évolution")