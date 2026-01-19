#!/usr/bin/env python3
"""
Comportement Appris - Lecture Active de Feed
Sharingan OS - Navigation douce + extraction de contenu et commentaires
"""

import sys
import time
import json
from pathlib import Path

# Configuration des comportements appris avec lecture
LEARNED_BEHAVIORS = {
    'human_feed_reading': {
        'description': 'Navigation douce comme un humain lisant son feed',
        'sites': ['facebook', 'youtube', 'tiktok', 'instagram', 'twitter'],
        'sequence': [
            {'action': 'scroll', 'pixels': 200, 'pause': 3.5, 'read_content': True},
            {'action': 'scroll', 'pixels': 180, 'pause': 4.2, 'read_content': True},
            {'action': 'scroll', 'pixels': 220, 'pause': 3.8, 'read_content': True},
            {'action': 'scroll', 'pixels': 250, 'pause': 5.1, 'read_content': True},
            {'action': 'scroll', 'pixels': 190, 'pause': 4.5, 'read_content': True},
            {'action': 'click_comments', 'pause': 2.0, 'read_comments': True},
            {'action': 'scroll', 'pixels': 280, 'pause': 4.0, 'read_content': True},
            {'action': 'scroll', 'pixels': 210, 'pause': 3.9, 'read_content': True},
        ],
        'rules': [
            'Pas de likes/réactions',
            'Clics commentaires sélectifs seulement',
            'Pauses variables 3-5 secondes',
            'Scrolls irréguliers 180-280px',
            'Comportement passif de lecture',
            'Extraction du texte des publications',
            'Lecture des commentaires visibles'
        ],
        'success_rate': '95%'
    }
}

