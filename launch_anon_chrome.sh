#!/bin/bash
# SCRIPT POUR LANCER CHROME AVEC TOR

echo "🛡️ LANCEMENT CHROME ANONYME AVEC TOR"
echo "==================================="

# Vérifier Tor
echo "🔍 Vérification Tor..."
if systemctl is-active --quiet tor; then
    echo "✅ Tor actif"
else
    echo "🔄 Activation Tor..."
    sudo systemctl start tor
    sleep 3
fi

# Créer profil temporaire
PROFILE_DIR="/tmp/anon-chrome-profile"
mkdir -p "$PROFILE_DIR"

echo "🚀 Lancement Chrome avec proxy Tor..."
echo "📁 Profil: $PROFILE_DIR"
echo "🔗 Proxy: socks5://127.0.0.1:9050"
echo ""

# Lancer Chrome avec Tor
google-chrome \
    --proxy-server="socks5://127.0.0.1:9050" \
    --host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1" \
    --user-data-dir="$PROFILE_DIR" \
    --incognito \
    --no-first-run \
    --disable-default-apps \
    --disable-sync \
    --disable-translate \
    --hide-crash-restore-bubble \
    --new-window \
    "https://www.whatsmyip.org/" &

CHROME_PID=$!
echo "✅ Chrome lancé (PID: $CHROME_PID)"
echo ""
echo "🎯 INSTRUCTIONS:"
echo "1. Vérifiez que l'IP affichée est: 194.26.192.46 (IP Tor)"
echo "2. Si c'est 154.124.15.146, l'anonymat ne fonctionne pas"
echo "3. Fermez Chrome pour revenir à la navigation normale"
echo ""
echo "💡 Laissez Chrome ouvert et testez d'autres sites !"

# Attendre que l'utilisateur ferme Chrome
wait $CHROME_PID

echo ""
echo "🧹 Nettoyage..."
rm -rf "$PROFILE_DIR"
echo "✅ Profil Chrome nettoyé"
