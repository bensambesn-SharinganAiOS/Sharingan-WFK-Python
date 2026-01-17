#!/usr/bin/env python3
"""
System Screenshot Module - Capture d'écran du système hote
Auto-detection des outils disponibles, choix automatique du meilleur
Supporte: Desktop complet, fenetre specifique, zone rectangulaire, multi-ecrans
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import logging

logger = logging.getLogger("sharingan.screenshot")


class PythonScreenshot:
    """Capture d'ecran pure Python utilisant mss (multi-plateforme)"""
    
    def __init__(self):
        self.mss_available = False
        self._check_mss()
    
    def _check_mss(self) -> bool:
        try:
            import mss
            self.mss = mss
            self.mss_available = True
            logger.info("MSS (Python screenshot) disponible")
            return True
        except ImportError:
            logger.warning("MSS non installe (pip install mss)")
            return False
    
    def capture_desktop(self, output: Path) -> bool:
        """Capture le bureau complet avec mss"""
        if not self.mss_available:
            return False
        try:
            with self.mss.mss() as sct:
                sct.shot(output=str(output), mon=-1)
            return output.exists()
        except Exception as e:
            logger.error(f"MSS capture failed: {e}")
            return False
    
    def capture_area(self, output: Path, x: int, y: int, width: int, height: int) -> bool:
        """Capture une zone rectangulaire avec mss"""
        if not self.mss_available:
            return False
        try:
            monitor = {"left": x, "top": y, "width": width, "height": height}
            with self.mss.mss() as sct:
                sct.grab(monitor).save(str(output))
            return output.exists()
        except Exception as e:
            logger.error(f"MSS area capture failed: {e}")
            return False
    
    def get_monitors(self) -> List[Dict]:
        """Retourne la liste des ecrans"""
        if not self.mss_available:
            return []
        try:
            with self.mss.mss() as sct:
                return [{"left": m["left"], "top": m["top"], 
                        "width": m["width"], "height": m["height"]} 
                       for m in sct.monitors[1:]]
        except Exception:
            return []


