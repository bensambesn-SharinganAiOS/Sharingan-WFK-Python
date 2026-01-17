#!/usr/bin/env python3
"""
Sharingan CDP Browser Controller - Se connecte à un navigateur existant
Ce module peut se connecter à un Chrome déjà ouvert et interagir avec lui
sans ouvrir un nouveau navigateur.
"""

import asyncio
import json
import urllib.request
import websockets
from typing import Dict, List, Optional, Any
from pathlib import Path

class CDPBrowserController:
    """
    Contrôleur de navigateur via Chrome DevTools Protocol.
    Se connecte à un navigateur Chrome existant via WebSocket.
    """
    
    def __init__(self, port: int = None):
        self.port = port or self._find_chrome_port()
        self.ws_url = None
        self.connected = False
        self.msg_id = 1
        self.current_url = ""
        self.current_title = ""
    
    def _find_chrome_port(self) -> Optional[int]:
        """Trouve le port CDP d'un Chrome existant"""
        import subprocess
        result = subprocess.run(
            "netstat -tlnp 2>/dev/null | grep -E 'chrome|chromedriver' | grep LISTEN | awk '{print $4}' | grep -oP ':\\d+' | grep -oP '\\d+'",
            shell=True, capture_output=True, text=True
        )
        if result.stdout.strip():
            ports = [int(p) for p in result.stdout.strip().split('\n') if p.isdigit()]
            # Prendre le premier port valide (celui du browser, pas chromedriver)
            if ports:
                return ports[0]
        return None
    
    def connect(self) -> bool:
        """Se connecte à un navigateur Chrome existant via CDP"""
        if not self.port:
            print("❌ Aucun navigateur Chrome trouvé!")
            print("   Lance d'abord: google-chrome --remote-debugging-port=9222")
            return False
        
        try:
            # Récupérer l'URL WebSocket
            targets = json.loads(
                urllib.request.urlopen(f"http://localhost:{self.port}/json").read()
            )
            
            for t in targets:
                if t.get('type') == 'page':
                    self.ws_url = t['webSocketDebuggerUrl']
                    self.current_url = t.get('url', 'about:blank')
                    self.current_title = t.get('title', '')
                    break
            
            if not self.ws_url:
                print("❌ Aucune page trouvée dans Chrome")
                return False
            
            # Se connecter via WebSocket
            async def _connect():
                async with websockets.connect(self.ws_url) as ws:
                    self.ws = ws
                    self.connected = True
                    print(f"✅ Connecté à Chrome sur le port {self.port}")
                    print(f"   URL: {self.current_url}")
                    print(f"   Titre: {self.current_title}")
            
            asyncio.run(_connect())
            return True
            
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    async def _send(self, method: str, params: dict = None) -> dict:
        """Envoie une commande CDP"""
        if not self.connected:
            return {"status": "error", "message": "Not connected"}
        
        msg = {"id": self.msg_id, "method": method, "params": params or {}}
        self.msg_id += 1
        
        await self.ws.send(json.dumps(msg))
        response = await self.ws.recv()
        return json.loads(response)
    
    async def navigate(self, url: str) -> Dict:
        """Navigue vers une URL"""
        result = await self._send("Page.navigate", {"url": url})
        await asyncio.sleep(2)
        await self._update_info()
        return {
            "status": "success",
            "url": url,
            "title": self.current_title
        }
    
    async def _update_info(self):
        """Met à jour l'URL et le titre"""
        result = await self._send("Runtime.evaluate", {
            "expression": "JSON.stringify({url: window.location.href, title: document.title})",
            "returnByValue": True
        })
        try:
            data = json.loads(result.get('result', {}).get('result', {}).get('value', '{}'))
            self.current_url = data.get('url', '')
            self.current_title = data.get('title', '')
        except:
            pass
    
    async def search_google(self, query: str) -> Dict:
        """Fait une recherche sur Google"""
        # Aller sur Google
        await self.navigate("https://www.google.com")
        await asyncio.sleep(2)
        
        # Remplir le champ de recherche
        result = await self._send("Runtime.evaluate", {
            "expression": f"""
                (() => {{
                    const input = document.querySelector('input[name="q"]');
                    if (input) {{
                        input.value = '{query}';
                        input.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return 'INPUT_FILLED';
                    }}
                    return 'INPUT_NOT_FOUND';
                }})()
            """,
            "returnByValue": True
        })
        
        await asyncio.sleep(1)
        
        # Appuyer sur Entrée
        await self._send("Runtime.evaluate", {
            "expression": """
                (() => {
                    const input = document.querySelector('input[name="q"]');
                    if (input) {
                        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', bubbles: true}));
                        return 'ENTER_PRESSED';
                    }
                    return 'ENTER_NOT_FOUND';
                })()
            """,
            "returnByValue": True
        })
        
        await asyncio.sleep(3)
        await self._update_info()
        
        return {
            "status": "success",
            "query": query,
            "url": self.current_url,
            "title": self.current_title
        }
    
    async def scroll_down(self, times: int = 3) -> Dict:
        """Défile vers le bas plusieurs fois"""
        for i in range(times):
            await self._send("Runtime.evaluate", {
                "expression": "window.scrollBy(0, 500)"
            })
            await asyncio.sleep(0.5)
        return {"status": "success", "scrolled": times}
    
    async def scroll_up(self, times: int = 3) -> Dict:
        """Défile vers le haut"""
        for i in range(times):
            await self._send("Runtime.evaluate", {
                "expression": "window.scrollBy(0, -500)"
            })
            await asyncio.sleep(0.5)
        return {"status": "success", "scrolled_up": times}
    
    async def get_articles(self, count: int = 6) -> List[Dict]:
        """Récupère les articles de la page actuelle"""
        result = await self._send("Runtime.evaluate", {
            "expression": f"""
                (() => {{
                    const articles = [];
                    // Chercher les liens d'actualités
                    const links = document.querySelectorAll('a');
                    links.forEach(a => {{
                        const href = a.href || '';
                        const text = (a.innerText || '').trim();
                        // Filtres pour les articles d'actualités
                        if (text.length > 30 && text.length < 300 &&
                            !text.includes('Google') &&
                            !text.includes('Sign in') &&
                            !text.includes(' connexion') &&
                            (href.includes('news') || 
                             href.includes('article') ||
                             href.includes('actu') ||
                             text.toLowerCase().includes('sénégal') ||
                             text.toLowerCase().includes('sonko') ||
                             text.toLowerCase().includes('politique') ||
                             text.toLowerCase().includes('afrique'))) {{
                            articles.push({{
                                text: text.substring(0, 150),
                                href: href.substring(0, 100)
                            }});
                        }}
                    }});
                    // Dédoublonner
                    const unique = [];
                    const seen = new Set();
                    articles.forEach(a => {{
                        const key = a.text.substring(0, 40);
                        if (!seen.has(key)) {{
                            seen.add(key);
                            unique.push(a);
                        }}
                    }});
                    return JSON.stringify(unique.slice(0, {count}));
                }})()
            """,
            "returnByValue": True
        })
        
        try:
            articles = json.loads(result.get('result', {}).get('result', {}).get('value', '[]'))
            return articles
        except:
            return []
    
    async def get_images(self, count: int = 3) -> List[Dict]:
        """Récupère les images de la page"""
        result = await self._send("Runtime.evaluate", {
            "expression": f"""
                (() => {{
                    const images = [];
                    const imgs = document.querySelectorAll('img');
                    imgs.forEach(img => {{
                        const src = img.src || '';
                        const alt = img.alt || '';
                        if (src.startsWith('http') && src.length > 20 &&
                            !src.includes('google') &&
                            !src.includes('logo') &&
                            !src.includes('icon') &&
                            !src.includes('favicon')) {{
                            images.push({{
                                src: src.substring(0, 150),
                                alt: alt.substring(0, 50)
                            }});
                        }}
                    }});
                    const unique = [];
                    const seen = new Set();
                    images.forEach(img => {{
                        const key = img.src.substring(0, 50);
                        if (!seen.has(key)) {{
                            seen.add(key);
                            unique.push(img);
                        }}
                    }});
                    return JSON.stringify(unique.slice(0, {count}));
                }})()
            """,
            "returnByValue": True
        })
        
        try:
            images = json.loads(result.get('result', {}).get('result', {}).get('value', '[]'))
            return images
        except:
            return []
    
    async def click_on_text(self, text: str) -> Dict:
        """Clique sur un élément contenant le texte spécifié"""
        result = await self._send("Runtime.evaluate", {
            "expression": f"""
                (() => {{
                    const elements = document.querySelectorAll('a, button, div, span, h1, h2, h3, h4, h5, h6, p');
                    for (let el of elements) {{
                        if (el.innerText && el.innerText.includes('{text}') && el.click) {{
                            el.click();
                            return 'CLICKED: ' + el.innerText.substring(0, 50);
                        }}
                    }}
                    return 'NOT_FOUND';
                }})()
            """,
            "returnByValue": True
        })
        
        await asyncio.sleep(2)
        await self._update_info()
        
        clicked = result.get('result', {}).get('result', {}).get('value', '')
        return {
            "status": "success" if "CLICKED" in clicked else "not_found",
            "clicked": clicked
        }
    
    async def get_tabs(self) -> List[Dict]:
        """Récupère la liste des onglets"""
        # Via CDP, on peut lister les targets
        try:
            targets = json.loads(
                urllib.request.urlopen(f"http://localhost:{self.port}/json").read()
            )
            tabs = []
            for t in targets:
                if t.get('type') == 'page':
                    tabs.append({
                        "url": t.get('url', ''),
                        "title": t.get('title', ''),
                        "id": t.get('id', '')
                    })
            return tabs
        except:
            return []
    
    async def close(self):
        """Ferme la connexion"""
        if self.connected:
            await self.ws.close()
            self.connected = False
            print("🔒 Connexion CDP fermée")


