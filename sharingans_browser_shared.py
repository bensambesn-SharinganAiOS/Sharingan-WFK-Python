#!/usr/bin/env python3
"""
SharingAN Browser Shared - Module de navigateur partagé (Singleton)

Ce module fournit une connexion CDP unique et persistante au navigateur
Chrome qui est lancé une seule fois et réutilisé pour toutes les
interactions Sharingan OS.

Usage:
    from sharingans_browser_shared import browser, navigate, get_text, scroll
    
    await navigate("https://google.com")
    content = await get_text()
"""
import asyncio
import json
import logging
import urllib.request
from typing import Any, Optional, Dict
import websockets

logger = logging.getLogger("sharingan.browser.shared")


class CDPBrowser:
    """
    Connexion CDP vers un navigateur Chrome partagé.
    """
    def __init__(self, host: str = "localhost", port: int = 9999):
        self.host = host
        self.port = port
        self.ws: Any = None
        self.target_id: str = ""
        self.message_id: int = 1
    
    @property
    def json_url(self) -> str:
        return f"http://{self.host}:{self.port}/json"
    
    async def connect(self, timeout: float = 10.0) -> bool:
        try:
            loop = asyncio.get_event_loop()
            targets_json = await loop.run_in_executor(
                None, 
                lambda: urllib.request.urlopen(self.json_url, timeout=5).read()
            )
            targets = json.loads(targets_json)
            
            if not targets:
                logger.error("Aucune cible CDP trouvée")
                return False
            
            target = targets[0]
            self.target_id = target.get("id", "")
            ws_url = target.get("webSocketDebuggerUrl", "")
            
            if not ws_url:
                ws_url = f"ws://{self.host}:{self.port}/devtools/page/{self.target_id}"
            
            self.ws = await asyncio.wait_for(
                websockets.connect(ws_url, open_timeout=timeout),
                timeout=timeout
            )
            
            await self._send_message("Browser.getVersion")
            logger.info(f"Connecté au navigateur CDP (target: {self.target_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur de connexion CDP: {e}")
            return False
    
    async def disconnect(self) -> None:
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
            self.ws = None
    
    async def _send_message(self, method: str, params: Optional[Dict] = None, timeout: float = 10.0) -> Dict:
        if not self.ws:
            raise RuntimeError("Pas de connexion WebSocket active")
        
        msg_id = self.message_id
        self.message_id += 1
        
        message = {"id": msg_id, "method": method}
        if params:
            message["params"] = params
        
        await self.ws.send(json.dumps(message))
        
        try:
            response = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
            return json.loads(response)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout pour {method}")
    
    async def navigate(self, url: str, timeout: float = 30.0) -> bool:
        try:
            await self._send_message("Page.navigate", {"url": url}, timeout)
            await asyncio.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Erreur de navigation: {e}")
            return False
    
    async def get_text(self, selector: str = "body", max_length: int = 5000) -> str:
        try:
            result = await self._send_message("Runtime.evaluate", {
                "expression": f"document.querySelector('{selector}')?.innerText || ''",
                "returnByValue": True
            })
            text = result.get("result", {}).get("result", {}).get("value", "")
            return text[:max_length]
        except Exception as e:
            logger.error(f"Erreur d'extraction: {e}")
            return ""
    
    async def scroll(self, x: int = 0, y: int = 500, times: int = 1, delay: float = 0.5) -> None:
        for _ in range(times):
            await self._send_message("Runtime.evaluate", {
                "expression": f"window.scrollBy({x}, {y})"
            })
            await asyncio.sleep(delay)
    
    async def click(self, selector: str) -> bool:
        try:
            await self._send_message("Runtime.evaluate", {
                "expression": f"""
                    (function() {{
                        const el = document.querySelector('{selector}');
                        if (el) {{
                            el.click();
                            return 'clicked';
                        }}
                        return 'not-found';
                    }})()
                """,
                "returnByValue": True
            })
            await asyncio.sleep(1)
            return True
        except Exception:
            return False
    
    async def type_text(self, text: str, selector: str = "input") -> bool:
        try:
            expression = f"""
                (function() {{
                    const el = document.querySelector('{selector}');
                    if (!el) return 'not-found';
                    el.value = `{text}`;
                    el.dispatchEvent(new Event('input', {{bubbles: true}}));
                    el.dispatchEvent(new Event('change', {{bubbles: true}}));
                    return 'typed';
                }})()
            """
            result = await self._send_message("Runtime.evaluate", {
                "expression": expression,
                "returnByValue": True
            })
            return result.get("result", {}).get("result", {}).get("value") == "typed"
        except Exception:
            return False
    
    async def press_key(self, key: str) -> bool:
        try:
            await self._send_message("Runtime.evaluate", {
                "expression": f"document.activeElement?.dispatchEvent(new KeyboardEvent('keydown', {{key: '{key}'}}))"
            })
            return True
        except Exception:
            return False
    
    async def get_url(self) -> str:
        try:
            result = await self._send_message("Runtime.evaluate", {
                "expression": "window.location.href",
                "returnByValue": True
            })
            return result.get("result", {}).get("result", {}).get("value", "")
        except Exception:
            return ""
    
    async def get_title(self) -> str:
        try:
            result = await self._send_message("Runtime.evaluate", {
                "expression": "document.title",
                "returnByValue": True
            })
            return result.get("result", {}).get("result", {}).get("value", "")
        except Exception:
            return ""
    
    async def execute_js(self, code: str, timeout: float = 10.0) -> Any:
        try:
            result = await self._send_message("Runtime.evaluate", {
                "expression": code,
                "returnByValue": True,
                "timeout": int(timeout * 1000)
            }, timeout)
            return result.get("result", {}).get("result", {}).get("value")
        except Exception as e:
            logger.error(f"Erreur JS: {e}")
            return None
    
    async def get_screenshot(self, path: str) -> bool:
        try:
            result = await self._send_message("Runtime.evaluate", {
                "expression": """
                    (function() {
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        canvas.width = window.innerWidth;
                        canvas.height = window.innerHeight;
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        ctx.font = '20px Arial';
                        ctx.fillStyle = 'black';
                        ctx.fillText('SharingAN Screenshot', 50, 50);
                        return canvas.toDataURL('image/png');
                    })()
                """,
                "returnByValue": True
            })
            if result:
                import base64
                data = result.get("result", {}).get("result", {}).get("value", "")
                if data.startswith("data:image/png;base64,"):
                    data = data[len("data:image/png;base64,"):]
                with open(path, "wb") as f:
                    f.write(base64.b64decode(data))
                return True
            return False
        except Exception:
            return False


