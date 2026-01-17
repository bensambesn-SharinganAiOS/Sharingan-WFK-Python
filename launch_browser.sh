#!/bin/bash
# Sharingan Browser Launcher
# Ce script lance Chrome et le garde ouvert

echo "======================================================================"
echo "  LANCEMENT NAVIGATEUR YOUTUBE - SHARINGAN"
echo "======================================================================"
echo ""

# Verifier si le navigateur est deja lance
if pgrep -f "sharingan_browser_server" > /dev/null; then
    echo "Un navigateur Sharingan est deja actif!"
    echo ""
    echo "Pour controler le navigateur, utilise:"
    echo "  ./browser_ctl.sh info        - voir la page actuelle"
    echo "  ./browser_ctl.sh navigate URL - naviguer"
    echo "  ./browser_ctl.sh screenshot  - capture d'ecran"
    echo "  ./browser_ctl.sh scroll bas  - defiler vers le bas"
    echo "  ./browser_ctl.sh close       - fermer"
    exit 0
fi

echo "Lancement de Chrome vers YouTube..."

# Lancer le navigateur avec un script Python qui reste ouvert
python3 << 'PYTHON_SCRIPT' &
    import sys
    import os
    sys.path.insert(0, '/root/Projets/Sharingan-WFK-Python')
    
    from sharingan_app._internal.browser_manager import get_browser_manager
    
    bm = get_browser_manager()
    
    search_url = "https://www.youtube.com/results?search_query=aissatou+diop+fall+ngonalou+rewmi+adp+PublicSn"
    
    result = bm.launch('youtube', search_url, browser='chrome', headless=False)
    
    print(f"Navigateur lance: {result['status']}")
    
    if result['status'] == 'success':
        print("")
        print("=" * 70)
        print("  NAVIGATEUR YOUTUBE OUVERT!")
        print("=" * 70)
        print("")
        print("Le navigateur est ouvert sur ton ecran.")
        print("")
        print("Pour le controler, execute dans un AUTRE terminal:")
        echo ""
        echo "  # Voir la page actuelle"
        echo "  python3 -c \"from sharingan_app._internal.browser_manager import get_browser_manager; print(get_browser_manager().get_page_info())\""
        echo ""
        echo "  # Naviguer vers une autre URL"
        echo "  python3 -c \"from sharingan_app._internal.browser_manager import get_browser_manager; get_browser_manager().navigate('https://google.com')\""
        echo ""
        echo "  # Scroller vers le bas"
        echo "  python3 -c \"from sharingan_app._internal.browser_manager import get_browser_manager; get_browser_manager().scroll(500, 'down')\""
        echo ""
        echo "  # Fermer le navigateur"
        echo "  python3 -c \"from sharingan_app._internal.browser_manager import get_browser_manager; get_browser_manager().close()\""
        echo ""
        
        # Garder le navigateur ouvert
        import time
        try:
            while True:
                time.sleep(10)
                # Verifier si le navigateur est toujours actif
                try:
                    info = bm.get_page_info()
                    if info['status'] != 'success':
                        print("Navigateur ferme.")
                        break
                except:
                    print("Navigateur ferme.")
                    break
        except KeyboardInterrupt:
            print("\nFermeture du navigateur...")
            bm.close()
    
    print("Script termine.")
    
PYTHON_SCRIPT

SERVER_PID=$!
echo "Processus serveur PID: $SERVER_PID"
echo ""
echo "Attente de 10 secondes pour le chargement..."
sleep 10

echo ""
echo "Navigateur YouTube devrait etre ouvert sur ton ecran!"
echo ""
echo "TU PEUX MAINTENANT:"
echo "  - Utiliser le navigateur sur ton ecran"
echo "  - Lancer des commandes de controle dans un autre terminal"
echo ""
echo "Pour controler le navigateur:"
echo "  python3 -c \"from sharingan_app._internal.browser_manager import get_browser_manager; bm = get_browser_manager(); bm.navigate('https://google.com')\""
echo ""
echo "Le navigateur RESTERA OUVERT meme si ce script se termine!"