class SystemScreenshot:
    """Gestionnaire de capture d'ecran avec auto-detection des outils"""
    
    def __init__(self):
        self.screenshots_dir = Path("/tmp/sharingan/screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        self.python_screenshot = PythonScreenshot()
        self.available_tools = self._detect_all_tools()
        self.preferred_order = self._get_preference_order()
    
    def _detect_all_tools(self) -> Dict[str, Dict]:
        """Detecte tous les outils de capture disponibles avec metadonnees"""
        tools = {}
        
        system_tools = [
            {"name": "maim", "quality": 95, "speed": 90, "features": ["desktop", "window", "area", "multimonitor"]},
            {"name": "scrot", "quality": 85, "speed": 80, "features": ["desktop", "window", "area", "multimonitor"]},
            {"name": "gnome-screenshot", "quality": 90, "speed": 70, "features": ["desktop"]},
            {"name": "import", "quality": 80, "speed": 60, "features": ["desktop", "window", "area"]},
            {"name": "xwd", "quality": 60, "speed": 95, "features": ["desktop", "window"]},
        ]
        
        for tool_info in system_tools:
            name = tool_info["name"]
            try:
                result = subprocess.run(
                    ["which", name], capture_output=True, check=True
                )
                tools[name] = {
                    "path": result.stdout.strip(),
                    "quality": tool_info["quality"],
                    "speed": tool_info["speed"],
                    "features": tool_info["features"],
                    "type": "system"
                }
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if self.python_screenshot.mss_available:
            tools["mss"] = {
                "quality": 88,
                "speed": 75,
                "features": ["desktop", "area"],
                "type": "python",
                "library": "mss"
            }
        
        logger.info(f"Outils de capture detectes: {list(tools.keys())}")
        return tools
    
    def _get_preference_order(self) -> List[str]:
        """Calcule l'ordre de preference automatiquement"""
        if not self.available_tools:
            return []
        
        def score(tool_name: str) -> Tuple[int, int, int]:
            tool = self.available_tools.get(tool_name, {})
            quality = tool.get("quality", 0)
            speed = tool.get("speed", 0)
            features_count = len(tool.get("features", []))
            return (quality * 10 + speed + features_count * 5, quality, speed)
        
        sorted_tools = sorted(self.available_tools.keys(), key=score, reverse=True)
        logger.info(f"Ordre de preference: {sorted_tools}")
        return sorted_tools
    
    def get_best_tool(self, feature: str) -> Optional[str]:
        """Retourne le meilleur outil pour une fonction donnee"""
        for tool_name in self.preferred_order:
            tool = self.available_tools.get(tool_name, {})
            if feature in tool.get("features", []):
                return tool_name
        return None
    
    def list_windows(self) -> List[Dict]:
        """Liste les fenetres actives avec xdotool"""
        try:
            result = subprocess.run(
                ["xdotool", "search", "--onlyvisible", "--name", "."],
                capture_output=True, text=True
            )
            windows = []
            for wpid in result.stdout.strip().split("\n"):
                if wpid:
                    try:
                        win_name = subprocess.run(
                            ["xdotool", "getwindowname", wpid],
                            capture_output=True, text=True
                        ).stdout.strip()
                        windows.append({"id": wpid, "name": win_name})
                    except Exception:
                        windows.append({"id": wpid, "name": "Unknown"})
            return windows
        except FileNotFoundError:
            logger.warning("xdotool non installe")
            return []
    
    def list_processes_with_windows(self) -> List[Dict]:
        """Liste les processus avec fenetres visibles"""
        try:
            result = subprocess.run(
                ["xdotool", "search", "--onlyvisible", "--class", "."],
                capture_output=True, text=True
            )
            processes = []
            seen = set()
            for wpid in result.stdout.strip().split("\n"):
                if wpid and wpid not in seen:
                    seen.add(wpid)
                    try:
                        pid = subprocess.run(
                            ["xdotool", "getwindowpid", wpid],
                            capture_output=True, text=True
                        ).stdout.strip()
                        proc_name = subprocess.run(
                            ["ps", "-p", pid, "-o", "comm="],
                            capture_output=True, text=True
                        ).stdout.strip()
                        win_name = subprocess.run(
                            ["xdotool", "getwindowname", wpid],
                            capture_output=True, text=True
                        ).stdout.strip()
                        processes.append({
                            "window_id": wpid,
                            "process_id": pid,
                            "process_name": proc_name,
                            "window_name": win_name
                        })
                    except Exception:
                        continue
            return processes
        except FileNotFoundError:
            logger.warning("xdotool non installe")
            return []
    
    def capture_desktop(self, output: Optional[str] = None) -> Dict:
        """Capture le bureau complet avec le meilleur outil disponible"""
        timestamp = int(time.time())
        if output is None:
            output = str(self.screenshots_dir / f"desktop_{timestamp}.png")
        output_path = Path(output)
        
        for tool_name in self.preferred_order:
            if tool_name == "mss":
                if self.python_screenshot.capture_desktop(output_path):
                    return {"status": "success", "path": output, "tool": "mss", "type": "desktop"}
                continue
            
            tool = self.available_tools.get(tool_name, {})
            if "desktop" not in tool.get("features", []):
                continue
            
            try:
                cmd = self._get_tool_command(tool_name, "desktop", output_path)
                if cmd:
                    subprocess.run(cmd, check=True, capture_output=True)
                    if output_path.exists():
                        logger.info(f"Capture bureau reussie: {output} (outil: {tool_name})")
                        return {"status": "success", "path": output, "tool": tool_name, "type": "desktop"}
            except Exception as e:
                logger.debug(f"Tool {tool_name} failed: {e}")
                continue
        
        return {"status": "error", "message": "Aucun outil de capture disponible"}
    
    def capture_window(self, window_id: str, output: Optional[str] = None) -> Dict:
        """Capture une fenetre specifique"""
        timestamp = int(time.time())
        if output is None:
            output = str(self.screenshots_dir / f"window_{window_id}_{timestamp}.png")
        output_path = Path(output)
        
        for tool_name in self.preferred_order:
            if tool_name == "mss":
                continue
            
            tool = self.available_tools.get(tool_name, {})
            if "window" not in tool.get("features", []):
                continue
            
            try:
                if tool_name == "maim":
                    window_id_hex = hex(int(window_id))
                    subprocess.run(
                        ["maim", "-i", window_id_hex, str(output_path)],
                        check=True, capture_output=True
                    )
                elif tool_name == "import":
                    subprocess.run(
                        ["import", "-window", window_id, str(output_path)],
                        check=True, capture_output=True
                    )
                elif tool_name == "xwd":
                    subprocess.run(
                        ["xwd", "-id", window_id],
                        capture_output=True
                    )
                    continue
                else:
                    continue
                
                if output_path.exists():
                    logger.info(f"Capture fenetre {window_id} reussie: {output} (outil: {tool_name})")
                    return {"status": "success", "path": output, "window_id": window_id, "tool": tool_name, "type": "window"}
            except Exception as e:
                logger.debug(f"Window capture with {tool_name} failed: {e}")
                continue
        
        return {"status": "error", "message": "Impossible de capturer la fenetre"}
    
    def capture_process(self, process_name: str, output: Optional[str] = None) -> Dict:
        """Capture la fenetre d'un processus par nom"""
        windows = self.list_processes_with_windows()
        for win in windows:
            if (process_name.lower() in win["process_name"].lower() or
                process_name.lower() in win["window_name"].lower()):
                return self.capture_window(win["window_id"], output)
        return {"status": "error", "message": f"Processus '{process_name}' non trouve"}
    
    def capture_area(self, x: int, y: int, width: int, height: int,
                     output: Optional[str] = None) -> Dict:
        """Capture une zone rectangulaire"""
        timestamp = int(time.time())
        if output is None:
            output = str(self.screenshots_dir / f"area_{x}_{y}_{width}x{height}_{timestamp}.png")
        output_path = Path(output)
        
        for tool_name in self.preferred_order:
            if tool_name == "mss":
                if self.python_screenshot.capture_area(output_path, x, y, width, height):
                    return {"status": "success", "path": output, "tool": "mss", "area": (x, y, width, height), "type": "area"}
                continue
            
            tool = self.available_tools.get(tool_name, {})
            if "area" not in tool.get("features", []):
                continue
            
            try:
                if tool_name == "import":
                    subprocess.run([
                        "import", "-window", "root", "-crop",
                        f"{width}x{height}+{x}+{y}", str(output_path)
                    ], check=True, capture_output=True)
                elif tool_name == "maim":
                    subprocess.run([
                        "maim", "-g", f"{width}x{height}+{x}+{y}", str(output_path)
                    ], check=True, capture_output=True)
                elif tool_name == "scrot":
                    subprocess.run([
                        "scrot", "-a", f"{x},{y},{width},{height}", str(output_path)
                    ], check=True, capture_output=True)
                else:
                    continue
                
                if output_path.exists():
                    logger.info(f"Capture zone {x},{y} {width}x{height} reussie: {output} (outil: {tool_name})")
                    return {"status": "success", "path": output, "tool": tool_name, "area": (x, y, width, height), "type": "area"}
            except Exception as e:
                logger.debug(f"Area capture with {tool_name} failed: {e}")
                continue
        
        return {"status": "error", "message": "Impossible de capturer la zone"}
    
    def capture_all_displays(self, output: Optional[str] = None) -> Dict:
        """Capture tous les ecrans (multi-monitor)"""
        timestamp = int(time.time())
        if output is None:
            output = str(self.screenshots_dir / f"multi_display_{timestamp}.png")
        output_path = Path(output)
        
        for tool_name in self.preferred_order:
            tool = self.available_tools.get(tool_name, {})
            if "multimonitor" not in tool.get("features", []):
                continue
            
            try:
                if tool_name == "maim":
                    subprocess.run(
                        ["maim", "--multimonitor", str(output_path)],
                        check=True, capture_output=True
                    )
                elif tool_name == "scrot":
                    subprocess.run(
                        ["scrot", "--multidisp", str(output_path)],
                        check=True, capture_output=True
                    )
                else:
                    continue
                
                if output_path.exists():
                    return {"status": "success", "path": output, "tool": tool_name, "type": "multimonitor"}
            except Exception as e:
                logger.debug(f"Multimonitor capture with {tool_name} failed: {e}")
                continue
        
        return {"status": "error", "message": "Impossible de capturer tous les ecrans"}
    
    def _get_tool_command(self, tool_name: str, feature: str, output_path: Path) -> Optional[List[str]]:
        """Genere la commande pour un outil donne"""
        commands = {
            "maim": ["maim", str(output_path)],
            "scrot": ["scrot", str(output_path)],
            "gnome-screenshot": ["gnome-screenshot", "-f", str(output_path)],
            "import": ["import", str(output_path)],
            "xwd": ["xwd", "-root"],
        }
        return commands.get(tool_name)
    
    def get_screenshot_history(self, limit: int = 20) -> List[Dict]:
        """Retourne l'historique des captures"""
        screenshots = []
        for f in sorted(self.screenshots_dir.glob("*.png"), reverse=True)[:limit]:
            screenshots.append({
                "path": str(f),
                "filename": f.name,
                "size": f.stat().st_size,
                "created": f.stat().st_ctime
            })
        return screenshots
    
    def get_status(self) -> Dict:
        """Retourne le statut du systeme de capture"""
        return {
            "available_tools": list(self.available_tools.keys()),
            "preferred_order": self.preferred_order,
            "python_mss_available": self.python_screenshot.mss_available,
            "best_desktop_tool": self.get_best_tool("desktop"),
            "best_window_tool": self.get_best_tool("window"),
            "best_area_tool": self.get_best_tool("area"),
            "screenshots_dir": str(self.screenshots_dir)
        }


_screenshot = None


def get_screenshot_system() -> SystemScreenshot:
    global _screenshot
    if _screenshot is None:
        _screenshot = SystemScreenshot()
    return _screenshot
