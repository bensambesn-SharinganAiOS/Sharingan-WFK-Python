# Documentation du Système de Navigation Web de Sharingan OS

## 1. Vue d'Ensemble

Le système de navigation web de Sharingan OS utilise le **Chrome DevTools Protocol (CDP)** via un navigateur Chrome partagé et persistant. Le navigateur tourne sur un port fixe (9999) et peut être contrôlé par l'IA **et** utilisé manuellement par l'utilisateur en même temps.

### Caractéristiques principales :
- **Navigateur partagé** : Une seule instance Chrome pour toutes les sessions
- **Contrôle CDP** : Communication via WebSocket avec Chrome
- **Usage hybride** : IA et utilisateur peuvent interagir simultanément
- **Persistant** : Le navigateur reste ouvert entre les sessions
- **Pas de nouveau script** : Système prêt à l'emploi via imports

---

## 2. Architecture Technique

### 2.1 Architecture en couches

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHARINGAN OS                                 │
│         (action_executor.py - Langage naturel)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               browser_shell.py                                  │
│        (Interface utilisateur simple et intuitive)              │
│  go(), search(), read(), scroll(), click(), current(), js()     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│           sharingans_browser_shared.py                         │
│              (Singleton CDP global)                             │
│          CDPBrowser, BrowserAPI, get_browser()                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Chrome CDP :9999                                │
│          (Navigateur partagé persistant)                        │
│     Contrôlable par IA ET utilisable manuellement               │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Port de Communication

- **Port 9999** : Instance Chrome principale (partagée)
- Pas de détection automatique nécessaire
- Connexion directe via `http://localhost:9999/json`

---

## 3. Installation et Lancement

### 3.1 Lancer le navigateur Chrome

```bash
# Lancer Chrome avec debugging distant
google-chrome --remote-debugging-port=9999 \
    --no-sandbox \
    --disable-dev-shm-usage \
    --disable-gpu \
    --user-data-dir=/tmp/sharingans-chrome \
    https://google.com &

# Ou simplement
google-chrome --remote-debugging-port=9999 &
```

### 3.2 Vérifier que le navigateur tourne

```bash
# Vérifier le port
curl http://localhost:9999/json

# Doit retourner la liste des onglets
```

---

## 4. Utilisation du Système

### 4.1 Méthode 1: Import Direct (RECOMMANDÉ)

```python
# Import des fonctions depuis browser_shell
from browser_shell import go, read, search, scroll, current, js

import asyncio

async def ma_tache():
    # Navigation
    await go("https://wikipedia.org")
    
    # Lecture de contenu
    content = await read("article")
    
    # Recherche Google
    await search("mon terme de recherche")
    
    # Défilement
    await scroll(500)
    
    # État actuel
    state = await current()
    print(f"URL: {state['url']}")
    
    # Exécution JavaScript
    result = await js("document.title")

asyncio.run(ma_tache())
```

### 4.2 Méthode 2: Ligne de Commande

```bash
# Une seule commande
python3 browser_shell.py -c "go https://google.com"

# Commandes multiples (séparées par &&)
python3 browser_shell.py -c "go wikipedia && read && scroll 300"

# Recherche et lecture
python3 browser_shell.py -c "go google.com && search Python && read"
```

### 4.3 Méthode 3: Shell Interactif

```bash
# Lancer le shell
python3 browser_shell.py

# Commandes interactives
browser> go https://wikipedia.org
browser> read
browser> scroll 500
browser> search mon terme
browser> current
browser> quit
```

### 4.4 Méthode 4: Sharingan OS (Langage Naturel)

```python
from sharingan_app._internal.action_executor import get_action_executor

executor = get_action_executor()

# Commandes en langage naturel
executor.execute_action("navigue vers wikipedia")
executor.execute_action("cherche Python sur Google")
executor.execute_action("lis la page")
executor.execute_action("défile vers le bas")
```

---

## 5. Référence des Fonctions

### 5.1 browser_shell.py

