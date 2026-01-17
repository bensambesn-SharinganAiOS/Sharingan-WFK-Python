#!/usr/bin/env python3
"""
Sharingan OS - Browser Manager
Gestionnaire de navigateurs persistants avec support multi-sessions.
Permet de garder les navigateurs ouverts et de les reutiliser.
"""

import os
import json
import time
import uuid
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("sharingan.browser_manager")

try:
    from browser_controller import get_browser_controller
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("browser_controller non disponible")


class BrowserManager:
    """
    Gestionnaire de navigateurs pour Sharingan OS.
    
    Fonctionnalites:
    - Multiples navigateurs simultanes
    - Sessions persistantes
    - Nommer les navigateurs
    - Basculer entre navigateurs
    - Fermer sans perdre l'etat
    """
    
    def __init__(self):
        self.browsers: Dict[str, Dict] = {}  # browser_id -> browser info
        self.active_browser_id: Optional[str] = None
        self.state_file = Path("/tmp/sharingan_browser_manager_state.json")
        self._load_state()
    
    def _load_state(self):
        """Charge l'etat depuis le fichier."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.browsers = data.get('browsers', {})
                    self.active_browser_id = data.get('active_browser_id')
        except Exception as e:
            logger.warning(f"Impossible de charger l'etat: {e}")
    
    def _save_state(self):
        """Sauvegarde l'etat dans le fichier."""
        try:
            data = {
                'browsers': self.browsers,
                'active_browser_id': self.active_browser_id,
                'last_update': datetime.now().isoformat()
            }
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Impossible de sauvegarder l'etat: {e}")
    
    def launch(self, name: Optional[str] = None, url: Optional[str] = None,
               browser: str = "chrome", headless: bool = False) -> Dict[str, Any]:
        """
        Lance un nouveau navigateur.
        
        Args:
            name: Nom pour identifier le navigateur (genere si non fourni)
            url: URL optionnelle d'ouverture
            browser: 'chrome' ou 'firefox'
            headless: Mode sans affichage
            
        Returns:
            Dict avec les informations du navigateur lance
        """
        if not SELENIUM_AVAILABLE:
            return {"status": "error", "message": "Module browser_controller non disponible"}
        
        browser_id = name or f"browser_{uuid.uuid4().hex[:8]}"
        
        # Verifier si un navigateur avec ce nom existe deja
        for bid, binfo in self.browsers.items():
            if binfo.get('name') == name and binfo.get('active', False):
                return {
                    "status": "warning",
                    "message": f"Un navigateur '{name}' existe deja",
                    "browser_id": bid,
                    "action": "use switch_browser() pour basculer"
                }
        
        try:
            # Creer le controleur de navigateur
            controller = get_browser_controller(browser=browser, headless=headless)
            
            # Lancer le navigateur
            result = controller.launch_browser(url)
            
            if result['status'] != 'success':
                return {
                    "status": "error",
                    "message": result.get('message', 'Erreur lancement'),
                    "details": result
                }
            
            # Enregistrer le navigateur
            browser_info = {
                'id': browser_id,
                'name': name or browser_id,
                'browser': browser,
                'headless': headless,
                'controller': controller,
                'current_url': url or 'about:blank',
                'created_at': datetime.now().isoformat(),
                'active': True
            }
            
            self.browsers[browser_id] = browser_info
            self.active_browser_id = browser_id
            self._save_state()
            
            return {
                "status": "success",
                "message": f"Navigateur '{name or browser_id}' lance avec succes",
                "browser_id": browser_id,
                "name": name or browser_id,
                "url": url or 'about:blank',
                "browsers_count": len(self.browsers)
            }
            
        except Exception as e:
            logger.error(f"Erreur lancement navigateur: {e}")
            return {"status": "error", "message": str(e)}
    
    def switch(self, browser_id: str) -> Dict[str, Any]:
        """
        Bascule vers un navigateur specifique.
        
        Args:
            browser_id: ID du navigateur cible
            
        Returns:
            Dict avec le resultat
        """
        if browser_id not in self.browsers:
            return {
                "status": "error",
                "message": f"Navigateur '{browser_id}' non trouve",
                "available_ids": list(self.browsers.keys())
            }
        
        # Desactiver l'ancien navigateur actif
        if self.active_browser_id:
            self.browsers[self.active_browser_id]['active'] = False
        
        # Activer le nouveau
        self.browsers[browser_id]['active'] = True
        self.active_browser_id = browser_id
        self._save_state()
        
        info = self.browsers[browser_id]
        return {
            "status": "success",
            "message": f"Bascule vers '{info.get('name', browser_id)}'",
            "browser_id": browser_id,
            "name": info.get('name'),
            "current_url": info.get('current_url')
        }
    
    def use(self, name: str) -> Dict[str, Any]:
        """
        Bascule vers un navigateur par son nom.
        """
        for bid, binfo in self.browsers.items():
            if binfo.get('name') == name:
                return self.switch(bid)
        
        return {
            "status": "error",
            "message": f"Navigateur '{name}' non trouve",
            "available_names": [binfo.get('name') for binfo in self.browsers.values()]
        }
    
    def list(self) -> Dict[str, Any]:
        """
        Liste tous les navigateurs.
        """
        browsers_list = []
        for bid, binfo in self.browsers.items():
            ctrl = binfo.get('controller')
            if ctrl and ctrl.driver:
                try:
                    current_url = ctrl.driver.current_url
                except:
                    current_url = binfo.get('current_url', 'unknown')
            else:
                current_url = binfo.get('current_url', 'closed')
            
            browsers_list.append({
                'id': bid,
                'name': binfo.get('name', bid),
                'browser': binfo.get('browser'),
                'status': 'active' if binfo.get('active') else 'inactive',
                'current_url': current_url,
                'created_at': binfo.get('created_at', '')
            })
        
        return {
            "status": "success",
            "browsers": browsers_list,
            "active_browser_id": self.active_browser_id,
            "total": len(browsers_list)
        }
    
    def get_active(self) -> Dict[str, Any]:
        """
        Retourne les informations du navigateur actif.
        """
        if not self.active_browser_id:
            return {
                "status": "error",
                "message": "Aucun navigateur actif",
                "hint": "Lancez un navigateur avec browser_manager.launch()"
            }
        
        if self.active_browser_id not in self.browsers:
            return {
                "status": "error",
                "message": "Navigateur actif non trouve",
                "hint": "Lancez un navigateur avec browser_manager.launch()"
            }
        
        binfo = self.browsers[self.active_browser_id]
        return {
            "status": "success",
            "browser_id": self.active_browser_id,
            "name": binfo.get('name'),
            "browser": binfo.get('browser'),
            "current_url": binfo.get('current_url')
        }
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigue vers une URL avec le navigateur actif.
        """
        active = self.get_active()
        if active['status'] != 'success':
            return active
        
        browser_id = active['browser_id']
        ctrl = self.browsers[browser_id]['controller']
        
        try:
            result = ctrl.navigate(url)
            if result['status'] == 'success':
                self.browsers[browser_id]['current_url'] = url
                self._save_state()
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def execute_js(self, script: str) -> Dict[str, Any]:
        """
        Execute JavaScript dans le navigateur actif.
        """
        active = self.get_active()
        if active['status'] != 'success':
            return active
        
        browser_id = active['browser_id']
        ctrl = self.browsers[browser_id]['controller']
        
        try:
            return ctrl.execute_js(script)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def fill(self, selector: str, value: str, by: str = "css") -> Dict[str, Any]:
        """
        Remplit un champ de formulaire.
        """
        active = self.get_active()
        if active['status'] != 'success':
            return active
        
        browser_id = active['browser_id']
        ctrl = self.browsers[browser_id]['controller']
        
        try:
            return ctrl.fill_form(selector, value, by=by)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def click(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """
        Clique sur un element.
        """
        active = self.get_active()
        if active['status'] != 'success':
            return active
        
        browser_id = active['browser_id']
        ctrl = self.browsers[browser_id]['controller']
        
        try:
            return ctrl.click_element(selector, by=by)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def screenshot(self, path: Optional[str] = None) -> Dict[str, Any]:
        """
        Prend une capture d'ecran.
        """
        active = self.get_active()
        if active['status'] != 'success':
            return active
        
        browser_id = active['browser_id']
        ctrl = self.browsers[browser_id]['controller']
        
        if path is None:
            timestamp = int(time.time())
            path = f"/tmp/screenshot_{active.get('name', browser_id)}_{timestamp}.png"
        
        try:
            return ctrl.take_screenshot(path)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_page_info(self) -> Dict[str, Any]:
        """
        Recupere les informations de la page courante.
        """
        active = self.get_active()
        if active['status'] != 'success':
            return active
        
        browser_id = active['browser_id']
        ctrl = self.browsers[browser_id]['controller']
        
        try:
            return ctrl.get_page_info()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_page_source(self) -> Dict[str, Any]:
        """
        Recupere le code source de la page.
        """
        active = self.get_active()
        if active['status'] != 'success':
            return active
        
        browser_id = active['browser_id']
        ctrl = self.browsers[browser_id]['controller']
        
        try:
            return ctrl.get_page_source()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def scroll(self, pixels: int = 500, direction: str = "down") -> Dict[str, Any]:
        """
        Defile dans la page.
        """
        active = self.get_active()
        if active['status'] != 'success':
            return active
        
        browser_id = active['browser_id']
        ctrl = self.browsers[browser_id]['controller']
        
        try:
            if direction == "down":
                return ctrl.scroll_down(pixels)
            return ctrl.scroll_up(pixels)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def new_tab(self, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Ouvre un nouvel onglet.
        """
        active = self.get_active()
        if active['status'] != 'success':
            return active
        
        browser_id = active['browser_id']
        ctrl = self.browsers[browser_id]['controller']
        
        try:
            return ctrl.new_tab(url)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def close(self, browser_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ferme un navigateur specifique ou le navigateur actif.
        """
        target_id = browser_id or self.active_browser_id
        
        if not target_id or target_id not in self.browsers:
            return {"status": "error", "message": "Navigateur non trouve"}
        
        binfo = self.browsers[target_id]
        ctrl = binfo.get('controller')
        
        try:
            if ctrl:
                ctrl.close_browser()
        except Exception as e:
            logger.warning(f"Erreur fermeture navigateur: {e}")
        
        name = binfo.get('name', target_id)
        del self.browsers[target_id]
        
        if self.active_browser_id == target_id:
            self.active_browser_id = None
            
            # Activer un autre navigateur si disponible
            if self.browsers:
                next_id = next(iter(self.browsers.keys()))
                self.browsers[next_id]['active'] = True
                self.active_browser_id = next_id
        
        self._save_state()
        
        return {
            "status": "success",
            "message": f"Navigateur '{name}' ferme",
            "remaining_browsers": len(self.browsers)
        }
    
    def close_all(self) -> Dict[str, Any]:
        """
        Ferme tous les navigateurs.
        """
        closed = 0
        for browser_id in list(self.browsers.keys()):
            result = self.close(browser_id)
            if result['status'] == 'success':
                closed += 1
        
        return {
            "status": "success",
            "message": f"{closed} navigateur(s) ferme(s)",
            "remaining": len(self.browsers)
        }
    
    def wait(self, seconds: float) -> Dict[str, Any]:
        """
        Attend pendant le nombre de secondes specifie.
        Utisepour laisser le temps de voir la page.
        """
        time.sleep(seconds)
        return {"status": "success", "waited": seconds}


# Instance globale du gestionnaire
browser_manager = BrowserManager()


def get_browser_manager() -> BrowserManager:
    """Retourne l'instance globale du BrowserManager."""
    return browser_manager


if __name__ == "__main__":
    print("=" * 60)
    print("  Sharingan Browser Manager - Mode interactif")
    print("=" * 60)
    print()
    print("Commandes disponibles:")
    print("  launch([name], [url], [browser], [headless])")
    print("  list()")
    print("  switch(id) / use(name)")
    print("  active()")
    print("  navigate(url)")
    print("  execute_js(script)")
    print("  fill(selector, value)")
    print("  click(selector)")
    print("  screenshot([path])")
    print("  scroll(pixels, direction)")
    print("  screenshot([path])")
    print("  new_tab([url])")
    print("  close([id])")
    print("  close_all()")
    print("  wait(seconds)")
    print()
    print("Exemple:")
    print("  bm = get_browser_manager()")
    print("  bm.launch('youtube', 'https://youtube.com', 'chrome')")
    print("  bm.wait(3)")
    print("  bm.list()")
    print()
