#!/usr/bin/env python3
"""
SHARINGAN FAST FILE AUDIT
Audit rapide et optimisé des fichiers lourds
"""

import os
import sys
from pathlib import Path
import time
import subprocess

def fast_large_files_scan():
    """Scan rapide utilisant find au lieu de Python pour la vitesse"""
    print('🚀 SHARINGAN OS - SCAN RAPIDE DES FICHIERS LOURDS')
    print('Utilisation de find pour performance optimale')
    print('=' * 60)

    # Utiliser find pour un scan ultra-rapide
    print('🔍 Recherche des fichiers >200MB avec find...')

    try:
        # Commande find optimisée
        cmd = "find /home /usr /var /opt -type f -size +200M -exec stat -c '%s %Y %n' {} \; 2>/dev/null | head -50"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            large_files = []

            for line in lines:
                if line.strip():
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        size_bytes, mtime, filepath = parts
                        size_mb = int(size_bytes) / (1024 * 1024)
                        modified = time.ctime(int(mtime))

                        large_files.append({
                            'path': filepath,
                            'size_mb': round(size_mb, 2),
                            'modified': modified
                        })

            print(f'✅ Scan terminé - {len(large_files)} fichiers trouvés')

            # Générer rapport
            return generate_fast_report(large_files)

        else:
            print('❌ Erreur lors du scan find')
            return None

    except subprocess.TimeoutExpired:
        print('⏰ Scan interrompu (timeout 5min)')
        return None
    except Exception as e:
        print(f'❌ Erreur: {e}')
        return None

def generate_fast_report(large_files):
    """Générer un rapport rapide"""
    desktop = Path.home() / 'Desktop'
    report_path = desktop / 'SHARINGAN_FAST_AUDIT.txt'

    with open(report_path, 'w') as f:
        f.write('=' * 80 + '\n')
        f.write('SHARINGAN OS - RAPPORT RAPIDE D\'AUDIT\n')
        f.write('Fichiers >200MB - Scan accéléré\n')
        f.write(f'Généré le: {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write('=' * 80 + '\n\n')

        if large_files:
            total_size = sum(f['size_mb'] for f in large_files)
            f.write(f'Fichiers trouvés: {len(large_files)}\n')
            f.write(f'Taille totale: {total_size:.2f} MB\n\n')

            large_files.sort(key=lambda x: x['size_mb'], reverse=True)

            f.write('LISTE DES FICHIERS:\n')
            f.write('-' * 30 + '\n\n')

            for i, file in enumerate(large_files, 1):
                f.write(f'{i}. {file["path"]}\n')
                f.write(f'   Taille: {file["size_mb"]} MB\n')
                f.write(f'   Modifié: {file["modified"]}\n\n')
        else:
            f.write('AUCUN FICHIER >200MB TROUVÉ\n')

        f.write('=' * 80 + '\n')
        f.write('Rapport généré automatiquement par Sharingan OS\n')
        f.write('Système d\'IA autonome et conscient\n')
        f.write('=' * 80 + '\n')

    return report_path

def main():
    start_time = time.time()

    report_path = fast_large_files_scan()

    if report_path:
        duration = time.time() - start_time
        print('.1f'        print(f'📄 Rapport: {report_path}')
        print('✅ Mission accomplie par Sharingan OS !')
    else:
        print('❌ Échec de la mission')

if __name__ == "__main__":
    main()