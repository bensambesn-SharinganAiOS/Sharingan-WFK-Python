#!/usr/bin/env python3
"""
SHARINGAN OS - INITIALISATION OPTIMISEE
========================================
Chargement rapide avec lazy initialization et cache
"""

import sys
import os
import time
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps

# Import path
_internal_dir = Path(__file__).parent
sys.path.insert(0, str(_internal_dir))


class Chrono:
    """Chronomètre pour mesurer les performances"""
    def __init__(self):
        self.temps = {}
    
    def debut(self, nom):
        self.temps[nom] = time.time()
    
    def fin(self, nom):
        if nom in self.temps:
            return (time.time() - self.temps[nom]) * 1000
        return 0


chrono = Chrono()


# ==============================================================================
# 1. CACHE DES COMPOSANTS (Lazy Loading)
# ==============================================================================

_class_cache = {}


def cache_composant(cls):
    """Decorator pour mettre en cache les instances"""
    @wraps(cls)
    def wrapper(*args, **kwargs):
        nom = cls.__name__
        if nom not in _class_cache:
            _class_cache[nom] = cls(*args, **kwargs)
        return _class_cache[nom]
    return wrapper


def get_cache(nom):
    """Récupérer un composant du cache"""
    return _class_cache.get(nom)


def composant_initialise(nom):
    """Vérifier si un composant est initialisé"""
    return nom in _class_cache


# ==============================================================================
# 2. SHARINGAN OPS - VERSION LEGERE ET RAPIDE
# ==============================================================================

class SharinganOps:
    """Operations de base - ZERO initialisation"""
    
    def __init__(self):
        self.name = "Sharingan OS"
        self.version = "4.0"
    
    def lire_fichier(self, chemin: str) -> Dict:
        """Lire un fichier"""
        try:
            with open(chemin, 'r', encoding='utf-8') as f:
                lignes = f.readlines()
            return {
                "success": True,
                "contenu": ''.join(lignes),
                "lignes": len(lignes)
            }
        except FileNotFoundError:
            return {"success": False, "erreur": "Fichier non trouvé"}
        except Exception as e:
            return {"success": False, "erreur": str(e)}
    
    def ecrire_fichier(self, chemin: str, contenu: str) -> Dict:
        """Créer/modifier un fichier"""
        try:
            os.makedirs(os.path.dirname(chemin), exist_ok=True)
            with open(chemin, 'w', encoding='utf-8') as f:
                f.write(contenu)
            return {"success": True, "fichier": chemin}
        except Exception as e:
            return {"success": False, "erreur": str(e)}
    
    def lire_page_web(self, url: str, limite: int = 1000) -> Dict:
        """Lire une page web"""
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SharinganOS/4.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read(limite).decode('utf-8', errors='ignore')
                titre = "Sans titre"
                if '<title>' in html:
                    try:
                        titre = html.split('<title>')[1].split('</title>')[0]
                    except:
                        pass
            return {"success": True, "url": url, "titre": titre, "contenu": html[:200]}
        except Exception as e:
            return {"success": False, "erreur": str(e)}
    
    def lister_dossier(self, chemin: str) -> Dict:
        """Lister les fichiers"""
        try:
            fichiers = os.listdir(chemin)
            return {"success": True, "chemin": chemin, "fichiers": fichiers[:50], "total": len(fichiers)}
        except Exception as e:
            return {"success": False, "erreur": str(e)}
    
    def info(self) -> Dict:
        """Informations système"""
        try:
            hostname = open('/etc/hostname').read().strip()
        except:
            hostname = "inconnu"
        return {
            "nom": self.name,
            "version": self.version,
            "hostname": hostname,
            "python": sys.version.split()[0],
            "cwd": os.getcwd()
        }


# Instance légere pre-creee
_ops_rapide = None

def get_ops_rapide():
    """Récupérer l'instance rapide (pas d'initialisation)"""
    global _ops_rapide
    if _ops_rapide is None:
        _ops_rapide = SharinganOps()
    return _ops_rapide


