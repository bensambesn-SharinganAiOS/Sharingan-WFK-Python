#!/usr/bin/env python3
"""
SharingAN Browser Ready-to-Use API
===================================

Interface SIMPLE et DIRECTE pour utiliser le navigateur Sharingan.
Plus besoin de créer de scripts !

Usage:
    # Option 1: Import direct (le plus simple)
    from browser_shell import browser, go, read, search, scroll
    
    await go("https://wikipedia.org")
    content = await read()
    await search("Python programming")
    
    # Option 2: Shell interactif
    python3 browser_shell.py
    
    # Option 3: Ligne de commande
    python3 browser_shell.py --cmd "go https://google.com && search test"
"""
import asyncio
import sys
import argparse
from typing import Optional, List, Dict, Any

sys.path.insert(0, '/root/Projets/Sharingan-WFK-Python')


class BrowserShell:
    """Shell de navigateur simple et intuitif."""
    
    def __init__(self):
        self._browser = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Se connecter au navigateur partagé."""
        if self._connected:
            return True
        
        from sharingans_browser_shared import get_browser, ensure_browser_connected
        self._browser = get_browser()
        self._connected = await ensure_browser_connected(timeout=10.0)
        
        if self._connected:
            print("   ✅ Navigateur connecté (CDP port 9999)")
        else:
            print("   ❌ Échec de connexion au navigateur")
        
        return self._connected
    
    @property
    def br(self):
        """Accès au navigateur CDP."""
        if not self._connected or self._browser is None:
            raise RuntimeError("Non connecté. Appelez connect() d'abord.")
        # BrowserAPI a la propriété 'br' qui retourne le CDPBrowser
        return self._browser.br
    
    async def go(self, url: str) -> Dict[str, Any]:
        await self.connect()
        success = await self.br.navigate(url)
        await asyncio.sleep(1)
        return {"status": "success" if success else "error", "url": await self.br.get_url()}
    
    async def search(self, query: str) -> Dict[str, Any]:
        await self.connect()
        await self.br.navigate("https://www.google.com")
        await asyncio.sleep(1)
        await self.br.type_text(query, "input[name='q']")
        await self.br.press_key("Enter")
        await asyncio.sleep(2)
        return {"status": "success", "query": query, "url": await self.br.get_url()}
    
    async def read(self, selector: str = "article", max_chars: int = 3000) -> str:
        await self.connect()
        return await self.br.get_text(selector, max_length=max_chars)
    
    async def scroll(self, pixels: int = 500, times: int = 1) -> Dict[str, Any]:
        await self.connect()
        await self.br.scroll(0, pixels, times=times)
        return {"status": "success", "scrolled": pixels * times}
    
    async def click(self, selector: str) -> Dict[str, Any]:
        await self.connect()
        success = await self.br.click(selector)
        await asyncio.sleep(1)
        return {"status": "success" if success else "error"}
    
    async def type(self, text: str, selector: str = "input") -> Dict[str, Any]:
        await self.connect()
        success = await self.br.type_text(text, selector)
        return {"status": "success" if success else "error"}
    
    async def press(self, key: str) -> Dict[str, Any]:
        await self.connect()
        success = await self.br.press_key(key)
        return {"status": "success" if success else "error"}
    
    async def current(self) -> Dict[str, Any]:
        await self.connect()
        return {"url": await self.br.get_url(), "title": await self.br.get_title()}
    
    async def screenshot(self, path: Optional[str] = None) -> Dict[str, Any]:
        if path is None:
            import tempfile
            from pathlib import Path
            path = str(Path(tempfile.gettempdir()) / "sharingan.png")
        await self.connect()
        success = await self.br.get_screenshot(path)
        return {"status": "success" if success else "error", "path": path}
    
    async def js(self, code: str) -> Any:
        await self.connect()
        return await self.br.execute_js(code)
    
    async def close(self):
        if self._browser:
            await self._browser.disconnect()
            self._connected = False


_browser_shell: Optional[BrowserShell] = None


def get_browser_shell() -> BrowserShell:
    global _browser_shell
    if _browser_shell is None:
        _browser_shell = BrowserShell()
    return _browser_shell


async def go(url: str) -> Dict[str, Any]:
    return await get_browser_shell().go(url)


async def search(query: str) -> Dict[str, Any]:
    return await get_browser_shell().search(query)


async def read(selector: str = "article", max_chars: int = 3000) -> str:
    return await get_browser_shell().read(selector, max_chars)


async def scroll(pixels: int = 500, times: int = 1) -> Dict[str, Any]:
    return await get_browser_shell().scroll(pixels, times)


async def click(selector: str) -> Dict[str, Any]:
    return await get_browser_shell().click(selector)


async def type(text: str, selector: str = "input") -> Dict[str, Any]:
    return await get_browser_shell().type(text, selector)


async def press(key: str) -> Dict[str, Any]:
    return await get_browser_shell().press(key)


async def current() -> Dict[str, Any]:
    return await get_browser_shell().current()


async def screenshot(path: Optional[str] = None) -> Dict[str, Any]:
    return await get_browser_shell().screenshot(path)


class InteractiveShell:
    COMMANDS = {
        'go': ('go <url>', 'Naviguer'),
        'search': ('search <terme>', 'Recherche Google'),
        'read': ('read', 'Lire le contenu'),
        'scroll': ('scroll [pixels]', 'Défiler'),
        'click': ('click <selector>', 'Cliquer'),
        'type': ('type <text> [selector]', 'Taper'),
        'press': ('press <key>', 'Appuyer sur une touche'),
        'current': ('current', 'URL et titre'),
        'screenshot': ('screenshot [path]', 'Capture'),
        'js': ('js <code>', 'JavaScript'),
        'help': ('help', 'Aide'),
        'quit': ('quit', 'Quitter'),
    }
    
    def __init__(self):
        self.browser = get_browser_shell()
        self.running = False
    
    async def run(self):
        self.running = True
        print("""
