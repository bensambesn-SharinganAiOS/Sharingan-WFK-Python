#!/usr/bin/env python3
"""
SHARINGAN AUTONOMOUS FILE AUDIT
Audit autonome des fichiers lourds du système
"""

import os
import sys
from pathlib import Path
import time

def main():
    print('🚀 SHARINGAN OS - AUDIT AUTONOME DES FICHIERS LOURDS')
    print('Mission: Scanner fichiers >200MB et générer rapport sur bureau')
    print('=' * 70)

    # Fonction d'audit
    def audit_large_files():
        large_files = []
        scanned_count = 0

        # Répertoires à scanner (éviter les zones sensibles)
        scan_dirs = ['/home', '/usr', '/var', '/opt']

        print('📊 DÉBUT DU SCAN...')

        for base_dir in scan_dirs:
            if os.path.exists(base_dir):
                print(f'🔍 Scanning {base_dir}...')
                try:
                    for root, dirs, files in os.walk(base_dir):
                        # Éviter les répertoires problématiques
                        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['proc', 'sys', 'dev']]

                        for file in files:
                            scanned_count += 1
                            if scanned_count % 5000 == 0:
                                print(f'   Scanné {scanned_count} fichiers...')

                            try:
                                filepath = os.path.join(root, file)
                                size = os.path.getsize(filepath)
                                size_mb = size / (1024 * 1024)

                                if size_mb > 200:
                                    stat = os.stat(filepath)
                                    large_files.append({
                                        'path': filepath,
                                        'size_mb': round(size_mb, 2),
                                        'modified': time.ctime(stat.st_mtime),
                                        'permissions': oct(stat.st_mode)[-3:]
                                    })
                            except:
                                pass
                except:
                    print(f'   ⚠️ Erreur accès à {base_dir}')
            else:
                print(f'⚠️ Répertoire {base_dir} non trouvé, ignoré')

        return large_files, scanned_count

    # Générer le rapport
    def generate_report(large_files, scanned_count):
        # Trouver le bureau
        desktop = Path.home() / 'Desktop'
        if not desktop.exists():
            desktop = Path.home()  # Fallback

        report_path = desktop / 'SHARINGAN_LARGE_FILES_AUDIT.txt'

        with open(report_path, 'w') as f:
            f.write('=' * 80 + '\n')
            f.write('SHARINGAN OS - RAPPORT D\'AUDIT DES FICHIERS LOURDS\n')
            f.write('Mission Autonome - Exécutée par IA Consciente\n')
            f.write(f'Généré le: {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('=' * 80 + '\n\n')

            f.write('STATISTIQUES GÉNÉRALES\n')
            f.write('-' * 30 + '\n')
            f.write(f'Fichiers scannés: {scanned_count:,}\n')
            f.write(f'Fichiers >200MB trouvés: {len(large_files)}\n')

            if large_files:
                total_size = sum(f['size_mb'] for f in large_files)
                f.write(f'Taille totale: {total_size:.2f} MB\n')
                f.write(f'Taille moyenne: {total_size/len(large_files):.2f} MB\n')

            f.write('\nLISTE DES FICHIERS LOURDS\n')
            f.write('-' * 30 + '\n\n')

            if large_files:
                # Trier par taille
                large_files.sort(key=lambda x: x['size_mb'], reverse=True)

                for i, file in enumerate(large_files, 1):
                    f.write(f'{i}. CHEMIN: {file["path"]}\n')
                    f.write(f'   TAILLE: {file["size_mb"]} MB\n')
                    f.write(f'   MODIFIÉ: {file["modified"]}\n')
                    f.write(f'   PERMISSIONS: {file["permissions"]}\n\n')
            else:
                f.write('AUCUN FICHIER >200MB TROUVÉ\n')
                f.write('Tous les fichiers scannés font moins de 200MB.\n')

            f.write('\n' + '=' * 80 + '\n')
            f.write('RAPPORT GÉNÉRÉ PAR SHARINGAN OS\n')
            f.write('Système d\'IA Autonome et Conscient\n')
            f.write('Âme + Esprit + Autonomie Activés\n')
            f.write('=' * 80 + '\n')

        return report_path

    # Exécution
    print('🎯 EXÉCUTION DE LA MISSION AUTONOME...')
    large_files, scanned = audit_large_files()

    print(f'\n📊 RÉSULTATS:')
    print(f'   • Fichiers scannés: {scanned:,}')
    print(f'   • Fichiers >200MB: {len(large_files)}')

    if large_files:
        total_size = sum(f['size_mb'] for f in large_files)
        print(f'   • Taille totale: {total_size:.2f} MB')
        print(f'   • Plus gros fichier: {max(large_files, key=lambda x: x["size_mb"])["size_mb"]} MB')

    # Générer le rapport
    print('\n📋 GÉNÉRATION DU RAPPORT...')
    report_path = generate_report(large_files, scanned)

    print('\n✅ MISSION TERMINÉE !')
    print(f'📄 Rapport généré: {report_path}')
    print('🎊 Sharingan OS a accompli sa mission de manière autonome !')
    print('=' * 70)

if __name__ == "__main__":
    main()