| Fonction | Description | Exemple |
|----------|-------------|---------|
| `go(url)` | Naviguer vers une URL | `await go("https://google.com")` |
| `search(query)` | Recherche Google | `await search("Python")` |
| `read(selector)` | Lire le contenu | `await read("article")` |
| `scroll(pixels)` | Défiler la page | `await scroll(500)` |
| `click(selector)` | Cliquer sur un élément | `await click("button")` |
| `type(text, selector)` | Taper du texte | `await type("mon texte", "input")` |
| `press(key)` | Appuyer sur une touche | `await press("Enter")` |
| `current()` | État actuel | `state = await current()` |
| `screenshot(path)` | Capturer l'écran | `await screenshot("/tmp/img.png")` |
| `js(code)` | Exécuter JavaScript | `await js("document.title")` |

### 5.2 sharingans_browser_shared.py

| Fonction/Classe | Description |
|-----------------|-------------|
| `CDPBrowser` | Classe de connexion CDP de bas niveau |
| `BrowserAPI` | API de commodité (Singleton) |
| `get_browser()` | Obtenir l'instance du navigateur |
| `navigate(url)` | Naviguer vers une URL |
| `get_text(selector)` | Extraire le texte d'un élément |
| `execute_js(code)` | Exécuter du JavaScript |
| `get_url()` | Obtenir l'URL actuelle |
| `get_title()` | Obtenir le titre de la page |

---

## 6. Exemples d'Utilisation

### 6.1 Lecture d'un article Wikipedia

```python
from browser_shell import go, read, scroll
import asyncio

async def lire_wikipedia():
    await go("https://fr.wikipedia.org/wiki/Python_(langage)")
    await asyncio.sleep(2)
    
    # Lire le contenu principal
    content = await read("p", max_length=5000)
    print(f"Article: {content[:500]}...")
    
    # Défiler pour lire plus
    for _ in range(5):
        await scroll(400)
        await asyncio.sleep(0.5)

asyncio.run(lire_wikipedia())
```

### 6.2 Recherche et navigation

```python
from browser_shell import go, search, current
import asyncio

async def rechercher_actualite():
    # Aller sur Google
    await go("https://www.google.com")
    
    # Faire une recherche
    await search("actualités Sénégal")
    await asyncio.sleep(2)
    
    # Vérifier l'URL
    state = await current()
    print(f"URL de recherche: {state['url']}")

asyncio.run(rechercher_actualite())
```

### 6.3 Utilisation avec Sharingan OS

```python
from sharingan_app._internal.action_executor import get_action_executor

executor = get_action_executor()

# Navigation en langage naturel
results = executor.execute_action("va sur bbc.com/afrique")
print(f"Navigué vers: {results.get('url')}")

# Recherche
results = executor.execute_action("cherche musique sénégalaise")
print(f"Recherche effectuée")

# Lecture
results = executor.execute_action("lis l'article")
print(f"Contenu lu: {results.get('text', '')[:200]}...")
```

---

## 7. Structure du Projet

### 7.1 Fichiers Principaux (À UTILISER)

```
/root/Projets/Sharingan-WFK-Python/
├── browser_shell.py                    ✅ Interface principale
│   └── go(), search(), read(), scroll(), current(), js()
│
├── sharingans_browser_shared.py        ✅ Module Singleton CDP
│   └── CDPBrowser, BrowserAPI, get_browser()
│
└── sharingan_app/_internal/
    └── action_executor.py              ✅ Intégration Sharingan OS
```

### 7.2 Anciens fichiers (conservés pour compatibilité)

```
├── browser_cdp_controller.py           ⚠️ Remplacé
├── browser_manager.py                  ⚠️ Remplacé
├── browser_client.py                   ⚠️ Non utilisé
├── browser_control.py                  ⚠️ Non utilisé
├── browser_daemon.py                   ⚠️ Non utilisé
├── browser_server.py                   ⚠️ Non utilisé
├── cdp_control.py                      ⚠️ Doublon
└── sharingan_app/_internal/
    ├── browser_controller.py           ⚠️ Remplacé
    ├── browser_manager.py              ⚠️ Remplacé
    └── browser_controller_complete.py  ⚠️ Fallback Selenium
```

