#!/usr/bin/env python3
"""
Sharingan OS - Browser Controller Complet
Toutes les capacites d'un utilisateur normal avec un navigateur.
"""

import os
import sys
import time
import logging
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger("sharingan.browser")

SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    SELENIUM_AVAILABLE = True
except ImportError:
    logger.warning("Selenium non installe. pip install selenium")


class BrowserController:
    """
    Controleur de navigateur complet.
    Toutes les capacites d'un utilisateur normal.
    SUPporte la connexion à un navigateur existant via CDP.
    """
    
    # Variable globale pour maintenir le navigateur entre les instances
    _shared_driver = None
    _shared_driver_port = None
    
    def __init__(self, browser: str = "chrome", headless: bool = False,
                 width: int = 1920, height: int = 1080, use_shared: bool = True):
        self.driver: Optional[Any] = None
        self.browser_type = browser.lower()
        self.headless = headless or os.environ.get("DISPLAY") is None
        self.width = width
        self.height = height
        self.current_url = ""
        self.tab_handles: List[str] = []
        self.use_shared = use_shared
        self.is_connected = False  # Si True, on utilise un navigateur existant
        
    def _get_driver_path(self, driver_name: str) -> Optional[str]:
        paths = [
            f"/usr/local/bin/{driver_name}",
            f"/usr/bin/{driver_name}",
            str(Path.home() / ".local" / "bin" / driver_name)
        ]
        for p in paths:
            if Path(p).exists():
                return p
        import shutil
        return shutil.which(driver_name)
    
    def _find_existing_chrome_port(self) -> Optional[int]:
        """Trouve le port CDP d'un Chrome existant"""
        import subprocess
        result = subprocess.run(
            "netstat -tlnp 2>/dev/null | grep chrome | grep LISTEN | head -5",
            shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 7:
                    # Chercher le format "127.0.0.1:PORT"
                    for part in parts:
                        if ':' in part and part.count('.') == 3 or part.startswith('::1:'):
                            try:
                                port = int(part.split(':')[-1])
                                if 9000 < port < 70000:  # Ports Chrome typiques
                                    return port
                            except:
                                pass
        return None
    
    def _connect_to_existing_chrome(self, port: int) -> bool:
        """Tente de se connecter à un Chrome existant via Selenium Remote"""
        try:
            # Essayer de se connecter via Remote WebDriver
            remote_url = f"http://localhost:{port}"
            self.driver = webdriver.Remote(
                command_executor=remote_url,
                options=webdriver.ChromeOptions()
            )
            self.current_url = self.driver.current_url
            self.tab_handles = self.driver.window_handles
            self.is_connected = True
            logger.info(f"Connecté au navigateur existant sur le port {port}")
            return True
        except Exception as e:
            logger.debug(f"Impossible de se connecter via remote {port}: {e}")
            return False
    
    def _use_cdp_for_existing(self, port: int) -> bool:
        """Utilise CDP pour contrôler un Chrome existant"""
        # On ne peut pas contrôler via Selenium, mais on peut via CDP
        # Marquer comme "CDP mode" où on utilise execute_js pour tout
        self.cdp_port = port
        self.is_connected = True
        # Essayer de получить l'URL via CDP
        try:
            import urllib.request
            import json
            targets = json.loads(
                urllib.request.urlopen(f"http://localhost:{port}/json").read()
            )
            if targets:
                self.current_url = targets[0].get('url', 'about:blank')
                logger.info(f"Connecté via CDP au port {port}, URL: {self.current_url}")
                return True
        except Exception as e:
            logger.debug(f"Erreur CDP: {e}")
        return False
    
    # =========================================================================
    # LANCEMENT ET FERMETURE
    # =========================================================================
    
    def launch_browser(self, url: Optional[str] = None, 
                       reuse_existing: bool = True) -> Dict[str, Any]:
        """
        Lance le navigateur avec url optionnelle.
        Si reuse_existing=True, essaie de se connecter à un navigateur existant.
        """
        if not SELENIUM_AVAILABLE:
            return {"status": "error", "message": "Selenium non installe"}
        
        # SI on veut réutiliser un navigateur existant
        if reuse_existing:
            existing_port = self._find_existing_chrome_port()
            if existing_port:
                logger.info(f"Navigateur existant trouvé sur le port {existing_port}")
                
                # Essayer de se connecter via Selenium Remote
                if self._connect_to_existing_chrome(existing_port):
                    if url:
                        self.navigate(url)
                    return {
                        "status": "success", 
                        "message": "Connecté au navigateur existant",
                        "mode": "connected",
                        "port": existing_port,
                        "url": self.current_url
                    }
                
                # Sinon utiliser CDP mode (read-only, execute_js fonctionne)
                if self._use_cdp_for_existing(existing_port):
                    if url and url != self.current_url:
                        # En mode CDP, on peut naviguer via execute_js
                        self.execute_js(f"window.location.href = '{url}'")
                        self.current_url = url
                    return {
                        "status": "success",
                        "message": "Connecté au navigateur existant via CDP",
                        "mode": "cdp",
                        "port": existing_port,
                        "url": self.current_url
                    }
        
        # Aucun navigateur existant ou pas de réutilisation demandée
        # -> Lancer un nouveau navigateur
        
        try:
            if self.browser_type == "firefox":
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
            else:
                options = ChromeOptions()
                if self.headless:
                    options.add_argument("--headless=new")
            
            options.add_argument(f"--width={self.width}")
            options.add_argument(f"--height={self.height}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-background-networking")
            options.add_argument("--no-first-run")
            
            if self.browser_type == "chrome":
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)
                driver_path = self._get_driver_path("chromedriver")
                if driver_path:
                    service = ChromeService(executable_path=driver_path)
                    self.driver = webdriver.Chrome(service=service, options=options)
                else:
                    self.driver = webdriver.Chrome(options=options)
            else:
                driver_path = self._get_driver_path("geckodriver")
                if driver_path:
                    service = FirefoxService(executable_path=driver_path)
                    self.driver = webdriver.Firefox(service=service, options=options)
                else:
                    self.driver = webdriver.Firefox(options=options)
            
            self.tab_handles = [self.driver.current_window_handle]
            
            if url:
                self.navigate(url)
            
            return {
                "status": "success",
                "message": f"{self.browser_type.capitalize()} lance",
                "url": url or "about:blank"
            }
        except Exception as e:
            logger.error(f"Erreur lancement: {e}")
            return {"status": "error", "message": str(e)}
    
    def close_browser(self) -> Dict[str, Any]:
        """Ferme le navigateur."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            self.tab_handles = []
            return {"status": "success", "message": "Navigateur ferme"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # NAVIGATION
    # =========================================================================
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigue vers une URL."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            self.driver.get(url)
            self.current_url = url
            return {"status": "success", "url": url, "title": self.driver.title}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def go_back(self) -> Dict[str, Any]:
        """Retourne a la page precedente."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.back()
            time.sleep(0.5)
            return {"status": "success", "url": self.driver.current_url}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def go_forward(self) -> Dict[str, Any]:
        """Avance vers la page suivante."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.forward()
            time.sleep(0.5)
            return {"status": "success", "url": self.driver.current_url}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def refresh(self) -> Dict[str, Any]:
        """Rafraichit la page."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.refresh()
            return {"status": "success", "message": "Page rafraichie"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # INFORMATIONS
    # =========================================================================
    
    def get_page_info(self) -> Dict[str, Any]:
        """Recupere les informations de la page."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            return {
                "status": "success",
                "url": self.driver.current_url,
                "title": self.driver.title,
                "tabs_count": len(self.tab_handles)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_page_source(self) -> Dict[str, Any]:
        """Recupere le code HTML."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            return {
                "status": "success",
                "html": self.driver.page_source,
                "url": self.driver.current_url
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_cookies(self) -> Dict[str, Any]:
        """Recupere tous les cookies."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            cookies = self.driver.get_cookies()
            return {"status": "success", "cookies": cookies, "count": len(cookies)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # ELEMENT: TROUVE
    # =========================================================================
    
    def find_element(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Trouve un element par selecteur."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
                "link": By.LINK_TEXT,
                "partial": By.PARTIAL_LINK_TEXT
            }
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            
            return {
                "status": "success",
                "tag": element.tag_name,
                "text": element.text[:200] if element.text else "",
                "is_displayed": element.is_displayed(),
                "is_enabled": element.is_enabled()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def find_elements(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Trouve tous les elements correspondant."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID, "name": By.NAME}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            elements = self.driver.find_elements(by_type, selector)
            
            return {
                "status": "success",
                "count": len(elements),
                "elements": [{"tag": e.tag_name, "text": e.text[:50]} for e in elements[:10]]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # ELEMENT: CLIC
    # =========================================================================
    
    def click(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Clique sur un element."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID, "name": By.NAME}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by_type, selector))
            )
            element.click()
            return {"status": "success", "message": f"Clic sur {selector}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def double_click(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Double clic sur un element."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            
            ActionChains(self.driver).double_click(element).perform()
            return {"status": "success", "message": f"Double clic sur {selector}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def right_click(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Clic droit sur un element."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            
            ActionChains(self.driver).context_click(element).perform()
            return {"status": "success", "message": f"Clic droit sur {selector}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def hover(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Survole un element."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            
            ActionChains(self.driver).move_to_element(element).perform()
            return {"status": "success", "message": f"Survol de {selector}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # ELEMENT: SAISIE
    # =========================================================================
    
    def fill(self, selector: str, value: str, by: str = "css", clear: bool = True) -> Dict[str, Any]:
        """Remplit un champ de saisie."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID, "name": By.NAME}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by_type, selector))
            )
            
            if clear:
                element.clear()
            
            element.send_keys(value)
            return {"status": "success", "message": f"Saisie dans {selector}: {value}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def clear_input(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Efface un champ de saisie."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID, "name": By.NAME}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            element.clear()
            return {"status": "success", "message": f"Champ {selector} efface"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def type_keys(self, keys: str) -> Dict[str, Any]:
        """Envoie des touches clavier globales."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.switch_to.active_element.send_keys(keys)
            return {"status": "success", "message": f"Touches: {keys}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def press_key(self, key: str) -> Dict[str, Any]:
        """Appuie sur une touche speciale."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            key_map = {
                "enter": Keys.ENTER,
                "tab": Keys.TAB,
                "escape": Keys.ESCAPE,
                "backspace": Keys.BACKSPACE,
                "delete": Keys.DELETE,
                "home": Keys.HOME,
                "end": Keys.END,
                "page_up": Keys.PAGE_UP,
                "page_down": Keys.PAGE_DOWN,
                "up": Keys.ARROW_UP,
                "down": Keys.ARROW_DOWN,
                "left": Keys.ARROW_LEFT,
                "right": Keys.ARROW_RIGHT,
                "control": Keys.CONTROL,
                "alt": Keys.ALT,
                "shift": Keys.SHIFT
            }
            
            key_obj = key_map.get(key.lower())
            if key_obj:
                ActionChains(self.driver).send_keys(key_obj).perform()
                return {"status": "success", "message": f"Touche: {key}"}
            return {"status": "error", "message": f"Touche inconnue: {key}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # ELEMENT: SELECTION
    # =========================================================================
    
    def select_dropdown(self, selector: str, value: str = None, text: str = None, 
                       index: int = None, by: str = "css") -> Dict[str, Any]:
        """Selectionne dans une liste deroulante."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID, "name": By.NAME}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            select = Select(element)
            
            if value is not None:
                select.select_by_value(value)
            elif text is not None:
                select.select_by_visible_text(text)
            elif index is not None:
                select.select_by_index(index)
            else:
                return {"status": "error", "message": "Specifier value, text ou index"}
            
            return {"status": "success", "message": f"Selection dans {selector}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def checkbox(self, selector: str, action: str = "check", by: str = "css") -> Dict[str, Any]:
        """Coche ou decoche une case a cocher."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            
            is_checked = element.is_selected()
            if action == "check" and not is_checked:
                element.click()
            elif action == "uncheck" and is_checked:
                element.click()
            
            return {"status": "success", "message": f"Checkbox {action}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # ELEMENT: ATTRIBUTS ET TEXTE
    # =========================================================================
    
    def get_text(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Recupere le texte d'un element."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID, "name": By.NAME}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            
            return {"status": "success", "text": element.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_attribute(self, selector: str, attribute: str, by: str = "css") -> Dict[str, Any]:
        """Recupere l'attribut d'un element."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            
            value = element.get_attribute(attribute)
            return {"status": "success", "attribute": attribute, "value": value}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # SCROLL
    # =========================================================================
    
    def scroll(self, pixels: int, direction: str = "down") -> Dict[str, Any]:
        """Defile dans la page."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            scroll_amount = pixels if direction == "down" else -pixels
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            return {"status": "success", "scrolled": scroll_amount}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def scroll_to_top(self) -> Dict[str, Any]:
        """Defile jusqu'en haut."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            return {"status": "success", "message": "Haut de page"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def scroll_to_bottom(self) -> Dict[str, Any]:
        """Defile jusqu'en bas."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            return {"status": "success", "message": "Bas de page"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def scroll_to_element(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Defile jusqu'a un element."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            return {"status": "success", "message": "Defile vers element"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # ONGLETS
    # =========================================================================
    
    def new_tab(self, url: Optional[str] = None) -> Dict[str, Any]:
        """Ouvre un nouvel onglet."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.tab_handles = list(self.driver.window_handles)
            
            if url:
                self.navigate(url)
            
            return {"status": "success", "tabs": len(self.tab_handles)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def switch_tab(self, index: int) -> Dict[str, Any]:
        """Bascule vers un onglet."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            handles = self.driver.window_handles
            if 0 <= index < len(handles):
                self.driver.switch_to.window(handles[index])
                self.tab_handles = handles
                return {"status": "success", "current_url": self.driver.current_url}
            return {"status": "error", "message": f"Onglet {index} inexistant"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def close_tab(self) -> Dict[str, Any]:
        """Ferme l'onglet courant."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            handles = self.driver.window_handles
            if len(handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(handles[0])
                self.tab_handles = list(self.driver.window_handles)
                return {"status": "success", "tabs": len(self.tab_handles)}
            else:
                return {"status": "warning", "message": "Dernier onglet"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # CAPTCHA ET ALERTES
    # =========================================================================
    
    def accept_alert(self) -> Dict[str, Any]:
        """Accepte une alerte."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.switch_to.alert.accept()
            return {"status": "success", "message": "Alerte acceptee"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def dismiss_alert(self) -> Dict[str, Any]:
        """Rejette une alerte."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.switch_to.alert.dismiss()
            return {"status": "success", "message": "Alerte rejetee"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_alert_text(self) -> Dict[str, Any]:
        """Recupere le texte d'une alerte."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            alert = self.driver.switch_to.alert
            text = alert.text
            return {"status": "success", "text": text}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # AUTRES
    # =========================================================================
    
    def take_screenshot(self, path: str = "/tmp/sharinganscreenshot.png") -> Dict[str, Any]:
        """Prend une capture d'ecran."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.save_screenshot(path)
            return {"status": "success", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def execute_js(self, script: str) -> Dict[str, Any]:
        """Execute du JavaScript."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            result = self.driver.execute_script(script)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def upload_file(self, selector: str, file_path: str, by: str = "css") -> Dict[str, Any]:
        """Upload un fichier."""
        if not self.driver:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            element.send_keys(file_path)
            return {"status": "success", "message": f"Fichier upload: {file_path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def wait(self, seconds: float) -> Dict[str, Any]:
        """Attend un nombre de secondes."""
        time.sleep(seconds)
        return {"status": "success", "waited": seconds}


def get_browser_controller(browser: str = "chrome", headless: bool = False) -> BrowserController:
    """Factory function."""
    return BrowserController(browser=browser, headless=headless)


if __name__ == "__main__":
    print("=" * 70)
    print("  Sharingan Browser Controller - Test Complet")
    print("=" * 70)
    print()
    
    ctrl = get_browser_controller(headless=False)
    
    print("Lancement de Chrome vers YouTube...")
    result = ctrl.launch_browser("https://www.youtube.com")
    print(f"  -> {result['status']}")
    
    if result['status'] == 'success':
        print()
        print("Navigateur ouvert! Methodes disponibles:")
        methods = [m for m in dir(ctrl) if not m.startswith('_') and callable(getattr(ctrl, m))]
        for m in sorted(methods):
            print(f"  - {m}")
        
        ctrl.close_browser()