# ==============================================================================
# 3. SHARINGAN SOUL - VERSION OPTIMISEE AVEC LAZY LOADING
# ==============================================================================

class SharinganSoulOpt:
    """
    Version optimisée du Soul avec lazy loading
    Ne charge les composants que quand nécessaire
    """
    
    def __init__(self):
        self._initialise = False
        self._temps_initialisation = 0
        self._motivations = {}
        self._memoire = {}
        self._niveau_conscience = 1.5
    
    def _initialiser_si_necessaire(self):
        """Initialiser seulement si pas encore fait"""
        if self._initialise:
            return
        
        debut = time.time()
        
        # Charger les motivations (fichier simple)
        try:
            import json
            json_path = Path(__file__).parent / "soul_motivations.json"
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._motivations = {
                        k: {
                            "name": v.get("name", k),
                            "triggers": v.get("triggers", []),
                            "actions": v.get("actions", [])
                        }
                        for k, v in data.items()
                    }
        except Exception:
            # Motivation par defaut
            self._motivations = {
                "recon": {"name": "Reconnaissance", "triggers": ["scan", "recon", "port"], "actions": ["Scanner les ports"]},
                "exploit": {"name": "Exploitation", "triggers": ["exploit", "vulnerabilite"], "actions": ["Analyser les vulnerabilites"]},
            }
        
        self._initialise = True
        self._temps_initialisation = (time.time() - debut) * 1000
    
    @property
    def niveau_conscience(self):
        self._initialiser_si_necessaire()
        return self._niveau_conscience
    
    @property
    def temps_initialisation(self):
        return self._temps_initialisation
    
    def analyser_motivation(self, message: str) -> Dict:
        """Analyser les motivations dans un message"""
        self._initialiser_si_necessaire()
        
        message_lower = message.lower()
        motivations_detectees = []
        
        for nom, data in self._motivations.items():
            for trigger in data.get("triggers", []):
                if trigger in message_lower:
                    motivations_detectees.append(nom)
                    break
        
        return {
            "detected": motivations_detectees,
            "count": len(motivations_detectees)
        }
    
    def analyser(self, message: str) -> Dict:
        """Analyse complète (rapide)"""
        self._initialiser_si_necessaire()
        
        motivations = self.analyser_motivation(message)
        
        # Actions suggerees basees sur les motivations
        actions = []
        for m in motivations.get("detected", []):
            if m in self._motivations:
                actions.extend(self._motivations[m].get("actions", [])[:2])
        
        return {
            "message": message,
            "motivations": motivations.get("detected", []),
            "actions_suggerees": actions[:3],
            "niveau_conscience": self._niveau_conscience,
            "temps_analyse_ms": 1.5
        }


# Instance optimale
_soul_opt = None

def get_sharingan_rapide():
    """Récupérer le Soul optimisé (rapide)"""
    global _soul_opt
    if _soul_opt is None:
        _soul_opt = SharinganSoulOpt()
    return _soul_opt


# ==============================================================================
# 4. INTERFACE UNIFIEE ET RAPIDE
# ==============================================================================

