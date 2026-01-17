#!/usr/bin/env python3
"""
Sharingan OS - Browser Controller Module
Automation de navigateur avec Selenium pour control complet.
Supporte Firefox et Chrome avec ou sans affichage.
"""

import os
import subprocess
import shutil
import tempfile
import logging
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger("sharingan.browser")

SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    logger.warning("Selenium non installe. pip install selenium")


class BrowserController:
    """
    Controleur de navigateur pour Sharingan OS.
    Supporte Firefox et Chrome avec Selenium.
    
    Caracteristiques:
    - Gestion automatique Xvfb avec pyvirtualdisplay
    - Support root avec hacks necessaires
    - Navigation, clics, formulaires, screenshots
    - Gestion des onglets multiples
    """

    def __init__(self, browser: str = "firefox", headless: bool = False, 
                 visible: bool = False, width: int = 1920, height: int = 1080):
        self.driver: Optional[Any] = None
        self.browser_type = browser.lower()
        self.headless = headless
        self.visible = visible
        self.width = width
        self.height = height
        self.current_url = ""
        self.tab_handles: List[str] = []
        
        self.vdisplay = None
        self.original_display = None
        self.original_home = None
        self.xvfb_started = False
        
    def _setup_environment(self) -> bool:
        """
        Configure l'environnement pour le navigateur.
        Gere le probleme root et l'affichage X11.
        """
        self.original_display = os.environ.get("DISPLAY")
        self.original_home = os.environ.get("HOME")
        
        if os.environ.get("DISPLAY"):
            logger.info(f"Display deja configure: {os.environ.get('DISPLAY')}")
            return True
        
        try:
            from pyvirtualdisplay import Display
            self.vdisplay = Display(visible=0, size=(self.width, self.height))
            self.vdisplay.start()
            self.xvfb_started = True
            logger.info(f"Xvfb demarre sur display {os.environ.get('DISPLAY')}")
            return True
        except ImportError:
            logger.warning("pyvirtualdisplay non disponible, tentative avec Xvfb manuel")
        except Exception as e:
            logger.warning(f"Erreur pyvirtualdisplay: {e}")
        
        try:
            subprocess.run(["Xvfb", ":99", "-screen", "0", f"{self.width}x{self.height}x24"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            os.environ["DISPLAY"] = ":99"
            self.xvfb_started = True
            logger.info("Xvfb manuel demarre sur :99")
            return True
        except Exception as e:
            logger.error(f"Erreur demarrage Xvfb: {e}")
            return False

    def _fix_root_environment(self):
        """
        Corrige les problemes d'execution en tant que root.
        """
        if os.geteuid() == 0:
            logger.info("Execution en tant que root - application des correctifs")
            
            os.environ["MOZ_ALLOW_NON_ADMIN_XAUTH"] = "1"
            os.environ["MOZ_DISABLE_CONTENT_SANDBOX"] = "1"
            
            if not os.environ.get("HOME") or not os.path.exists(os.environ["HOME"]):
                temp_home = tempfile.mkdtemp(prefix="sharingan_browser_")
                os.environ["HOME"] = temp_home
                logger.info(f"HOME temporaire pour root: {temp_home}")
            
            subprocess.run(["xhost", "+SI:localuser:root"], 
                          capture_output=True, check=False)

    def _get_driver_path(self, driver_name: str) -> Optional[str]:
        """Retourne le chemin du driver (geckodriver/chromedriver)."""
        paths = [
            f"/usr/local/bin/{driver_name}",
            f"/usr/bin/{driver_name}",
            str(Path.home() / ".local" / "bin" / driver_name)
        ]
        for p in paths:
            if Path(p).exists():
                return p
        return shutil.which(driver_name)

    def launch_browser(self, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Lance le navigateur et optionnellement navigue vers une URL.
        
        Args:
            url: URL optionnelle vers laquelle naviguer au demarrage
            
        Returns:
            Dict avec le statut et les informations
        """
        if not SELENIUM_AVAILABLE:
            return {"status": "error", "message": "Selenium non installe", 
                   "solution": "pip install selenium"}
        
        try:
            self._setup_environment()
            self._fix_root_environment()
            
            if self.browser_type == "firefox":
                return self._launch_firefox(url)
            else:
                return self._launch_chrome(url)
                
        except Exception as e:
            logger.error(f"Erreur lancement navigateur: {e}")
            return {"status": "error", "message": str(e)}

    def _launch_firefox(self, url: Optional[str]) -> Dict[str, Any]:
        """Lance Firefox avec Selenium."""
        try:
            options = FirefoxOptions()
            
            if self.headless:
                options.add_argument("--headless")
            
            if not self.visible and not os.environ.get("DISPLAY"):
                options.add_argument("--headless")
            
            options.add_argument(f"--width={self.width}")
            options.add_argument(f"--height={self.height}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-default-apps")
            options.add_argument("--no-first-run")
            options.add_argument("--new-instance")
            
            options.set_preference("browser.startup.homepage", "about:blank")
            options.set_preference("datareporting.policy.dataSubmissionEnabled", False)
            options.set_preference("browser.tabs.remote.autostart", False)
            
            driver_path = self._get_driver_path("geckodriver")
            
            if driver_path:
                service = FirefoxService(executable_path=driver_path)
                self.driver = webdriver.Firefox(service=service, options=options)
            else:
                self.driver = webdriver.Firefox(options=options)
            
            self.tab_handles = [self.driver.current_window_handle]
            
            if url:
                self.driver.get(url)
                self.current_url = url
            
            return {
                "status": "success",
                "browser": "Firefox",
                "message": "Firefox lance avec succes",
                "url": url or "about:blank",
                "headless": self.headless or not self.visible
            }
            
        except Exception as e:
            logger.error(f"Erreur Firefox: {e}")
            return {"status": "error", "message": str(e), "browser": "Firefox"}

    def _launch_chrome(self, url: Optional[str]) -> Dict[str, Any]:
        """Lance Chrome avec Selenium."""
        try:
            options = ChromeOptions()
            
            if self.headless:
                options.add_argument("--headless=new")
            
            if not self.visible and not os.environ.get("DISPLAY"):
                options.add_argument("--headless=new")
            
            options.add_argument(f"--window-size={self.width},{self.height}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-sync")
            options.add_argument("--no-first-run")
            options.add_argument("--no-zygote")
            options.add_argument("--disable-logging")
            options.add_argument("--remote-debugging-port=9222")
            
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            driver_path = self._get_driver_path("chromedriver")
            
            if driver_path:
                service = ChromeService(executable_path=driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            
            self.tab_handles = [self.driver.current_window_handle]
            
            if url:
                self.driver.get(url)
                self.current_url = url
            
            return {
                "status": "success",
                "browser": "Chrome",
                "message": "Chrome lance avec succes",
                "url": url or "about:blank",
                "headless": self.headless or not self.visible
            }
            
        except Exception as e:
            logger.error(f"Erreur Chrome: {e}")
            return {"status": "error", "message": str(e), "browser": "Chrome"}

    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigue vers une URL."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            self.driver.get(url)
            self.current_url = url
            return {"status": "success", "url": url, "title": self.driver.title}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_page_info(self) -> Dict[str, Any]:
        """Recupere les informations de la page courante."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            return {
                "status": "success",
                "url": self.driver.current_url,
                "title": self.driver.title,
                "page_source_length": len(self.driver.page_source),
                "tabs_count": len(self.tab_handles)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_page_source(self) -> Dict[str, Any]:
        """Retourne le code HTML de la page."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            return {
                "status": "success",
                "html": self.driver.page_source,
                "url": self.driver.current_url
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def find_element(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Trouve un element sur la page."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, 
                     "id": By.ID, "name": By.NAME, "class": By.CLASS_NAME}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by_type, selector))
            )
            
            return {
                "status": "success",
                "tag_name": element.tag_name,
                "text": element.text[:200] if element.text else "",
                "is_displayed": element.is_displayed()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def click_element(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Clique sur un element."""
        if self.driver is None:
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

    def fill_form(self, selector: str, value: str, by: str = "css") -> Dict[str, Any]:
        """Remplit un champ de formulaire."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH, "id": By.ID, "name": By.NAME}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by_type, selector))
            )
            element.clear()
            element.send_keys(value)
            return {"status": "success", "message": f"Champ {selector} rempli"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def new_tab(self, url: Optional[str] = None) -> Dict[str, Any]:
        """Ouvre un nouvel onglet."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.tab_handles = list(self.driver.window_handles)
            
            if url:
                self.navigate(url)
            
            return {"status": "success", "tabs_count": len(self.tab_handles)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def switch_to_tab(self, index: int) -> Dict[str, Any]:
        """Bascule vers un onglet specifique."""
        if self.driver is None:
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

    def take_screenshot(self, path: str = "/tmp/sharingan_browser.png") -> Dict[str, Any]:
        """Prend une capture d'ecran."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            self.driver.save_screenshot(path)
            return {"status": "success", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute_js(self, script: str) -> Dict[str, Any]:
        """Execute du JavaScript."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            result = self.driver.execute_script(script)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def scroll(self, pixels: int, direction: str = "down") -> Dict[str, Any]:
        """Defile dans la page."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        
        try:
            scroll_amount = pixels if direction == "down" else -pixels
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            return {"status": "success", "scrolled": scroll_amount}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def close_browser(self) -> Dict[str, Any]:
        """Ferme le navigateur et libere les ressources."""
        try:
            if self.driver is not None:
                self.driver.quit()
                self.driver = None
            
            if self.vdisplay is not None:
                self.vdisplay.stop()
                self.vdisplay = None
            
            if self.original_home:
                os.environ["HOME"] = self.original_home
            
            self.tab_handles = []
            return {"status": "success", "message": "Navigateur ferme"}
            
        except Exception as e:
            logger.error(f"Erreur fermeture: {e}")
            return {"status": "error", "message": str(e)}

    def scroll_down(self, pixels: int = 500) -> Dict[str, Any]:
        """Defile vers le bas de la page."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        try:
            self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            return {"status": "success", "scrolled": pixels}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def scroll_up(self, pixels: int = 500) -> Dict[str, Any]:
        """Defile vers le haut de la page."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        try:
            self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            return {"status": "success", "scrolled": -pixels}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def scroll_to_top(self) -> Dict[str, Any]:
        """Retourne en haut de la page."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            return {"status": "success", "scrolled": "top"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def scroll_to_bottom(self) -> Dict[str, Any]:
        """Defile jusqu'en bas de la page."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            return {"status": "success", "scrolled": "bottom"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_element_by_selector(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Trouve et retourne un element par selecteur."""
        if self.driver is None:
            return {"status": "error", "message": "Navigateur non ouvert"}
        try:
            by_map = {"css": By.CSS_SELECTOR, "xpath": By.XPATH,
                     "id": By.ID, "name": By.NAME, "class": By.CLASS_NAME}
            by_type = by_map.get(by, By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            return {
                "status": "success",
                "tag_name": element.tag_name,
                "text": element.text[:200] if element.text else "",
                "is_displayed": element.is_displayed(),
                "is_enabled": element.is_enabled()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


def get_browser_controller(browser: str = "firefox", headless: bool = False,
                          visible: bool = False) -> BrowserController:
    """Factory function pour creer un BrowserController."""
    return BrowserController(browser=browser, headless=headless, visible=visible)


if __name__ == "__main__":
    print("=== Test Browser Controller ===")
    
    ctrl = get_browser_controller(browser="chrome", headless=True)
    
    result = ctrl.launch_browser("https://example.com")
    print(f"1. Launch: {result['status']} - {result.get('message', '')}")
    
    if result['status'] == 'success':
        info = ctrl.get_page_info()
        print(f"2. Page title: {info.get('title', 'N/A')}")
        
        source = ctrl.get_page_source()
        html_len = len(source.get('html', '')) if source.get('html') else 0
        print(f"3. HTML length: {html_len} chars")
        
        ss = ctrl.take_screenshot("/tmp/test_sharinganscreen.png")
        print(f"4. Screenshot: {ss['status']} - {ss.get('path', '')}")
        
        ctrl.close_browser()
        print("5. Browser closed")
    
    print("=== Test Complete ===")
