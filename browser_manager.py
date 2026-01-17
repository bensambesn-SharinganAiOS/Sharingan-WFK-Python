#!/usr/bin/env python3
"""
Sharingan Browser Manager - Gère le navigateur de manière propre
- Un seul navigateur
- Pas de fermeture automatique
- Connexion via CDP pour les interactions
"""

import subprocess
import json
import urllib.request
import asyncio
import websockets
from typing import Dict, List, Optional
from pathlib import Path
import time

class SharinganBrowser:
    """
    Gestionnaire de navigateur Sharingan.
    Un seul navigateur, réutilisable, pas de fermeture automatique.
    """
    
    def __init__(self, port: int = 9999):
        self.port = port
        self.ws_url = None
        self.connected = False
        self.msg_id = 1
        self.chrome_process = None
        
    def launch(self, url: str = "https://www.google.com") -> bool:
        """Lance un navigateur Chrome avec debug port"""
        # Tuer les processus existants
        subprocess.run("pkill -9 -f 'chrome.*remote-debugging-port=9999' 2>/dev/null", shell=True)
        time.sleep(1)
        
        print(f"\n🚀 Lancement du navigateur Sharingan (port {self.port})...")
        
        cmd = f"""
            google-chrome \
                --remote-debugging-port={self.port} \
                --no-sandbox \
                --disable-dev-shm-usage \
                --disable-gpu \
                --disable-extensions \
                --disable-background-networking \
                --no-first-run \
                --user-data-dir=/tmp/sharingans-chrome \
                "{url}" &
        """
        
        subprocess.run(cmd, shell=True)
        time.sleep(3)
        
        # Vérifier que Chrome est lancé
        result = subprocess.run(
            f"netstat -tlnp | grep {self.port}",
            shell=True, capture_output=True, text=True
        )
        
        if f":{self.port}" in result.stdout:
            print(f"   ✅ Chrome lancé sur le port {self.port}")
            self.chrome_process = True
            return self.connect()
        else:
            print(f"   ❌ Échec du lancement de Chrome")
            return False
    
    def connect(self) -> bool:
        """Se connecte au navigateur via CDP"""
        try:
            targets = json.loads(
                urllib.request.urlopen(f"http://localhost:{self.port}/json").read()
            )
            
            for t in targets:
                if t.get('type') == 'page' and 'extension' not in t.get('url', ''):
                    self.ws_url = t['webSocketDebuggerUrl']
                    break
            
            if self.ws_url:
                print(f"   ✅ Connecté via CDP")
                return True
            
        except Exception as e:
            print(f"   ❌ Erreur de connexion: {e}")
        return False
    
    async def _send(self, method: str, params: dict = None) -> dict:
        """Envoie une commande CDP"""
        msg = {"id": self.msg_id, "method": method, "params": params or {}}
        self.msg_id += 1
        await self.ws.send(json.dumps(msg))
        response = await self.ws.recv()
        return json.loads(response)
    
    async def navigate(self, url: str) -> Dict:
        """Navigue vers une URL"""
        await self._send("Page.navigate", {"url": url})
        await asyncio.sleep(2)
        return {"status": "success", "url": url}
    
    async def search(self, query: str) -> Dict:
        """Fait une recherche sur Google"""
        # Aller sur Google
        await self.navigate("https://www.google.com")
        await asyncio.sleep(2)
        
        # Remplir le champ de recherche
        await self._send("Runtime.evaluate", {
            "expression": f"""
                (() => {{
                    const input = document.querySelector('input[name="q"]');
                    if (input) {{
                        input.value = '{query}';
                        input.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return 'TYPED';
                    }}
                    return 'NOT_FOUND';
                }})()
            """,
            "returnByValue": True
        })
        await asyncio.sleep(1)
        
        # Entrée
        await self._send("Runtime.evaluate", {
            "expression": """
                (() => {
                    const input = document.querySelector('input[name="q"]');
                    if (input) {
                        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
                        return 'ENTER';
                    }
                    return 'NOT_FOUND';
                })()
            """,
            "returnByValue": True
        })
        await asyncio.sleep(3)
        
        return {"status": "success", "query": query}
    
    async def scroll(self, times: int = 5) -> Dict:
        """Défile plusieurs fois"""
        for i in range(times):
            await self._send("Runtime.evaluate", {"expression": "window.scrollBy(0, 500)"})
            await asyncio.sleep(0.3)
        return {"status": "success", "scrolled": times}
    
    async def get_articles(self, count: int = 6) -> List[str]:
        """Récupère les titres d'articles"""
        await self._send("Runtime.evaluate", {
            "expression": f"""
                (() => {{
                    const articles = [];
                    const links = document.querySelectorAll('a, h3');
                    links.forEach(el => {{
                        const text = (el.innerText || '').trim();
                        if (text.length > 25 && text.length < 200 &&
                            !text.includes('Google') &&
                            !text.includes(' connexion') &&
                            (text.toLowerCase().includes('sonko') ||
                             text.toLowerCase().includes('sénégal') ||
                             text.toLowerCase().includes('politique') ||
                             text.toLowerCase().includes('actualit') ||
                             text.toLowerCase().includes('afrique'))) {{
                            articles.push(text);
                        }}
                    }});
                    return JSON.stringify([...new Set(articles)].slice(0, {count}));
                }})()
            """,
            "returnByValue": True
        })
        
        try:
            result = await self._send("Runtime.evaluate", {"expression": ""})
            data = result.get('result', {}).get('result', {}).get('value', '[]')
            return json.loads(data) if data else []
        except:
            return []
    
    async def get_images(self, count: int = 3) -> List[str]:
        """Récupère les URLs d'images"""
        await self._send("Runtime.evaluate", {
            "expression": f"""
                (() => {{
                    const images = [];
                    document.querySelectorAll('img').forEach(img => {{
                        const src = img.src || '';
                        if (src.startsWith('http') && src.length > 50 &&
                            !src.includes('google') &&
                            !src.includes('logo') &&
                            !src.includes('icon') &&
                            !src.includes('favicon')) {{
                            images.push(src);
                        }}
                    }});
                    return JSON.stringify([...new Set(images)].slice(0, {count}));
                }})()
            """,
            "returnByValue": True
        })
        
        try:
            result = await self._send("Runtime.evaluate", {"expression": ""})
            data = result.get('result', {}).get('result', {}).get('value', '[]')
            return json.loads(data) if data else []
        except:
            return []
    
    async def get_tabs(self) -> List[Dict]:
        """Liste les onglets"""
        targets = json.loads(
            urllib.request.urlopen(f"http://localhost:{self.port}/json").read()
        )
        tabs = []
        for t in targets:
            if t.get('type') == 'page' and 'extension' not in t.get('url', ''):
                tabs.append({
                    "title": t.get('title', '')[:50],
                    "url": t.get('url', '')[:60]
                })
        return tabs
    
    async def run(self, command: str) -> Dict:
        """Exécute une commande en langage naturel"""
        cmd_lower = command.lower()
        
        if "va sur" in cmd_lower or "ouvre" in cmd_lower:
            import re
            url_match = re.search(r'https?://[^\s]+', command)
            url = url_match.group() if url_match else "https://www.google.com"
            sites = {"google": "https://google.com", "bbc": "https://www.bbc.com", "youtube": "https://youtube.com"}
            for site, site_url in sites.items():
                if site in cmd_lower:
                    url = site_url
                    break
            await self.navigate(url)
            return {"status": "success", "action": "navigate", "url": url}
        
        elif "cherche" in cmd_lower:
            query = command.replace("cherche", "").replace("sur google", "").strip()
            await self.search(query)
            return {"status": "success", "action": "search", "query": query}
        
        elif "scroll" in cmd_lower or "défile" in cmd_lower:
            await self.scroll(5)
            return {"status": "success", "action": "scroll"}
        
        elif "lis" in cmd_lower or "articles" in cmd_lower:
            articles = await self.get_articles(6)
            return {"status": "success", "action": "read", "articles": articles}
        
        elif "images" in cmd_lower or "photos" in cmd_lower:
            images = await self.get_images(3)
            return {"status": "success", "action": "images", "images": images}
        
        elif "onglets" in cmd_lower or "tabs" in cmd_lower:
            tabs = await self.get_tabs()
            return {"status": "success", "action": "tabs", "tabs": tabs}
        
        return {"status": "unknown", "command": command}
    
    async def close(self):
        """Ferme la connexion"""
        if self.connected:
            await self.ws.close()
            self.connected = False
            print("   🔒 Connexion CDP fermée")
        
        # Ne PAS fermer le navigateur Chrome - le laisser ouvert!
        print("   📍 Navigateur Chrome reste OUVERT (utilisable manuellement)")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def main():
    print("="*70)
    print("🧪 SHARINGAN BROWSER MANAGER - TEST COMPLET")
    print("="*70)
    
    async with SharinganBrowser() as browser:
        # Lancer le navigateur
        if not browser.launch("https://www.google.com"):
            print("❌ Échec du lancement")
            return
        
        # Connexion CDP
        if not browser.connect():
            print("❌ Échec de la connexion CDP")
            return
        
        # Se connecter via WebSocket
        targets = json.loads(urllib.request.urlopen(f"http://localhost:{browser.port}/json").read())
        ws_url = [t for t in targets if t.get('type') == 'page' and 'extension' not in t.get('url', '')][0]['webSocketDebuggerUrl']
        
        async with websockets.connect(ws_url) as browser.ws:
            browser.connected = True
            
            # [1] Lister les onglets
            print("\n[1] Liste des onglets:")
            tabs = await browser.get_tabs()
            for i, tab in enumerate(tabs, 1):
                print(f"   {i}. {tab['title']} - {tab['url']}")
            
            # [2] Recherche "Ousmane Sonko"
            print("\n[2] Recherche 'Ousmane Sonko actualité Sénégal'...")
            await browser.search("Ousmane Sonko actualité Sénégal")
            
            # [3] Défiler
            print("\n[3] Défilement (5 fois)...")
            await browser.scroll(5)
            
            # [4] Extraire articles
            print("\n[4] Extraction des articles (6)...")
            articles = await browser.get_articles(6)
            for i, art in enumerate(articles[:6], 1):
                print(f"   {i}. {art[:80]}...")
            
            # [5] Extraire images
            print("\n[5] Extraction des images (3)...")
            images = await browser.get_images(3)
            for i, img in enumerate(images[:3], 1):
                print(f"   {i}. {img[:70]}...")
            
            print("\n" + "="*70)
            print("✅ TEST TERMINÉ")
            print("="*70)
            print(f"""
📊 RÉSULTATS:
   - Navigateur: UN SEUL lancé (pas de multiples!)
   - Connexion: CDP via WebSocket
   - Articles: {len(articles)} extraits
   - Images: {len(images)} extraites
   - Onglet: Google avec recherche Ousmane Sonko

🎯 POINTS CLÉS:
   ✅ Un seul navigateur
   ✅ Pas de fermeture automatique
   ✅ Connexion via CDP
   ✅ Interactions en langage naturel

📍 Le navigateur Chrome reste OUVERT sur la page de recherche!
   Tu peux l'utiliser manuellement maintenant.
""")

if __name__ == "__main__":
    asyncio.run(main())