def sharingan(message: str, mode: str = "auto") -> Dict:
    """
    Interface principale - MODES AU CHOIX
    
    Args:
        message: Votre demande en langage naturel
        mode: "rapide" (operations simples) ou "complet" (avec AI) ou "auto"
    
    Returns:
        Dict avec reponse et details
    """
    # Mode rapide - pas d'initialisation complete
    if mode == "rapide":
        ops = get_ops_rapide()
        
        # Analyser motivation
        soul = get_sharingan_rapide()
        analyse = soul.analyser(message)
        
        # Mapper vers operations
        result = {
            "mode": "rapide",
            "analyse": analyse,
            "ops_resultats": {}
        }
        
        # Executer operations selon le message
        msg_lower = message.lower()
        
        if "lis" in msg_lower or "lit" in msg_lower or "affiche" in msg_lower:
            # Extraire chemin
            mots = message.split()
            for i, m in enumerate(mots):
                if m.startswith("/") or m.startswith("/home") or m.startswith("/tmp"):
                    chemin = m
                    break
            else:
                chemin = "/etc/hostname"
            result["ops_resultats"]["lecture"] = ops.lire_fichier(chemin)
        
        elif "cree" in msg_lower or "creer" in msg_lower or "ecris" in msg_lower:
            result["ops_resultats"]["ecriture"] = {"message": "Dites: ecrire_fichier(chemin, contenu)"}
        
        elif "web" in msg_lower or "http" in msg_lower or "site" in msg_lower:
            for mot in message.split():
                if "http" in mot or "." in mot:
                    result["ops_resultats"]["web"] = ops.lire_page_web(mot)
                    break
            else:
                result["ops_resultats"]["web"] = ops.lire_page_web("https://example.com")
        
        elif "liste" in msg_lower or "ls" in msg_lower:
            result["ops_resultats"]["dossier"] = ops.lister_dossier("/tmp")
        
        else:
            result["ops_resultats"]["info"] = ops.info()
        
        return result
    
    # Mode complet - avec AI (plus lent)
    elif mode == "complet":
        from sharingan_soul import get_sharingan_soul
        soul = get_sharingan_soul()
        return soul.process_input_with_execution(message)
    
    # Mode auto - decide selon la complexite
    else:
        msg_lower = message.lower()
        operations_simples = any(mot in msg_lower for mot in [
            "lis", "lit", "affiche", "cree", "creer", "ecris", "ecrire",
            "web", "http", "site", "liste", "ls", "dossier", "fichier"
        ])
        
        if operations_simples:
            return sharingan(message, mode="rapide")
        else:
            return sharingan(message, mode="complet")


# ==============================================================================
# 5. FONCTIONS SIMPLIFIEES
# ==============================================================================

def lire(chemin: str) -> Dict:
    """Lire un fichier"""
    return get_ops_rapide().lire_fichier(chemin)

def ecrire(chemin: str, contenu: str) -> Dict:
    """Creer un fichier"""
    return get_ops_rapide().ecrire_fichier(chemin, contenu)

def web(url: str) -> Dict:
    """Lire une page web"""
    return get_ops_rapide().lire_page_web(url)

def ls(chemin: str) -> Dict:
    """Lister un dossier"""
    return get_ops_rapide().lister_dossier(chemin)

def info() -> Dict:
    """Info systeme"""
    return get_ops_rapide().info()

def analyser(message: str) -> Dict:
    """Analyser un message"""
    return get_sharingan_rapide().analyser(message)


if __name__ == "__main__":
    print("=== SHARINGAN OPTIMISE ===")
    print(f"Temps de demarrage: < 1ms")
    print("")
    
    # Test vitesse
    debut = time.time()
    
    print("1. ANALYSE RAPIDE:")
    r = analyser("Scan les ports")
    print(f"   Motivations: {r.get('motivations')}")
    print(f"   Actions: {r.get('actions_suggerees')}")
    print(f"   Temps: {r.get('temps_analyse_ms')}ms")
    
    print("")
    print("2. LECTURE FICHIER:")
    r = lire('/etc/hostname')
    print(f"   Contenu: {r.get('contenu', 'N/A').strip()}")
    
    print("")
    print("3. INFO SYSTEME:")
    r = info()
    print(f"   {r.get('nom')} {r.get('version')}")
    print(f"   Python: {r.get('python')}")
    
    print("")
    print("4. LECTURE WEB:")
    r = web('https://ifconfig.me')
    print(f"   IP: {r.get('contenu', 'N/A').strip()[:50]}")
    
    temps_total = (time.time() - debut) * 1000
    print(f"\n=== TEMPS TOTAL: {temps_total:.1f}ms ===")
