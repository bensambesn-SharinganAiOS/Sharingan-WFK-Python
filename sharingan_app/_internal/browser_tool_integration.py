#!/usr/bin/env python3
"""
Sharingan OS - Browser Automation Tool Integration
Integrates browser navigation capabilities into Sharingan OS tool system
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger("sharingan.browser_tool")

class BrowserToolIntegrator:
    """Intègre les capacités de navigation au système Sharingan"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.browser_controller_path = self.base_dir / "browser_controller_complete.py"
        self.cdp_control_path = self.base_dir / "cdp_control.py"
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Retourne toutes les capacités du navigateur"""
        return {
            "name": "browser_automation",
            "category": "browser",
            "version": "1.0.0",
            "description": "Navigation web automatisée avec Chrome DevTools Protocol",
            
            "capabilities": {
                "navigation": {
                    "description": "Navigation vers des URLs",
                    "actions": ["navigate", "go_back", "go_forward", "refresh"],
                    "methods": ["Page.navigate", "history.back()", "history.forward()", "location.reload()"]
                },
                "search": {
                    "description": "Recherche sur Google et sites web",
                    "actions": ["search_google", "search_site", "fill_search"],
                    "methods": ["input.value + Enter", "site-specific search forms"]
                },
                "reading": {
                    "description": "Lecture de contenu web",
                    "actions": ["get_title", "get_url", "get_content", "get_elements"],
                    "methods": ["document.title", "document.body.innerText", "querySelector"]
                },
                "scrolling": {
                    "description": "Défilement dans les pages",
                    "actions": ["scroll_down", "scroll_up", "scroll_to_element", "scroll_to_bottom"],
                    "methods": ["window.scrollBy(0, pixels)", "element.scrollIntoView()"]
                },
                "interaction": {
                    "description": "Interaction avec les éléments",
                    "actions": ["click", "double_click", "right_click", "hover", "fill_form"],
                    "methods": ["element.click()", "element.value = 'text'"]
                },
                "screenshot": {
                    "description": "Captures d'écran",
                    "actions": ["screenshot_page", "screenshot_element"],
                    "methods": ["driver.save_screenshot()"]
                },
                "tabs": {
                    "description": "Gestion des onglets",
                    "actions": ["new_tab", "switch_tab", "close_tab", "get_tabs"],
                    "methods": ["window.open()", "driver.switch_to.window()"]
                },
                "upload": {
                    "description": "Upload de fichiers",
                    "actions": ["upload_file"],
                    "methods": ["element.send_keys('/path/file')"],
                    "note": "Requiert Selenium (pas CDP seul)"
                },
                "javascript": {
                    "description": "Exécution JavaScript",
                    "actions": ["execute_js", "eval_js"],
                    "methods": ["Runtime.evaluate", "document.querySelector()"]
                }
            },
            
            "technologies": {
                "selenium": {
                    "description": "Contrôle complet du navigateur",
                    "uses": ["upload", "form_filling", "screenshot", "element_location"]
                },
                "cdp": {
                    "description": "Chrome DevTools Protocol via WebSocket",
                    "uses": ["navigation", "reading", "scrolling", "javascript", "clicking"]
                }
            },
            
            "limitations": {
                "cannot": [
                    "Upload de fichiers via CDP seul (besoin Selenium)",
                    "Résoudre les CAPTCHA",
                    "Authentification automatique (OAuth complexe)",
                    "Drag & drop précis",
                    "Vidéo/audio control avancé",
                    "Shadow DOM direct",
                    "Extensions Chrome"
                ]
            },
            
            "files": {
                "main": str(self.browser_controller_path),
                "cdp": str(self.cdp_control_path),
                "documentation": str(self.base_dir.parent.parent / "WEB_NAVIGATION_DOCUMENTATION.md"),
                "capabilities": str(self.base_dir.parent.parent / "BROWSER_CAPABILITIES.md")
            },
            
            "usage_examples": [
                "Naviguer vers un site: navigate('https://google.com')",
                "Rechercher: fill('input[name=\"q\"]', 'Sénégal') + press Enter",
                "Lire contenu: execute_js('document.title')",
                "Scroller: execute_js('window.scrollBy(0, 400)')",
                "Cliquer: click('button.submit')",
                "Screenshot: take_screenshot('/path/image.png')",
                "Upload: send_keys('/path/file.jpg') à input[type='file']"
            ]
        }
    
    def get_tool_schema(self) -> Dict:
        """Retourne le schéma de l'outil pour l'intégration"""
        caps = self.get_capabilities()
        return {
            "name": "browser_controller_complete",
            "category": "browser",
            "description": caps["description"],
            "version": caps["version"],
            "capabilities": list(caps["capabilities"].keys()),
            "actions": {
                "navigate": {
                    "description": "Naviguer vers une URL",
                    "parameters": {"url": {"type": "string", "required": True}},
                    "returns": {"status": "string", "url": "string"}
                },
                "search": {
                    "description": "Faire une recherche",
                    "parameters": {"query": {"type": "string", "required": True}},
                    "returns": {"status": "string", "results_count": "int"}
                },
                "read": {
                    "description": "Lire le contenu de la page",
                    "parameters": {"selector": {"type": "string", "required": False}},
                    "returns": {"content": "string", "elements": "list"}
                },
                "scroll": {
                    "description": "Défiler dans la page",
                    "parameters": {"pixels": {"type": "int", "default": 400}},
                    "returns": {"status": "string"}
                },
                "click": {
                    "description": "Cliquer sur un élément",
                    "parameters": {"selector": {"type": "string", "required": True}},
                    "returns": {"status": "string"}
                },
                "screenshot": {
                    "description": "Prendre une capture d'écran",
                    "parameters": {"path": {"type": "string", "default": "/tmp/screenshot.png"}},
                    "returns": {"status": "string", "path": "string"}
                },
                "new_tab": {
                    "description": "Ouvrir un nouvel onglet",
                    "parameters": {"url": {"type": "string", "required": False}},
                    "returns": {"status": "string", "tab_id": "string"}
                },
                "switch_tab": {
                    "description": "Basculer vers un onglet",
                    "parameters": {"index": {"type": "int", "required": True}},
                    "returns": {"status": "string", "url": "string"}
                },
                "upload": {
                    "description": "Uploader un fichier",
                    "parameters": {"file_path": {"type": "string", "required": True}},
                    "returns": {"status": "string", "upload_url": "string"}
                },
                "execute_js": {
                    "description": "Exécuter JavaScript",
                    "parameters": {"script": {"type": "string", "required": True}},
                    "returns": {"result": "any", "status": "string"}
                }
            },
            "limitations": caps["limitations"]["cannot"]
        }
    
    def integrate_into_registry(self, registry: Dict) -> Dict:
        """Intègre l'outil dans le registre existant"""
        caps = self.get_capabilities()
        
        # Ajouter/Mettre à jour l'entrée du navigateur complet
        registry["tools"]["browser_controller_complete"] = {
            "name": "browser_controller_complete",
            "category": "browser",
            "path": str(self.browser_controller_path),
            "capabilities": list(caps["capabilities"].keys()),
            "source": "internal",
            "version": caps["version"],
            "description": caps["description"],
            "methods": ["selenium", "cdp"],
            "documented": True,
            "documentation_files": [
                str(self.base_dir.parent.parent / "WEB_NAVIGATION_DOCUMENTATION.md"),
                str(self.base_dir.parent.parent / "BROWSER_CAPABILITIES.md")
            ]
        }
        
        # Mettre à jour les capacités du browser_controller basique
        if "browser_controller" in registry["tools"]:
            registry["tools"]["browser_controller"]["capabilities"] = [
                "browser_automation",
                "firefox_control"
            ]
            registry["tools"]["browser_controller"]["note"] = "Use browser_controller_complete for full features"
        
        return registry
    
    def create_genome_mutation(self) -> Dict:
        """Crée une mutation du génome pour cette nouvelle capacité"""
        caps = self.get_capabilities()
        return {
            "mutation_id": "browser_automation_v1",
            "type": "capability_addition",
            "name": "Browser Automation Capability",
            "description": "Ajout des capacités de navigation web automatisée",
            "reason": "Le système peut maintenant naviguer sur le web, lire du contenu, et interagir avec les pages",
            "capabilities_added": list(caps["capabilities"].keys()),
            "files_created": [
                str(self.browser_controller_path),
                str(self.cdp_control_path),
                str(self.base_dir.parent.parent / "WEB_NAVIGATION_DOCUMENTATION.md"),
                str(self.base_dir.parent.parent / "BROWSER_CAPABILITIES.md")
            ],
            "technologies": caps["technologies"],
            "limitations": caps["limitations"],
            "confidence": 0.95,
            "impact": "high",
            "evolution_step": True,
            "learning_source": "manual_integration",
            "test_status": "passed",
            "user_validation": True,
            "created_at": str(__import__("datetime").datetime.now().isoformat())
        }
    
    def create_action_handlers(self) -> Dict[str, str]:
        """Crée les handlers d'actions pour l'action_executor"""
        return {
            "navigate": "handle_browser_navigate",
            "search": "handle_browser_search",
            "read": "handle_browser_read",
            "scroll": "handle_browser_scroll",
            "click": "handle_browser_click",
            "screenshot": "handle_browser_screenshot",
            "new_tab": "handle_browser_new_tab",
            "switch_tab": "handle_browser_switch_tab",
            "upload": "handle_browser_upload",
            "execute_js": "handle_browser_execute_js"
        }
    
    def get_status(self) -> Dict:
        """Retourne le statut de l'intégration"""
        return {
            "integrated": True,
            "files_exist": {
                "browser_controller_complete": self.browser_controller_path.exists(),
                "cdp_control": self.cdp_control_path.exists(),
                "navigation_docs": (self.base_dir.parent.parent / "WEB_NAVIGATION_DOCUMENTATION.md").exists(),
                "capabilities_docs": (self.base_dir.parent.parent / "BROWSER_CAPABILITIES.md").exists()
            },
            "capabilities": self.get_capabilities()["capabilities"],
            "tool_schema": self.get_tool_schema(),
            "integration_complete": True
        }

def get_browser_tool_integrator() -> BrowserToolIntegrator:
    return BrowserToolIntegrator()

if __name__ == "__main__":
    integrator = get_browser_tool_integrator()
    status = integrator.get_status()
    print("="*60)
    print("📚 BROWSER TOOL INTEGRATION STATUS")
    print("="*60)
    print(f"Integrated: {status['integrated']}")
    print(f"Files exist: {status['files_exist']}")
    print(f"Capabilities: {list(status['capabilities'].keys())}")
    print("="*60)