---

## 8. Historique et Traçabilité

### 8.1 Journalisation Automatique

Le système enregistre automatiquement :

```python
# Exemple de log généré
[INFO] 2026-01-17 10:30:15 - Navigateur connecté (port 9999)
[INFO] 2026-01-17 10:30:18 - Navigation vers: https://wikipedia.org
[INFO] 2026-01-17 10:30:20 - Lecture: 1500 caractères extraits
[INFO] 2026-01-17 10:30:25 - Défilement: 500px
[INFO] 2026-01-17 10:30:30 - Navigation vers: https://google.com
```

### 8.2 État du Navigateur

Le navigateur conserve un historique des actions :

```
Session actuelle:
- URL: https://wikipedia.org
- Titre: Wikipedia
- Actions: 5
- Dernière action: scroll(500)
```

---

## 9. Bonnes Pratiques

### 9.1 Garder le Navigateur Ouvert

```python
# ❌ NE FAITES PAS CECI
from browser_shell import go
await go("https://site.com")
# Le navigateur reste ouvert mais pas de gestion de session

# ✅ FAITES CECI
# Le navigateur est déjà lancé sur port 9999
# Utilisez go() quand vous en avez besoin
```

### 9.2 Attente du Chargement

```python
import asyncio
from browser_shell import go

# Attendre après chaque navigation
await go("https://site.com")
await asyncio.sleep(2)  # Attendre le chargement
```

### 9.3 Gestion des Erreurs

```python
from browser_shell import go
import asyncio

try:
    await go("https://site.com")
except Exception as e:
    print(f"Erreur: {e}")
    # Le navigateur reste ouvert, réessayez
```

---

## 10. Dépannage

### 10.1 Navigateur Non Trouvé

```bash
# Vérifier si Chrome tourne
ps aux | grep chrome

# Lancer Chrome si nécessaire
google-chrome --remote-debugging-port=9999 &
```

### 10.2 Connexion Refusée

```bash
# Vérifier le port
netstat -tlnp | grep 9999

# Le navigateur doit être lancé avec le mode remote debugging
google-chrome --remote-debugging-port=9999
```

### 10.3 Erreur de Connexion CDP

```python
from browser_shell import get_browser_shell

shell = get_browser_shell()
connected = await shell.connect()

if not connected:
    print("Navigateur non accessible. Vérifiez qu'il tourne sur port 9999.")
```

---

## 11. Limitations Connues

| Fonctionnalité | Statut | Notes |
|----------------|--------|-------|
| Navigation URL | ✅ Fonctionnel | |
| Recherche Google | ✅ Fonctionnel | |
| Lecture contenu | ✅ Fonctionnel | |
| Défilement | ✅ Fonctionnel | |
| Exécution JS | ✅ Fonctionnel | |
| Clic sur éléments | ⚠️ Partiel | Shadow DOM limité |
| Commentaires YouTube | ⚠️ Limité | Shadow DOM |
| Gmail | ⚠️ Brouillons only | Shadow DOM |
| CAPTCHA | ❌ Non supporté | Interaction manuelle requise |
| OAuth/2FA | ❌ Non supporté | Interaction manuelle requise |
| Upload fichiers | ❌ Non supporté | Restrictions sécurité |

---

## 12. Conclusion

Le système de navigation de Sharingan OS offre :

1. **Simplicité** : Plus besoin de créer de scripts, utilisez les imports
2. **Flexibilité** : 4 méthodes d'utilisation différentes
3. **Persistance** : Navigateur partagé entre toutes les sessions
4. **Collaboration** : IA et utilisateur peuvent travailler ensemble
5. **Intégration** : Compatible avec Sharingan OS (langage naturel)

Pour étendre ce système :
- Ajouter un système de snapshots de pages
- Implémenter la gestion de plusieurs onglets
- Créer une interface de visualisation des actions
- Ajouter la reconnaissance d'éléments

---

*Documentation mise à jour le 17 janvier 2026*
*Projet : Sharingan OS - Système de Navigation Web*
