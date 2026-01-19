#!/usr/bin/env python3
"""
DNA Backup System - Complete System Snapshot
Sauvegarde complète de l'état du système pour préserver le projet.
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

_internal_dir = Path(__file__).parent
sys.path.insert(0, str(_internal_dir))


class DNABackupSystem:
    """
    Système de sauvegarde ADN complet.
    
    Fonctionnalités:
    - Snapshot complet du système (code, structure, genome, consciousness)
    - Archivage automatique dans DNA_EVOLUTIONS_DOCUMENTATION
    - Historique des évolutions
    - Restoration possible
    """
    
    def __init__(self):
        self.data_dir = _internal_dir / "data"
        self.dna_dir = self.data_dir / "DNA_EVOLUTIONS_DOCUMENTATION"
        self.dna_dir.mkdir(exist_ok=True)
        
        self.main_dna_file = self.data_dir / "SYSTEM_DNA_FULL.json"
        self.backup_counter = 0
    
    def generate_snapshot(self) -> Dict[str, Any]:
        """Génère un snapshot complet du système"""
        
        snapshot = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "3.0.0",
                "type": "full_snapshot"
            },
            "system_info": self._get_system_info(),
            "genome_state": self._get_genome_state(),
            "consciousness_state": self._get_consciousness_state(),
            "tools_state": self._get_tools_state(),
            "project_structure": self._get_project_structure(),
            "key_files_content": self._get_key_files_content(),
            "algorithms_summary": self._get_algorithms_summary()
        }
        
        return snapshot
    
    def _get_system_info(self) -> Dict:
        """Informations système de base"""
        return {
            "name": "Sharingan OS",
            "purpose": "AI-Powered Cybersecurity Operating System",
            "creator": "Ben Sambe",
            "components": [
                "Genome Memory",
                "System Consciousness",
                "112+ Tools",
                "AI Providers (tgpt, MiniMax, GLM-4)",
                "Instinct Layer",
                "Context Manager"
            ]
        }
    
    def _get_genome_state(self) -> Dict:
        """État actuel du genome (simplifié car le full DNA contient tout)"""
        try:
            from genome_memory import get_genome_memory
            genome = get_genome_memory()
            stats = genome.get_statistics()
            return {
                "total_genes": stats['total_genes'],
                "total_mutations": stats['total_mutations'],
                "total_instincts": stats['total_instincts'],
                "categories": stats.get('by_category', {}),
                "note": "Full DNA contains complete genome data in key_files_content"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_consciousness_state(self) -> Dict:
        """État de la conscience"""
        try:
            from system_consciousness import SystemConsciousness
            consciousness = SystemConsciousness(connect_memory=False)
            return {
                "identity": consciousness.agent_identity,
                "capabilities": consciousness.capabilities,
                "permissions": consciousness.permissions,
                "modes": ["build", "plan"]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_tools_state(self) -> Dict:
        """État des outils"""
        tools_dir = _internal_dir / "tools" / "official"
        if tools_dir.exists():
            tools = [d.name for d in tools_dir.iterdir() if d.is_dir()]
            return {
                "total_tools": len(tools),
                "tools_list": sorted(tools)[:20],  # Preview
                "note": "Full tool list in project_structure"
            }
        return {"total_tools": 0}
    
    def _get_project_structure(self) -> Dict:
        """Structure complète du projet"""
        structure = {
            "root": "/root/Projets/Sharingan-WFK-Python",
            "main_app": "sharingan_app/_internal",
            "subdirectories": []
        }
        
        for item in Path(_internal_dir).iterdir():
            if item.is_dir() and not item.name.startswith("__pycache__"):
                structure["subdirectories"].append(item.name)
        
        return structure
    
    def _get_key_files_content(self) -> Dict[str, str]:
        """Contenu des fichiers clés (POUR NE PAS PERDRE LE CODE)"""
        key_files = [
            "main.py",
            "system_consciousness.py",
            "genome_memory.py",
            "instinct_layer.py",
            "context_manager.py",
            "ai_providers.py",
            "tool_registry.py",
            "clarification_layer.py",
            "ai_memory_manager.py"
        ]
        
        content = {}
        for filename in key_files:
            filepath = _internal_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r') as f:
                        content[filename] = f.read()
                except Exception:
                    pass
        
        return content
    
    def _get_algorithms_summary(self) -> Dict[str, str]:
        """Résumé des algorithmes clés"""
        return {
            "genome_memory": """
            Le Genome Memory est un système d'apprentissage ADN-like:
            - Gènes: connaissances accumulées avec priorités
            - Mutations: évolutions des gènes
            - Instincts: réponses automatiques basées sur patterns
            - Évolution: élimine les gènes faibles
            """,
            "consciousness": """
            System Consciousness assure la conscience du système:
            - Analyse des intentions utilisateur
            - Vérification des permissions
            - Gestion du mode build/plan
            - Détection de l'environnement
            """,
            "instinct_layer": """
            Nouvelle couche additive qui vérifie les instincts:
            - Pattern matching avec le genome
            - Prévention des échecs connus
            - Réponses automatiques si match
            """,
            "tool_execution": """
            Système d'exécution d'outils avec:
            - Registry unifié de 112+ outils
            - Validation avant exécution
            - Tracking des succès/échecs
            """
        }
    
    def save_dna(self, reason: str = "manual") -> str:
        """Sauvegarde le DNA complet"""
        snapshot = self.generate_snapshot()
        
        # Sauvegarder le fichier principal
        with open(self.main_dna_file, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        # Créer une copie horodatée
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checksum = hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()[:8]
        backup_filename = f"DNA_{timestamp}_{checksum}.json"
        backup_path = self.dna_dir / backup_filename
        
        with open(backup_path, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        # Créer un lien vers la dernière version
        latest_link = self.dna_dir / "LATEST.json"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(backup_path)
        
        self.backup_counter += 1
        
        return str(backup_path)
    
    def load_dna(self) -> Dict:
        """Charge le DNA complet"""
        if self.main_dna_file.exists():
            with open(self.main_dna_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_evolution_history(self) -> List[Dict]:
        """Retourne l'historique des évolutions"""
        history = []
        for f in sorted(self.dna_dir.glob("DNA_*.json")):
            if f.name != "LATEST.json":
                try:
                    with open(f, 'r') as file:
                        data = json.load(file)
                        history.append({
                            "file": f.name,
                            "timestamp": data.get("metadata", {}).get("timestamp"),
                            "genes": data.get("genome_state", {}).get("total_genes", 0),
                            "tools": data.get("tools_state", {}).get("total_tools", 0)
                        })
                except Exception:
                    pass
        return history


def get_dna_backup_system() -> DNABackupSystem:
    return DNABackupSystem()


def create_dna_backup(reason: str = "manual") -> str:
    """Fonction utilitaire simple"""
    dna = get_dna_backup_system()
    return dna.save_dna(reason)


if __name__ == "__main__":
    print("=== DNA BACKUP SYSTEM ===\n")
    
    dna = get_dna_backup_system()
    
    print("1. Generating full snapshot...")
    snapshot = dna.generate_snapshot()
    print(f"   System: {snapshot['system_info']['name']}")
    print(f"   Files captured: {len(snapshot['key_files_content'])}")
    print(f"   Algorithms: {len(snapshot['algorithms_summary'])}")
    
    print("\n2. Saving DNA...")
    backup_path = dna.save_dna("test_backup")
    print(f"   Saved to: {backup_path}")
    
    print("\n3. Evolution history:")
    history = dna.get_evolution_history()
    for h in history:
        print(f"   - {h['file']}: {h.get('genes', 0)} genes, {h.get('tools', 0)} tools")
    
    print("\n✓ DNA Backup System operational!")
    print(f"\nMain DNA file: {dna.main_dna_file}")
    print(f"Evolution directory: {dna.dna_dir}")