async def main():
    """Test du contrôleur CDP"""
    print("="*70)
    print("🧪 TEST CDP BROWSER CONTROLLER")
    print("="*70)
    
    # Créer le contrôleur
    controller = CDPBrowserController()
    
    # Se connecter au navigateur existant
    if not controller.connect():
        print("\n⚠️  Pas de navigateur trouvé!")
        print("   Lance d'abord un navigateur avec:")
        print("   google-chrome --remote-debugging-port=9222")
        return
    
    # Tester les fonctionnalités
    print("\n[1] Navigation vers Google...")
    await controller.navigate("https://www.google.com")
    
    print("\n[2] Recherche 'Ousmane Sonko'...")
    await controller.search_google("Ousmane Sonko actualité Sénégal")
    
    print("\n[3] Défilement...")
    await controller.scroll_down(3)
    
    print("\n[4] Extraction des articles...")
    articles = await controller.get_articles(6)
    print(f"   Trouvés {len(articles)} articles:")
    for i, art in enumerate(articles, 1):
        print(f"   {i}. {art.get('text', 'N/A')[:60]}...")
    
    print("\n[5] Extraction des images...")
    images = await controller.get_images(3)
    print(f"   Trouvées {len(images)} images:")
    for i, img in enumerate(images, 1):
        print(f"   {i}. {img.get('src', 'N/A')[:60]}...")
    
    print("\n[6] Liste des onglets...")
    tabs = await controller.get_tabs()
    for i, tab in enumerate(tabs, 1):
        print(f"   {i}. {tab.get('title', 'N/A')[:40]} - {tab.get('url', 'N/A')[:40]}")
    
    await controller.close()
    
    print("\n" + "="*70)
    print("✅ TEST TERMINÉ")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