╔═══════════════════════════════════════════════════════════════╗
║       SHARINGAN BROWSER - SHELL INTERACTIF                    ║
╠═══════════════════════════════════════════════════════════════╣
║  Commandes: go, search, read, scroll, click, type, press,    ║
║             current, screenshot, js, help, quit               ║
╚═══════════════════════════════════════════════════════════════╝
        """)
        
        if await self.browser.connect():
            print()
        
        while self.running:
            try:
                cmd_input = input("browser> ").strip()
            except EOFError:
                break
            
            if not cmd_input:
                continue
            
            await self.execute(cmd_input)
        
        await self.browser.close()
    
    async def execute(self, cmd_input: str):
        parts = cmd_input.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        try:
            if cmd in ('quit', 'exit'):
                self.running = False
                return
            
            elif cmd == 'help':
                print("\nCommandes:")
                for name, (usage, desc) in self.COMMANDS.items():
                    print(f"  {usage:18s} → {desc}")
                print()
            
            elif cmd == 'go':
                if not args:
                    print("Usage: go <url>\n")
                    return
                result = await self.browser.go(args)
                print(f"   ✅ {result.get('url')}\n")
            
            elif cmd == 'search':
                if not args:
                    print("Usage: search <terme>\n")
                    return
                result = await self.browser.search(args)
                print(f"   ✅ Recherche: {result.get('query')}\n")
            
            elif cmd == 'read':
                text = await self.browser.read()
                print(f"\n{'─' * 50}")
                print(text[:1000] if len(text) > 1000 else text)
                print(f"{'─' * 50}\n")
            
            elif cmd == 'scroll':
                pixels = int(args) if args.isdigit() else 500
                await self.browser.scroll(pixels)
                print(f"   ✅ Défilé: {pixels}px\n")
            
            elif cmd == 'click':
                if not args:
                    print("Usage: click <selector>\n")
                    return
                result = await self.browser.click(args)
                print(f"   {'✅' if result.get('status')=='success' else '❌'}\n")
            
            elif cmd == 'type':
                parts = args.split(maxsplit=1)
                text = parts[0]
                selector = parts[1] if len(parts) > 1 else "input"
                result = await self.browser.type(text, selector)
                print(f"   {'✅' if result.get('status')=='success' else '❌'}\n")
            
            elif cmd == 'press':
                await self.browser.press(args)
                print("   ✅\n")
            
            elif cmd == 'current':
                result = await self.browser.current()
                print(f"   URL: {result.get('url')}")
                print(f"   Titre: {result.get('title')}\n")
            
            elif cmd == 'screenshot':
                result = await self.browser.screenshot()
                print(f"   {'✅' if result.get('status')=='success' else '❌'} {result.get('path')}\n")
            
            elif cmd == 'js':
                if not args:
                    print("Usage: js <code>\n")
                    return
                result = await self.browser.js(args)
                print(f"   Résultat: {result}\n")
            
            else:
                print(f"   Commande inconnue: {cmd}\n")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}\n")


async def execute_command_string(cmd_string: str) -> str:
    shell = get_browser_shell()
    
    if not await shell.connect():
        return "❌ Connexion impossible"
    
    outputs = []
    commands = [c.strip() for c in cmd_string.split('&&')]
    
    for cmd in commands:
        if not cmd:
            continue
        
        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        try:
            if action == 'go':
                result = await shell.go(args)
                outputs.append(f"✅ {result.get('url')}")
            elif action == 'search':
                result = await shell.search(args)
                outputs.append(f"✅ {result.get('query')}")
            elif action == 'read':
                text = await shell.read()
                outputs.append(f"📄 {len(text)} caractères")
            elif action == 'scroll':
                pixels = int(args) if args.isdigit() else 500
                await shell.scroll(pixels)
                outputs.append(f"⬇️ {pixels}px")
            elif action == 'screenshot':
                result = await shell.screenshot()
                outputs.append(f"📸 {result.get('path')}")
            elif action == 'current':
                result = await shell.current()
                outputs.append(f"🌐 {result.get('url')}")
            else:
                outputs.append(f"⚠️ {action}")
        except Exception as e:
            outputs.append(f"❌ {e}")
    
    return '\n'.join(outputs)


def main():
    parser = argparse.ArgumentParser(
        description="SharingAN Browser - Interface prête à l'emploi",
        epilog="""
Exemples:
  python3 browser_shell.py                    # Shell interactif
  python3 browser_shell.py -c "go https://google.com"
  python3 browser_shell.py -c "go wikipedia && read && scroll 300"
        """
    )
    parser.add_argument('--cmd', '-c', type=str, help='Commandes (&& pour séparer)')
    parser.add_argument('--shell', '-s', action='store_true', help='Shell interactif')
    args = parser.parse_args()
    
    if args.shell or not args.cmd:
        asyncio.run(InteractiveShell().run())
    else:
        result = asyncio.run(execute_command_string(args.cmd))
        print(result)


if __name__ == "__main__":
    main()
