#!/usr/bin/env python3
"""
Genome Memory Initialization Script
Initialise le système Genome Memory avec des gènes et instincts de base
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire au path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from genome_memory import GenomeMemory

def initialize_genome_memory():
    """Initialise le Genome Memory avec des gènes et instincts essentiels"""

    print("🧬 INITIALISATION DU GENOME MEMORY")
    print("=" * 50)

    genome = GenomeMemory()

    # === GÈNES CORE (Priorité 100) ===
    print("\n📝 Création des gènes CORE...")

    genome.mutate("system_capabilities", {
        "ai_providers": ["tgpt", "MiniMax", "GLM-4", "OpenRouter"],
        "tools_count": 112,
        "kali_categories": ["network", "web", "password", "wireless", "forensic", "social"],
        "memory_systems": ["genome", "ai_memory", "context", "vector"],
        "autonomy_level": "high"
    }, "core", source="system_init", tags=["system", "capabilities", "ai", "tools"])

    genome.mutate("sharingan_identity", {
        "name": "Sharingan OS",
        "purpose": "AI-powered cybersecurity operating system",
        "inspiration": ["AutoGPT", "Kali Linux", "Metasploit"],
        "author": "Ben Sambe",
        "version": "3.0.0"
    }, "core", source="system_init", tags=["identity", "purpose", "version"])

    # === GÈNES SECURITY (Priorité 95) ===
    print("🔒 Création des gènes SECURITY...")

    genome.mutate("security_defaults", {
        "common_passwords": ["admin", "password", "123456", "root", "user"],
        "default_credentials": ["admin:admin", "root:root", "user:password"],
        "dangerous_ports": [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995],
        "common_vulnerabilities": ["SQL injection", "XSS", "CSRF", "buffer overflow"]
    }, "security", source="security_init", tags=["passwords", "credentials", "ports", "vulnerabilities"])

    genome.mutate("network_basics", {
        "port_ranges": {
            "well_known": "0-1023",
            "registered": "1024-49151",
            "dynamic": "49152-65535"
        },
        "common_services": {
            22: "SSH", 80: "HTTP", 443: "HTTPS", 53: "DNS",
            25: "SMTP", 110: "POP3", 143: "IMAP", 993: "IMAPS"
        }
    }, "security", source="network_init", tags=["network", "ports", "services"])

    # === GÈNES PERFORMANCE (Priorité 90) ===
    print("⚡ Création des gènes PERFORMANCE...")

    genome.mutate("memory_optimization", {
        "context_max_tokens": 100000,
        "auto_compact_threshold": 0.9,
        "memory_cleanup_interval": 3600,
        "priority_levels": ["CRITICAL", "HIGH", "MEDIUM", "LOW", "TEMPORARY"]
    }, "performance", source="performance_init", tags=["memory", "optimization", "context"])

    # === GÈNES FEATURE (Priorité 70) ===
    print("🛠️ Création des gènes FEATURE...")

    genome.mutate("tool_integration", {
        "nmap_scanning": True,
        "sqlmap_testing": True,
        "hashcat_cracking": True,
        "metasploit_exploitation": True,
        "volatility_forensics": True
    }, "feature", source="tools_init", tags=["tools", "integration", "kali"])

    genome.mutate("ai_autonomy", {
        "independent_responses": True,
        "fake_detection": True,
        "context_management": True,
        "learning_system": True,
        "multi_agent_support": True
    }, "feature", source="ai_init", tags=["ai", "autonomy", "learning"])

    # === INSTINCTS DE BASE ===
    print("\n🎯 Création des instincts de base...")

    instincts = [
        ("bonjour", "Bonjour ! Je suis Sharingan OS, un système d'exploitation IA pour la cybersécurité.", "greeting"),
        ("salut", "Salut ! Sharingan OS à votre service pour la cybersécurité.", "greeting"),
        ("hello", "Hello! I'm Sharingan OS, an AI-powered cybersecurity system.", "greeting"),
        ("aide", "Je peux vous aider avec : scans réseau, tests de sécurité, analyse de vulnérabilités, exploitation d'outils Kali Linux, et apprentissage continu.", "help"),
        ("help", "I can help you with: network scanning, security testing, vulnerability analysis, Kali Linux tools, and continuous learning.", "help"),
        ("status", "Système opérationnel avec 112 outils Kali intégrés, IA autonome et système Genome Memory actif.", "status"),
        ("qui es tu", "Je suis Sharingan OS, un système d'exploitation IA inspiré d'AutoGPT, Kali Linux et Metasploit.", "identity"),
        ("what are you", "I am Sharingan OS, an AI-powered cybersecurity operating system combining autonomous AI with 112 security tools.", "identity"),
        ("merci", "De rien ! N'hésitez pas si vous avez besoin d'aide en cybersécurité.", "gratitude"),
        ("thanks", "You're welcome! Let me know if you need cybersecurity assistance.", "gratitude")
    ]

    for pattern, response, condition in instincts:
        genome.add_instinct(pattern, response, condition)

    # Enregistrer quelques succès initiaux
    print("\n✅ Enregistrement des succès initiaux...")
    genes_keys = list(genome.genes.keys())
    for key in genes_keys[:3]:  # Marquer les 3 premiers comme réussis
        genome.record_success(key)

    # Statistiques finales
    stats = genome.get_statistics()
    print("\n" + "=" * 50)
    print("🎉 INITIALISATION TERMINÉE")
    print("=" * 50)
    print(f"📊 Gènes créés: {stats['total_genes']}")
    print(f"🎯 Instincts configurés: {stats['total_instincts']}")
    print(f"🔄 Mutations: {stats['total_mutations']}")

    print("\n📂 Répartition par catégorie:")
    for cat, data in stats['by_category'].items():
        print(f"  {cat}: {data['count']} gènes")

    print("\n🏆 Top gènes:")
    for gene_key in stats['top_genes'][:3]:
        gene = genome.genes.get(gene_key)
        if gene:
            print(f"  {gene_key}: priorité {gene.priority}, succès {gene.success_rate:.2f}")

    print("\n🧬 Genome Memory opérationnel !")

    return genome

if __name__ == "__main__":
    try:
        initialize_genome_memory()
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()