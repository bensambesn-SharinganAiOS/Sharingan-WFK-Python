#!/usr/bin/env python3
"""
Sharingan Action Executor AVEC NAVIGATEUR PARTAGÉ
Version modifiée pour réutiliser le même navigateur entre les commandes
"""

import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("sharingan.action_executor")

class ActionType(Enum):
    RECON = "recon"
    EXPLOIT = "exploit"
    SCAN = "scan"
    ENUMERATION = "enumeration"
    ANALYSIS = "analysis"
    REPORT = "report"
    CLEANUP = "cleanup"
    BROWSER = "browser"

@dataclass
class ExecutedAction:
    action_type: str
    command: str
    target: Optional[str]
    result: Any
    success: bool
    output: str


class SharedBrowser:
    """
    Navigateur partagé pour toutes les actions Sharingan.
    Un seul navigateur, réutilisé entre les appels.
    """
    
    _instance = None
    _driver = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.current_url = ""
        self.initialized = False
    
    def get_browser(self, url: str = "about:blank") -> Any:
        """Retourne le navigateur partagé"""
        if self._driver is None:
            print("   🚀 Lancement du navigateur partagé...")
            self._driver = self._launch_new_browser()
            if self._driver:
                self.initialized = True
                if url and url != "about:blank":
                    self._driver.get(url)
                    self.current_url = url
            return self._driver
        else:
            print("   ♻️  Réutilisation du navigateur existant")
            if url and url != "current" and url != self.current_url:
                self._driver.get(url)
                self.current_url = url
            return self._driver
    
    def _launch_new_browser(self) -> Any:
        """Lance un nouveau navigateur Chrome"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-first-run")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            driver_path = "/usr/local/bin/chromedriver"
            if Path(driver_path).exists():
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                driver = webdriver.Chrome(options=options)
            
            self.current_url = driver.current_url
            print("   ✅ Navigateur lancé avec succès")
            return driver
            
        except Exception as e:
            print(f"   ❌ Erreur lancement navigateur: {e}")
            return None
    
    def navigate(self, url: str) -> Dict:
        """Navigue vers une URL"""
        if self._driver:
            self._driver.get(url)
            self.current_url = url
            return {"status": "success", "url": url, "title": self._driver.title}
        return {"status": "error", "message": "Navigateur non initialisé"}
    
    def execute_js(self, script: str) -> Dict:
        """Exécute du JavaScript"""
        if self._driver:
            try:
                result = self._driver.execute_script(script)
                return {"status": "success", "result": result}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "error", "message": "Navigateur non initialisé"}
    
    def close(self):
        """Ferme le navigateur partagé"""
        if self._driver:
            self._driver.quit()
            self._driver = None
            self.initialized = False
            print("   🔒 Navigateur partagé fermé")


def get_shared_browser() -> SharedBrowser:
    """Retourne l'instance unique du navigateur partagé"""
    return SharedBrowser()


