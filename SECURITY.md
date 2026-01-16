# Security Policy - Sharingan OS

## Vue d'ensemble

Sharingan OS est un système d'IA autonome avec capacités de cybersécurité. Ce document explique les limites de sécurité et comment activer/désactiver les fonctionnalités dangereuses.

## Niveaux de Danger

### Niveau 1 - Sûr (Auto-activé)
- Lecture de fichiers
- Requêtes HTTP vers APIs autorisées
- Calculs et analyse
- Génération de code

### Niveau 2 - Modéré (Confirmation requise)
- Installation d'outils système
- Modifications de fichiers
- Accès réseau étendu

### Niveau 3 - Dangereux (Pré-approbation requise)
- Exécution de code arbitraire
- Outils de pentest (nmap, sqlmap, etc.)
- Accès root/sudo
- Manipulation de processus

### Niveau 4 - Critique (Désactivé par défaut)
- Exploitation de vulnérabilités
- Mouvement latéral
- Accès persistence système

## Activation des Fonctions Dangereuses

### Méthode 1: Variable d'environnement
```bash
export SHARINGAN_DANGEROUS_MODE=true
```

### Méthode 2: Fichier de configuration
```bash
echo "dangerous_mode = true" > ~/.sharingan/config
```

### Méthode 3: Confirmation interactive
```
Sharingan: "Je veux exécuter nmap. Autoriser? (oui/non)"
User: "oui"
```

## Sandboxing

Pour toute exécution d'outils dangereux, Sharingan utilise:

1. **Docker** si disponible:
```bash
docker run --rm -v $PWD:/workdir sharingan-tools nmap -sS target
```

2. **gVisor** si disponible:
```bash
runsc --unsafe-none --network-off run --bundle /path/to/bundle nmap -sS target
```

3. **Fallback**: subprocess avec limitations

## Limitations Actuelles

- **Pas d'exécution root par défaut** - Utiliser `user=nobody`
- **Timeouts stricts** - 30 secondes max
- **Quota mémoire** - 512MB max
- **Network isolation** - Par défaut, pas d'accès réseau externe

## Signaler une Vulnérabilité

Pour signaler un problème de sécurité:
1. Ne pas créer d'issue publique
2. Contacter: security@sharingan-os.example.com
3. Décrire le problème avec étapes de reproduction

## Checklist de Sécurité

- [ ] Vérifier `SHARINGAN_DANGEROUS_MODE` avant exécution
- [ ] Confirmer chaque outil dangereux individuellement
- [ ] Utiliser sandbox quand possible
- [ ] Logger toutes les actions sensibles
- [ ] Review régulier des permissions
