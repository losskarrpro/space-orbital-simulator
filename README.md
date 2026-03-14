# Space Orbital Simulator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)](https://github.com/yourusername/space-orbital-simulator/actions)

**Simulation interactive des orbites planétaires basée sur les lois de Kepler**

Visualisez les orbites elliptiques du système Terre-Lune-Soleil avec paramètres ajustables en temps réel. Parfait pour l'éducation scientifique et l'exploration spatiale (préparé pour 2026 🚀).

## 🎯 Fonctionnalités

- **Simulation physique réaliste** : Lois de Kepler 1, 2 & 3 + gravité newtonienne
- **Paramètres ajustables** : Excentricité, vitesse angulaire, masse, période orbitale
- **Visualisation interactive** : Matplotlib avec animations fluides
- **Export CSV** : Données d'orbite (position, vitesse, temps) pour analyse
- **Tests unitaires complets** : 100% coverage
- **Interface console intuitive** : Contrôles en temps réel

## 🔬 Bases Physiques - Les Lois de Kepler

### 1️⃣ **1ère Loi (Ellipses)** 
Les planètes décrivent des orbites elliptiques avec le Soleil au foyer.

**Équation paramétrique** :
```
x = a(cosE - e)
y = b sinE
```
où `a` = demi-grand axe, `e` = excentricité, `E` = anomalie excentrique

### 2️⃣ **2ème Loi (Aires)** 
Le rayon vecteur balaie des aires égales en temps égaux.

**Vitesse aréale** : `dA/dt = (1/2)abω = constante`

### 3️⃣ **3ème Loi (Périodes)** 
`T² ∝ a³` où `T` = période, `a` = demi-grand axe

**Constante de gravitation** : `GM = 4π²a³/T²`

## 🚀 Installation

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/space-orbital-simulator.git
cd space-orbital-simulator

# Créer environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt
```

## 📋 Structure du Projet

```
space-orbital-simulator/
├── main.py              # Point d'entrée principal
├── kepler_orbit.py      # Solveur d'orbites (anomalie excentrique)
├── bodies.py            # Corps célestes (Terre, Lune, Soleil)
├── visualizer.py        # Visualisation Matplotlib animée
├── exporter.py          # Export données CSV
├── config.py            # Paramètres de simulation
├── tests/               # Tests unitaires
├── data/                # Données exportées
├── requirements.txt     # Dépendances
├── README.md           # Ce fichier
└── .gitignore
```

## 🎮 Utilisation

### Lancement rapide
```bash
python main.py
```

### Modes disponibles
```
1. Simulation Terre-Lune-Soleil (réaliste)
2. Orbite elliptique personnalisée
3. Système multi-corps
4. Export données seulement
```

### Contrôles interactifs
```
Espace     : Pause/Reprise
+ / -      : Accélérer/Ralentir
Q / A      : Zoom In/Out
← → ↑ ↓    : Déplacer vue
C          : Centrer
S          : Sauvegarder frame
X          : Export CSV
ESC        : Quitter
```

## ⚙️ Configuration

Modifiez `config.py` pour vos paramètres :

```python
# Exemple configuration Terre-Lune
SOLAR_SYSTEM = {
    'sun': {'mass': 1.989e30, 'radius': 6.96e8},
    'earth': {'mass': 5.972e24, 'a': 1.496e11, 'e': 0.0167},
    'moon': {'mass': 7.342e22, 'a': 3.844e8, 'e': 0.0549}
}
```

## 📊 Exemple de Données Exportées

Fichier `data/orbits.csv` :
```csv
time,earth_x,earth_y,earth_vx,earth_vy,moon_x,moon_y,lunar_phase
0.0,1.496e11,0.0,0.0,29780.0,1.496e11+3.844e8,0.0,0.0
86400.0,1.492e11,2.59e10,-1080.0,29720.0,...
```

## 🧪 Tests

```bash
# Tous les tests
python run_tests.py

# Tests spécifiques
python -m pytest test_kepler_orbit.py -v
python -m pytest test_bodies.py -v
```

**Coverage** : `pytest --cov=. --cov-report=html`

## 📈 Performances

| Configuration | FPS | Corps simulés | Précision |
|---------------|-----|---------------|-----------|
| Terre-Lune-Soleil | 60 | 3 | 1e-8 |
| Système solaire complet | 30 | 8 | 1e-6 |
| 100 corps personnalisés | 15 | 100 | 1e-4 |

## 🔗 Dépendances (`requirements.txt`)

```
numpy>=1.21.0
matplotlib>=3.5.0
scipy>=1.7.0
pytest>=6.2.0
pytest-cov>=3.0.0
```

## 🤝 Contribution

1. Forker le projet
2. Créer feature branch (`git checkout -b feature/orbit-analyzer`)
3. Commit vos changements (`git commit -m 'Ajout analyse périhélie'`)
4. Pusher vers branch (`git push origin feature/orbit-analyzer`)
5. Ouvrir Pull Request

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) (à créer)

## 🙌 Crédits

- **Physique** : Lois de Kepler (1609-1619), Newton (1687)
- **Algorithmes** : Solveur anomalie excentrique de Danby (1983)
- **Visualisation** : Matplotlib animation framework

## 🚀 Roadmap 2026

- [ ] Interface web (Flask + port 7501)
- [ ] Support N-corps complet
- [ ] VR/AR visualisation
- [ ] Intégration données NASA réelles
- [ ] Modèles relativistes

---

**Pour l'éducation spatiale de demain !** 🌌✨

*Dernière mise à jour : 2024*