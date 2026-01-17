#!/usr/bin/env python3
"""
System Screenshot Module - Capture d'écran du système hôte
Supporte: Desktop complet, fenêtre spécifique, application
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, List, Dict
import logging

logger = logging.getLogger("sharingan.screenshot")


class SystemScreenshot:
    def __init__(self):
        self.screenshots_dir = Path("/tmp/sharingan/screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.tools = []
        self._detect_tools()

    def _detect_tools(self) -> List[str]:
        """Détecte les outils de capture disponibles"""
        available_tools = ["scrot", "import", "gnome-screenshot", "maim", "grim", "xwd"]
        for tool in available_tools:
            try:
                subprocess.run(
                    ["which", tool], capture_output=True, check=True
                )
                self.tools.append(tool)
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        logger.info(f"Outils de capture disponibles: {self.tools}")
        return self.tools

    def list_windows(self) -> List[Dict]:
        """Liste les fenêtres actives avec xdotool"""
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
            logger.warning("xdotool non installé")
            return []

    def list_processes_with_windows(self) -> List[Dict]:
        """Liste les processus avec fenêtres visibles"""
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
            logger.warning("xdotool non installé")
            return []

    def capture_desktop(self, output: Optional[str] = None) -> Dict:
        """Capture le bureau complet"""
        timestamp = int(time.time())
        if output is None:
            output = str(self.screenshots_dir / f"desktop_{timestamp}.png")

        for tool in ["maim", "scrot", "gnome-screenshot", "import"]:
            try:
                if tool == "maim":
                    subprocess.run(["maim", output], check=True, capture_output=True)
                elif tool == "scrot":
                    subprocess.run(["scrot", output], check=True, capture_output=True)
                elif tool == "gnome-screenshot":
                    subprocess.run(["gnome-screenshot", "-f", output], check=True, capture_output=True)
                elif tool == "import":
                    subprocess.run(["import", output], check=True, capture_output=True)
                logger.info(f"Capture bureau réussie: {output} (outil: {tool})")
                return {"status": "success", "path": output, "tool": tool, "type": "desktop"}
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        return {"status": "error", "message": "Aucun outil de capture disponible"}

    def capture_window(self, window_id: str, output: Optional[str] = None) -> Dict:
        """Capture une fenêtre spécifique par ID"""
        timestamp = int(time.time())
        if output is None:
            output = str(self.screenshots_dir / f"window_{window_id}_{timestamp}.png")

        try:
            subprocess.run(
                ["import", "-window", window_id, output],
                check=True, capture_output=True
            )
            logger.info(f"Capture fenêtre {window_id} réussie: {output}")
            return {"status": "success", "path": output, "window_id": window_id, "type": "window"}
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        try:
            window_id_hex = hex(int(window_id))
            subprocess.run(
                ["maim", "-i", window_id_hex, output],
                check=True, capture_output=True
            )
            logger.info(f"Capture fenêtre {window_id} réussie (maim): {output}")
            return {"status": "success", "path": output, "window_id": window_id, "type": "window"}
        except Exception as e:
            logger.error(f"Échec capture fenêtre {window_id}: {e}")
            return {"status": "error", "message": str(e)}

    def capture_process(self, process_name: str, output: Optional[str] = None) -> Dict:
        """Capture la fenêtre d'un processus par nom"""
        windows = self.list_processes_with_windows()
        for win in windows:
            if (process_name.lower() in win["process_name"].lower() or
                process_name.lower() in win["window_name"].lower()):
                return self.capture_window(win["window_id"], output)
        return {"status": "error", "message": f"Processus '{process_name}' non trouvé"}

    def capture_area(self, x: int, y: int, width: int, height: int,
                     output: Optional[str] = None) -> Dict:
        """Capture une zone rectangulaire"""
        timestamp = int(time.time())
        if output is None:
            output = str(self.screenshots_dir / f"area_{x}_{y}_{width}x{height}_{timestamp}.png")

        try:
            subprocess.run([
                "import", "-window", "root", "-crop",
                f"{width}x{height}+{x}+{y}", output
            ], check=True, capture_output=True)
            logger.info(f"Capture zone {x},{y} {width}x{height} réussie: {output}")
            return {"status": "success", "path": output, "area": (x, y, width, height), "type": "area"}
        except Exception as e:
            logger.error(f"Échec capture zone: {e}")
            return {"status": "error", "message": str(e)}

    def capture_all_displays(self, output: Optional[str] = None) -> Dict:
        """Capture tous les écrans (multi-monitor)"""
        timestamp = int(time.time())
        if output is None:
            output = str(self.screenshots_dir / f"multi_display_{timestamp}.png")

        try:
            subprocess.run(["maim", "--multimonitor", output], check=True, capture_output=True)
            return {"status": "success", "path": output, "type": "multimonitor"}
        except Exception:
            pass

        try:
            subprocess.run(["scrot", "--multidisp", output], check=True, capture_output=True)
            return {"status": "success", "path": output, "type": "multimonitor"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

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


_screenshot = None


def get_screenshot_system() -> SystemScreenshot:
    global _screenshot
    if _screenshot is None:
        _screenshot = SystemScreenshot()
    return _screenshot
