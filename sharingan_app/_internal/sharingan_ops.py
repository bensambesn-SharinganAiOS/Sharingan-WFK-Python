#!/usr/bin/env python3
"""
SHARINGAN - OPERATIONS SIMPLES
===============================
Lecture fichiers, pages web, creation fichiers
"""

import os
import urllib.request
from datetime import datetime

class SharinganOps:
    """Operations simples disponibles sans initialisation complete"""
    
    def __init__(self):
        self.name = "Sharingan OS"
        self.version = "4.0"
    
    def lire_fichier(self, chemin):
        """Lire le contenu d'un fichier"""
        try:
            with open(chemin, 'r', encoding='utf-8') as f:
                return {
                    "success": True,
                    "contenu": f.read(),
                    "lignes": len(f.readlines())
                }
        except FileNotFoundError:
            return {"success": False, "erreur": "Fichier non trouve"}
        except Exception as e:
            return {"success": False, "erreur": str(e)}
    
    def creer_fichier(self, chemin, contenu):
        """Creer un fichier avec du contenu"""
        try:
            with open(chemin, 'w', encoding='utf-8') as f:
                f.write(contenu)
            return {
                "success": True,
                "message": f"Fichier cree: {chemin}"
            }
        except Exception as e:
            return {"success": False, "erreur": str(e)}
    
    def lire_page_web(self, url):
        """Lire le contenu d'une page web"""
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                html = response.read(2000).decode('utf-8')
                titre = html.split('<title>')[1].split('</title>')[0] if '<title>' in html else 'Sans titre'
                return {
                    "success": True,
                    "url": url,
                    "titre": titre,
                    "contenu": html[:500]
                }
        except Exception as e:
            return {"success": False, "erreur": str(e)}
    
    def lister_dossier(self, chemin):
        """Lister les fichiers d'un dossier"""
        try:
            fichiers = os.listdir(chemin)
            return {
                "success": True,
                "chemin": chemin,
                "fichiers": fichiers[:20],
                "total": len(fichiers)
            }
        except Exception as e:
            return {"success": False, "erreur": str(e)}
    
    def info_systeme(self):
        """Informations sur le systeme"""
        return {
            "nom": self.name,
            "version": self.version,
            "hostname": open('/etc/hostname').read().strip(),
            "utilisateur": os.getenv('USER', 'inconnu'),
            "repertoire_courant": os.getcwd()
        }


# Instance unique
_ops = None

def get_ops():
    global _ops
    if _ops is None:
        _ops = SharinganOps()
    return _ops


# Interface simple
def lire(chemin):
    """Lire un fichier"""
    return get_ops().lire_fichier(chemin)

def ecrire(chemin, contenu):
    """Creer/modifier un fichier"""
    return get_ops().creer_fichier(chemin, contenu)

def web(url):
    """Lire une page web"""
    return get_ops().lire_page_web(url)

def ls(chemin):
    """Lister un dossier"""
    return get_ops().lister_dossier(chemin)

def info():
    """Informations systeme"""
    return get_ops().info_systeme()


if __name__ == "__main__":
    print("=== SHARINGAN OPERATIONS ===")
    print("")
    
    # Test lecture fichier
    print("1. Lecture fichier:")
    r = lire('/etc/hostname')
    print(f"   Hostname: {r.get('contenu', 'N/A').strip()}")
    
    # Test creation fichier
    print("\n2. Creation fichier:")
    r = ecrire('/tmp/sharingantest.txt', f"Test - {datetime.now()}\n")
    print(f"   {r.get('message')}")
    
    # Test page web
    print("\n3. Page web:")
    r = web('https://example.com')
    print(f"   Titre: {r.get('titre')}")
    print(f"   URL: {r.get('url')}")
    
    # Info systeme
    print("\n4. Systeme:")
    i = info()
    print(f"   Nom: {i.get('nom')} {i.get('version')}")
    print(f"   Host: {i.get('hostname')}")
    print(f"   User: {i.get('utilisateur')}")