# =============================================================================
# SINGLETON GLOBAL
# =============================================================================

_cdp_browser: Optional[CDPBrowser] = None
_connected: bool = False


def _get_browser() -> CDPBrowser:
    """Obtenir l'objet CDPBrowser global."""
    global _cdp_browser
    if _cdp_browser is None:
        _cdp_browser = CDPBrowser()
    return _cdp_browser


async def _ensure_connected() -> bool:
    """S'assurer que le navigateur est connecté."""
    global _connected
    if _connected:
        return True
    browser = _get_browser()
    _connected = await browser.connect()
    return _connected


class BrowserAPI:
    """Interface simple pour le navigateur partagé."""
    _instance: Optional["BrowserAPI"] = None
    
    def __new__(cls) -> "BrowserAPI":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def br(self) -> CDPBrowser:
        if not _connected:
            raise RuntimeError("Navigateur non connecté. Appelez await connect() d'abord.")
        return _get_browser()
    
    async def connect(self) -> bool:
        result = await _ensure_connected()
        if result:
            print("   ✅ Navigateur CDP connecté (singleton)")
        return result
    
    async def disconnect(self) -> None:
        global _connected
        browser = _get_browser()
        await browser.disconnect()
        _connected = False
    
    @property
    def is_connected(self) -> bool:
        return _connected


def get_browser() -> BrowserAPI:
    """Obtenir l'instance de l'API navigateur."""
    return BrowserAPI()


# =============================================================================
# FONCTIONS DE COMMODITÉ
# =============================================================================

async def navigate(url: str) -> Dict[str, Any]:
    await _ensure_connected()
    browser = _get_browser()
    success = await browser.navigate(url)
    return {"status": "success" if success else "error", "url": await browser.get_url()}


async def search(query: str) -> Dict[str, Any]:
    await _ensure_connected()
    browser = _get_browser()
    await browser.navigate("https://www.google.com")
    await browser.type_text(query, "input[name='q']")
    await browser.press_key("Enter")
    await asyncio.sleep(2)
    return {"status": "success", "query": query, "url": await browser.get_url()}


async def get_text(selector: str = "body", max_length: int = 3000) -> str:
    await _ensure_connected()
    browser = _get_browser()
    return await browser.get_text(selector, max_length)


async def scroll(pixels: int = 500, times: int = 1) -> Dict[str, Any]:
    await _ensure_connected()
    browser = _get_browser()
    await browser.scroll(0, pixels, times=times)
    return {"status": "success", "scrolled": pixels * times}


async def click(selector: str) -> Dict[str, Any]:
    await _ensure_connected()
    browser = _get_browser()
    success = await browser.click(selector)
    await asyncio.sleep(1)
    return {"status": "success" if success else "error"}


async def type_text(text: str, selector: str = "input") -> Dict[str, Any]:
    await _ensure_connected()
    browser = _get_browser()
    success = await browser.type_text(text, selector)
    return {"status": "success" if success else "error"}


async def press_key(key: str) -> Dict[str, Any]:
    await _ensure_connected()
    browser = _get_browser()
    success = await browser.press_key(key)
    return {"status": "success" if success else "error"}


async def get_url() -> str:
    await _ensure_connected()
    browser = _get_browser()
    return await browser.get_url()


async def get_title() -> str:
    await _ensure_connected()
    browser = _get_browser()
    return await browser.get_title()


async def current() -> Dict[str, Any]:
    await _ensure_connected()
    browser = _get_browser()
    return {"url": await browser.get_url(), "title": await browser.get_title()}


async def execute_js(code: str) -> Any:
    await _ensure_connected()
    browser = _get_browser()
    return await browser.execute_js(code)


async def screenshot(path: str = "/tmp/sharingan.png") -> Dict[str, Any]:
    await _ensure_connected()
    browser = _get_browser()
    success = await browser.get_screenshot(path)
    return {"status": "success" if success else "error", "path": path}


# Alias pour compatibilité
async def ensure_browser_connected(timeout: float = 10.0) -> bool:
    """Alias pour _ensure_connected (compatibilité)."""
    return await _ensure_connected()


if __name__ == "__main__":
    async def test():
        print("Test du module sharingans_browser_shared...")
        
        print(f"URL: {await get_url()}")
        print(f"Titre: {await get_title()}")
        
        await navigate("https://example.com")
        print(f"Après navigation: {await get_url()}")
        
        await scroll(300)
        print("Défilé")
        
        await disconnect()
        print("Déconnecté")
    
    async def disconnect():
        global _connected
        browser = _get_browser()
        await browser.disconnect()
        _connected = False
    
    asyncio.run(test())