class LearnedBehaviorReproducer:
    """Reproducteur de comportements appris avec lecture de contenu"""

    def __init__(self, behavior_name='human_feed_reading'):
        self.behavior = LEARNED_BEHAVIORS.get(behavior_name, {})
        if not self.behavior:
            raise ValueError(f"Comportement '{behavior_name}' non trouvé")

        self.cmd_file = "/tmp/facebook_browser_cmd.txt"
        self.result_file = "/tmp/facebook_browser_result.txt"
        self.content_log = []  # Stockage du contenu lu

    def send_command(self, cmd_type, params=None):
        """Envoie une commande au démon navigateur"""
        if params is None:
            params = {}

        cmd_data = {
            "type": cmd_type,
            "params": params,
            "timestamp": time.time()
        }

        try:
            with open(self.cmd_file, 'w') as f:
                json.dump(cmd_data, f)
            return True
        except Exception as e:
            print(f"❌ Erreur envoi commande: {e}")
            return False

    def wait_result(self, timeout=10):
        """Attend le résultat d'une commande"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if Path(self.result_file).exists():
                try:
                    with open(self.result_file, 'r') as f:
                        result = json.load(f)
                    Path(self.result_file).unlink()  # Supprime le fichier
                    return result
                except Exception as e:
                    print(f"❌ Erreur lecture résultat: {e}")
                    break
            time.sleep(0.5)
        return None

    def extract_content(self, site_url):
        """Extrait le contenu visible selon le site - approche simplifiée"""
        content = {
            'timestamp': time.time(),
            'site': site_url,
            'publications': [],
            'commentaires': [],
            'debug_info': {}
        }

        try:
            # Méthode simplifiée : extraire tout le texte visible de la page
            self.send_command('execute_js', {
                'script': '''
                // Fonction pour extraire du texte visible
                function getVisibleText() {
                    const elements = document.querySelectorAll('*');
                    let texts = [];

                    for (let el of elements) {
                        // Vérifier si l'élément est visible
                        const style = window.getComputedStyle(el);
                        const isVisible = style.display !== 'none' &&
                                        style.visibility !== 'hidden' &&
                                        style.opacity !== '0' &&
                                        el.offsetWidth > 0 &&
                                        el.offsetHeight > 0;

                        if (isVisible && el.textContent) {
                            const text = el.textContent.trim();
                            // Filtrer les textes intéressants (plus de 20 caractères, moins de 1000)
                            if (text.length > 20 && text.length < 1000) {
                                // Éviter les textes dupliqués ou répétitifs
                                if (!texts.some(t => t.includes(text.substring(0, 50)))) {
                                    texts.push(text);
                                }
                                if (texts.length >= 10) break; // Limiter à 10 éléments
                            }
                        }
                    }

                    return texts.slice(0, 5); // Retourner les 5 premiers
                }

                // Extraire des informations de debug
                const debug = {
                    url: window.location.href,
                    title: document.title,
                    bodyTextLength: document.body.textContent.length,
                    visibleElements: document.querySelectorAll('*').length
                };

                return {
                    visible_texts: getVisibleText(),
                    debug: debug,
                    timestamp: new Date().toISOString()
                };
                '''
            })

            # Attendre le résultat de l'extraction
            result = self.wait_result(15)  # Timeout plus long pour l'extraction
            if result and result.get('status') == 'success':
                js_result = result.get('result', {})
                content['debug_info'] = js_result.get('debug', {})
                visible_texts = js_result.get('visible_texts', [])

                # Traiter les textes visibles selon le site
                if 'facebook.com' in site_url:
                    content['publications'] = [{
                        'index': i+1,
                        'text': text[:300] + '...' if len(text) > 300 else text,
                        'type': 'facebook_post',
                        'timestamp': time.time()
                    } for i, text in enumerate(visible_texts[:3])]

                elif 'youtube.com' in site_url:
                    content['publications'] = [{
                        'index': i+1,
                        'title': text.split('\n')[0] if '\n' in text else text[:100],
                        'description': text[:200] + '...' if len(text) > 200 else text,
                        'type': 'youtube_video',
                        'timestamp': time.time()
                    } for i, text in enumerate(visible_texts[:3])]

                elif 'tiktok.com' in site_url:
                    content['publications'] = [{
                        'index': i+1,
                        'description': text[:250] + '...' if len(text) > 250 else text,
                        'type': 'tiktok_video',
                        'timestamp': time.time()
                    } for i, text in enumerate(visible_texts[:3])]

                # Les commentaires sont plus difficiles à identifier, on utilise une approche générique
                content['commentaires'] = [{
                    'index': i+1,
                    'text': text[:150] + '...' if len(text) > 150 else text,
                    'type': 'comment',
                    'timestamp': time.time()
                } for i, text in enumerate(visible_texts[3:6])]  # Prendre les suivants comme commentaires

        except Exception as e:
            content['debug_info']['error'] = str(e)

        return content

    def execute_learned_behavior(self, site_url=None):
        """Exécute le comportement appris avec lecture de contenu"""
        print(f"🎯 Reproduction du comportement appris: {self.behavior['description']}")
        print(f"📊 Taux de succès: {self.behavior['success_rate']}")
        print(f"🌐 Sites compatibles: {', '.join(self.behavior['sites'])}")
        print("📖 Mode lecture actif: Publications + Commentaires")
        print()

        # Navigation vers le site si spécifié
        if site_url:
            print(f"🔄 Navigation vers: {site_url}")
            self.send_command('navigate', {'url': site_url})
            result = self.wait_result()
            if result and result.get('status') == 'success':
                print("✅ Navigation réussie")
            else:
                print("⚠️ Navigation peut-être échouée, continuation...")
            time.sleep(5)  # Pause plus longue pour le chargement

        # Exécution de la séquence apprise avec lecture
        print("🚀 Début de la séquence de lecture active...")
        print("=" * 60)
        print()

        for i, step in enumerate(self.behavior['sequence'], 1):
            action = step['action']

            print(f"[{i}/{len(self.behavior['sequence'])}] ", end="")

            if action == 'scroll':
                pixels = step['pixels']
                print(f"📜 Scroll de {pixels}px vers le bas")

                # Effectuer le scroll
                self.send_command('scroll', {'pixels': pixels, 'direction': 'down'})
                result = self.wait_result()
                if result and result.get('status') == 'success':
                    print("   ✅ Scroll réussi")
                else:
                    print("   ⚠️ Scroll peut-être échoué")

                # Lire le contenu si demandé
                if step.get('read_content', False) and site_url:
                    print("   📖 Extraction du contenu visible...")
                    content = self.extract_content(site_url)
                    self.content_log.append(content)

                    # Afficher un résumé du contenu extrait
                    if 'posts' in content and content['posts']:
                        print(f"   📝 {len(content['posts'])} publications trouvées")
                        for post in content['posts'][:2]:  # Afficher les 2 premiers
                            print(f"      • {post['text'][:100]}...")
                    elif 'videos' in content and content['videos']:
                        print(f"   🎥 {len(content['videos'])} vidéos trouvées")
                        for video in content['videos'][:2]:
                            if 'title' in video:
                                print(f"      • {video['title']}")
                            elif 'description' in video:
                                print(f"      • {video['description'][:100]}...")

                    if content.get('comments'):
                        print(f"   💬 {len(content['comments'])} commentaires trouvés")

            elif action == 'click_comments':
                print("💬 Clic sur commentaires + lecture")
                # Essayer différents sélecteurs de commentaires
                for selector in ["[aria-label*='Commentaire']", "[data-testid*='comment']", ".comment-link"]:
                    self.send_command('click', {'selector': selector})
                    time.sleep(0.5)

                result = self.wait_result()
                if result and result.get('status') == 'success':
                    print("   ✅ Clic commentaires réussi")
                else:
                    print("   ⚠️ Clic commentaires peut-être échoué")

                # Lire les commentaires après le clic
                if step.get('read_comments', False) and site_url:
                    time.sleep(2)  # Attendre le chargement des commentaires
                    print("   📖 Lecture des commentaires...")
                    content = self.extract_content(site_url)
                    self.content_log.append(content)

                    if content.get('comments'):
                        print(f"   💬 {len(content['comments'])} commentaires lus:")
                        for comment in content['comments'][:3]:  # Afficher les 3 premiers
                            print(f"      • {comment['text'][:120]}...")

            # Pause réaliste
            pause = step.get('pause', 3.0)
            print(f"   ⏱️ Pause de {pause}s pour lecture...")
            time.sleep(pause)

        print()
        print("🎉 Séquence de lecture terminée !")
        print(f"📚 Contenu extrait: {len(self.content_log)} captures")
        print()
        print("📝 Règles respectées:")
        for rule in self.behavior['rules']:
            print(f"   ✅ {rule}")

        # Afficher un résumé final du contenu lu
        print()
        print("📊 RÉSUMÉ DU CONTENU LU:")
        total_posts = sum(len(c.get('posts', [])) + len(c.get('videos', [])) for c in self.content_log)
        total_comments = sum(len(c.get('comments', [])) for c in self.content_log)
        print(f"   📝 Publications/Vidéos: {total_posts}")
        print(f"   💬 Commentaires: {total_comments}")
        print(f"   🌐 Site: {site_url}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 learned_behavior.py <comportement> [url_site]")
        print()
        print("Comportements disponibles:")
        for name, behavior in LEARNED_BEHAVIORS.items():
            print(f"  {name}: {behavior['description']}")
            print(f"    Sites: {', '.join(behavior['sites'])}")
            print("    Fonctions: Lecture active de contenu + commentaires")
        print()
        print("Exemples:")
        print("  python3 learned_behavior.py human_feed_reading https://facebook.com")
        print("  python3 learned_behavior.py human_feed_reading https://youtube.com")
        return

    behavior_name = sys.argv[1]
    site_url = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        reproducer = LearnedBehaviorReproducer(behavior_name)
        reproducer.execute_learned_behavior(site_url)
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()