class ActionExecutor:
    """
    Executes actions with SHARED BROWSER to avoid multiple instances
    """
    
    def __init__(self):
        self.execution_history: List[ExecutedAction] = []
        self.kali_tools = self._initialize_kali_tools()
        # Navigateur partagé entre toutes les actions
        self._shared_browser = get_shared_browser()
    
    def _initialize_kali_tools(self) -> Dict:
        """Initialize available Kali tools"""
        return {
            "nmap": {"path": "/usr/bin/nmap", "capabilities": ["port_scan", "service_detection"]},
            "gobuster": {"path": "/usr/bin/gobuster", "capabilities": ["dir_scan"]},
            "searchsploit": {"path": "/usr/bin/searchsploit", "capabilities": ["exploit_search"]},
            "whois": {"path": "/usr/bin/whois", "capabilities": ["whois_lookup"]},
        }
    
    def analyze_action(self, action_text: str) -> tuple:
        """Analyze action and return (type, target, params)"""
        action_lower = action_text.lower().strip()
        action_original = action_text.strip()
        
        # ========== NAVIGATEUR - Commandes en langage naturel ==========
        browser_navigation_keywords = ["va sur", "navigue vers", "ouvre", "aller à", "ouvre la page"]
        browser_search_keywords = ["cherche", "recherche sur google", "cherche sur le web"]
        browser_read_keywords = ["lis", "lit la page", "lis l'article", "affiche le contenu"]
        browser_scroll_keywords = ["scroll", "défile", "descends", "monte"]
        browser_click_keywords = ["clic", "clique sur", "click sur"]
        browser_screenshot_keywords = ["capture", "screenshot", "prends une photo"]
        browser_tab_keywords = ["nouvel onglet", "nouveau onglet", "ouvre un nouvel onglet"]
        browser_upload_keywords = ["upload", "télécharge un fichier", "envoie un fichier"]
        browser_js_keywords = ["execute js", "exécute javascript", "javascript"]
        
        import re
        
        if any(kw in action_lower for kw in browser_navigation_keywords):
            url_match = re.search(r'https?://[^\s]+', action_original)
            url = url_match.group() if url_match else ""
            if url:
                return ActionType.BROWSER, url, {"browser_action": "navigate", "url": url}
            sites = {
                "google": "https://google.com", "youtube": "https://youtube.com",
                "github": "https://github.com", "bbc": "https://www.bbc.com/afrique",
                "facebook": "https://facebook.com", "twitter": "https://twitter.com"
            }
            for site, site_url in sites.items():
                if site in action_lower:
                    return ActionType.BROWSER, site, {"browser_action": "navigate", "url": site_url}
            return ActionType.BROWSER, "google.com", {"browser_action": "navigate", "url": "https://google.com"}
        
        if any(kw in action_lower for kw in browser_search_keywords):
            query = action_original
            for kw in ["cherche", "recherche", "sur google", "sur le web"]:
                query = query.replace(kw, "").strip()
            return ActionType.BROWSER, "search", {"browser_action": "search", "query": query}
        
        if any(kw in action_lower for kw in browser_read_keywords):
            url_match = re.search(r'https?://[^\s]+', action_original)
            url = url_match.group() if url_match else ""
            if url:
                return ActionType.BROWSER, url, {"browser_action": "read", "url": url}
            return ActionType.BROWSER, "current", {"browser_action": "read"}
        
        if any(kw in action_lower for kw in browser_scroll_keywords):
            pixels = 400
            if "haut" in action_lower or "monte" in action_lower:
                pixels = -400
            return ActionType.BROWSER, "page", {"browser_action": "scroll", "pixels": pixels}
        
        if any(kw in action_lower for kw in browser_click_keywords):
            return ActionType.BROWSER, "element", {"browser_action": "click"}
        
        if any(kw in action_lower for kw in browser_screenshot_keywords):
            return ActionType.BROWSER, "screenshot", {"browser_action": "screenshot"}
        
        if any(kw in action_lower for kw in browser_tab_keywords):
            url_match = re.search(r'https?://[^\s]+', action_original)
            url = url_match.group() if url_match else "about:blank"
            return ActionType.BROWSER, url, {"browser_action": "new_tab", "url": url}
        
        if any(kw in action_lower for kw in browser_upload_keywords):
            file_match = re.search(r'/[^\s]+', action_original)
            file_path = file_match.group() if file_match else "/tmp/test_image.jpg"
            return ActionType.BROWSER, "upload", {"browser_action": "upload", "file_path": file_path}
        
        if any(kw in action_lower for kw in browser_js_keywords):
            js_code = action_original
            for kw in ["execute", "exécute", "javascript", "js"]:
                js_code = js_code.replace(kw, "").strip()
            return ActionType.BROWSER, "js", {"browser_action": "execute_js", "script": js_code}
        
        # ========== KALI TOOLS ==========
        if action_lower.startswith("nmap"):
            parts = action_original.split()
            target = "localhost"
            for i, part in enumerate(parts):
                if i == 0: continue
                if not part.startswith('-'):
                    target = part
                    break
            return ActionType.SCAN, target, {"tool": "nmap"}
        
        if "gobuster" in action_lower:
            for part in action_original.split():
                if part.startswith("http://") or part.startswith("https://"):
                    target = part.replace("http://", "").replace("https://", "").rstrip('/')
                    return ActionType.ENUMERATION, target, {"tool": "gobuster"}
        
        # Fallback
        hostname_match = re.search(r'([a-zA-Z0-9.-]+\.[a-z]{2,})', action_original)
        target = hostname_match.group() if hostname_match else "unknown"
        return ActionType.ANALYSIS, target, {"original_cmd": action_original}
    
    def execute_action(self, action_text: str, motivation: str = "unknown") -> Dict[str, Any]:
        """Execute a single action using SHARED BROWSER"""
        action_type, target, params = self.analyze_action(action_text)
        
        logger.info(f"Executing action: {action_text}")
        logger.info(f"Action type: {action_type}, Target: {target}")
        
        if action_type == ActionType.BROWSER:
            return self._execute_browser_shared(target, params)
        elif action_type == ActionType.SCAN:
            return self._execute_scan(target, params)
        elif action_type == ActionType.ENUMERATION:
            return self._execute_enumeration(target, params)
        else:
            return self._execute_analysis(target, params)
    
    def _execute_browser_shared(self, target: str, params: Dict) -> Dict[str, Any]:
        """Execute browser action using SHARED BROWSER - ONLY ONE BROWSER!"""
        browser_action = params.get("browser_action", "navigate")
        
        try:
            from selenium.webdriver.common.by import By
            import time
            
            # UTILISER LE NAVIGATEUR PARTAGÉ
            driver = self._shared_browser.get_browser()
            if driver is None:
                return {"status": "error", "message": "Failed to get shared browser"}
            
            result = {}
            
            if browser_action == "navigate":
                url = params.get("url", "https://google.com")
                driver.get(url)
                time.sleep(2)
                result = {
                    "status": "success",
                    "action": "navigate",
                    "url": url,
                    "current_url": driver.current_url,
                    "title": driver.title
                }
            
            elif browser_action == "search":
                query = params.get("query", "")
                driver.get("https://www.google.com")
                time.sleep(2)
                try:
                    search_box = driver.find_element(By.CSS_SELECTOR, 'input[name="q"]')
                    search_box.send_keys(query)
                    search_box.send_keys("\n")
                    time.sleep(2)
                    result = {
                        "status": "success",
                        "action": "search",
                        "query": query,
                        "url": driver.current_url,
                        "title": driver.title
                    }
                except Exception as e:
                    result = {"status": "error", "message": str(e)}
            
            elif browser_action == "read":
                url = params.get("url", "")
                if url:
                    driver.get(url)
                    time.sleep(3)
                title = driver.title
                try:
                    headings = driver.find_elements(By.CSS_SELECTOR, 'h1, h2, h3')
                    heading_texts = [h.text[:100] for h in headings[:5] if h.text]
                except:
                    heading_texts = []
                result = {
                    "status": "success",
                    "action": "read",
                    "title": title,
                    "headings": heading_texts,
                    "url": driver.current_url
                }
            
            elif browser_action == "scroll":
                pixels = params.get("pixels", 400)
                for i in range(3):
                    driver.execute_script(f"window.scrollBy(0, {pixels})")
                    time.sleep(0.5)
                result = {
                    "status": "success",
                    "action": "scroll",
                    "pixels": pixels * 3,
                    "url": driver.current_url
                }
            
            elif browser_action == "click":
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, 'button, a')
                    for btn in buttons:
                        if btn.is_displayed():
                            btn.click()
                            break
                    result = {"status": "success", "action": "click", "url": driver.current_url}
                except Exception as e:
                    result = {"status": "error", "message": str(e)}
            
            elif browser_action == "screenshot":
                path = "/tmp/sharingan_screenshot.png"
                try:
                    driver.save_screenshot(path)
                    result = {"status": "success", "action": "screenshot", "path": path, "url": driver.current_url}
                except Exception as e:
                    result = {"status": "error", "message": str(e)}
            
            elif browser_action == "new_tab":
                url = params.get("url", "about:blank")
                driver.execute_script(f"window.open('{url}', '_blank')")
                time.sleep(2)
                tabs = driver.window_handles
                driver.switch_to.window(tabs[-1])
                time.sleep(1)
                result = {
                    "status": "success",
                    "action": "new_tab",
                    "url": driver.current_url,
                    "total_tabs": len(tabs)
                }
            
            elif browser_action == "upload":
                file_path = params.get("file_path", "/tmp/test_image.jpg")
                driver.get("https://tmpfiles.org")
                time.sleep(2)
                try:
                    file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                    file_input.send_keys(file_path)
                    result = {"status": "success", "action": "upload", "file": file_path, "url": driver.current_url}
                except Exception as e:
                    result = {"status": "error", "message": str(e)}
            
            elif browser_action == "execute_js":
                script = params.get("script", "return document.title")
                try:
                    js_result = driver.execute_script(script)
                    result = {"status": "success", "action": "execute_js", "result": str(js_result), "url": driver.current_url}
                except Exception as e:
                    result = {"status": "error", "message": str(e)}
            
            else:
                result = {"status": "error", "message": f"Unknown browser action: {browser_action}"}
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _execute_scan(self, target: str, params: Dict) -> Dict[str, Any]:
        tool = params.get("tool", "nmap")
        cmd = f"nmap {params.get('flags', '-sV -sC')} {target}"
        return self._run_command(cmd, "scan", target)
    
    def _execute_enumeration(self, target: str, params: Dict) -> Dict[str, Any]:
        tool = params.get("tool", "gobuster")
        cmd = f"gobuster dir -u http://{target}/ -w /usr/share/wordlists/dirb/common.txt -q"
        return self._run_command(cmd, "enumeration", target)
    
    def _execute_analysis(self, target: str, params: Dict) -> Dict[str, Any]:
        original_cmd = params.get("original_cmd", "")
        if original_cmd:
            return self._run_command(original_cmd, "analysis", target)
        return {"status": "success", "output": f"Analysis of {target}"}
    
    def _run_command(self, cmd: str, action_type: str, target: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout + result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    # Test du système avec navigateur partagé
    print("="*70)
    print("🧪 TEST SYSTÈME AVEC NAVIGATEUR PARTAGÉ")
    print("="*70)
    
    executor = ActionExecutor()
    
    print("\n[1] 'va sur Google'")
    r1 = executor.execute_action("va sur Google")
    print(f"   Status: {r1.get('status')}, URL: {r1.get('url', 'N/A')[:50]}")
    
    print("\n[2] 'cherche Sénégal actualité'")
    r2 = executor.execute_action("cherche Sénégal actualité")
    print(f"   Status: {r2.get('status')}, URL: {r2.get('url', 'N/A')[:50]}")
    
    print("\n[3] 'ouvre la page https://www.bbc.com/afrique'")
    r3 = executor.execute_action("ouvre la page https://www.bbc.com/afrique")
    print(f"   Status: {r3.get('status')}, URL: {r3.get('url', 'N/A')[:50]}")
    
    # Vérifier le nombre de navigateurs
    result = subprocess.run("ps aux | grep 'chrome --' | grep -v grep | wc -l", shell=True, capture_output=True, text=True)
    count = int(result.stdout.strip())
    
    print("\n" + "="*70)
    print("📊 RÉSULTAT")
    print("="*70)
    print(f"\nNavigateurs ouverts: {count}")
    
    if count <= 1:
        print("✅ SUCCÈS: Un seul navigateur réutilisé!")
    else:
        print(f"⚠️ PROBLÈME: {count} navigateurs ouverts")
    
    print(f"\nURLs visitées:")
    for i, r in enumerate([r1, r2, r3], 1):
        url = r.get('url', 'N/A')
        if url and url != 'N/A':
            print(f"   {i}. {url[:60]}...")
    
    print("\n" + "="*70)
