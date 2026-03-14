#!/usr/bin/env python3
"""
Script pour exécuter tous les tests du projet space-orbital-simulator avec coverage.
"""

import sys
import subprocess
import os
import coverage
from pathlib import Path

def run_tests_with_coverage():
    """Exécute tous les tests avec coverage et génère un rapport."""
    
    # Configuration du coverage
    cov = coverage.Coverage(
        source=['.'],  # Couvre tout le répertoire courant
        omit=[
            'test_*',
            'run_tests.py',
            '*__pycache__*',
            '*.pyc'
        ]
    )
    
    try:
        print("🚀 Lancement des tests avec coverage...")
        print("=" * 60)
        
        # Démarre le coverage
        cov.start()
        
        # Liste des fichiers de test
        test_files = [
            'test_kepler_orbit.py',
            'test_bodies.py',
            'test_exporter.py',
            'test_visualizer.py'
        ]
        
        # Exécute chaque test individuellement
        passed = 0
        total = len(test_files)
        
        for test_file in test_files:
            if not os.path.exists(test_file):
                print(f"❌ Fichier de test manquant: {test_file}")
                continue
                
            print(f"🧪 Test: {test_file}")
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {test_file} - PASS")
                passed += 1
            else:
                print(f"❌ {test_file} - FAIL")
                print(f"Erreur: {result.stderr}")
        
        print("=" * 60)
        print(f"Résumé: {passed}/{total} tests passés")
        
        if passed < total:
            sys.exit(1)
            
    finally:
        # Arrête le coverage et génère les rapports
        cov.stop()
        cov.save()
        
        print("\n📊 Génération des rapports de coverage...")
        
        # Rapport console
        print("\n📈 Couverture du code:")
        cov.report(show_missing=True)
        
        # Rapport HTML
        html_dir = Path("htmlcov")
        html_dir.mkdir(exist_ok=True)
        cov.html_report(directory=html_dir, title="Space Orbital Simulator - Coverage")
        print(f"📂 Rapport HTML généré: file://{os.path.abspath(html_dir)}/index.html")
        
        # Rapport XML (pour CI/CD)
        cov.xml_report(outfile="coverage.xml")
        print("📄 Rapport XML généré: coverage.xml")

def run_tests_simple():
    """Exécute les tests sans coverage (mode rapide)."""
    test_files = [
        'test_kepler_orbit.py',
        'test_bodies.py',
        'test_exporter.py',
        'test_visualizer.py'
    ]
    
    passed = 0
    total = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            total += 1
            print(f"🧪 {test_file}")
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ PASS")
                passed += 1
            else:
                print(f"❌ FAIL")
                print(result.stderr)
    
    print(f"\n📊 Résumé: {passed}/{total} tests passés")
    return passed == total

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Exécuter les tests du space-orbital-simulator")
    parser.add_argument('--simple', '-s', action='store_true',
                       help="Mode rapide sans coverage")
    parser.add_argument('--coverage', '-c', action='store_true',
                       help="Générer rapport de coverage (défaut)")
    
    args = parser.parse_args()
    
    if args.simple:
        success = run_tests_simple()
    else:
        run_tests_with_coverage()
        success = True
    
    sys.exit(0 if success else 1)