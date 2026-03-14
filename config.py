"""
Configuration centrale pour le simulateur orbital.
Constantes physiques et paramètres par défaut.
"""

import numpy as np
from typing import Dict, Any

# Constantes physiques (SI)
GRAVITATIONAL_CONSTANT = 6.67430e-11  # m³ kg⁻¹ s⁻²
AU = 1.495978707e11  # m (Unité Astronomique)
SOLAR_MASS = 1.989e30  # kg
EARTH_MASS = 5.972e24  # kg
MOON_MASS = 7.342e22  # kg

# Paramètres d'affichage
SCALE_FACTOR = 1e9  # Échelle pour visualisation (m -> pixels)
DT_SIMULATION = 3600  # Pas de temps simulation (1h en secondes)
MAX_SIM_STEPS = 10000  # Nombre max d'étapes de simulation

# Système Terre-Lune-Soleil par défaut
DEFAULT_CONFIG = {
    "bodies": {
        "Soleil": {
            "mass": SOLAR_MASS,
            "position": [0.0, 0.0],
            "velocity": [0.0, 0.0],
            "radius": 6.96e8,
            "color": "#FFD700",
            "fixed": True
        },
        "Terre": {
            "mass": EARTH_MASS,
            "position": [AU, 0.0],
            "velocity": [0.0, 29.78e3],  # ~30 km/s
            "radius": 6.371e6,
            "color": "#4169E1",
            "fixed": False
        },
        "Lune": {
            "mass": MOON_MASS,
            "position": [AU + 3.844e8, 0.0],
            "velocity": [0.0, 29.78e3 + 1022],  # Vitesse orbitale Terre + Lune
            "radius": 1.737e6,
            "color": "#C0C0C0",
            "fixed": False
        }
    },
    "simulation": {
        "time_scale": 1000.0,  # Accélérateur temps réel
        "duration": 365.25 * 24 * 3600,  # 1 année en secondes
        "export_interval": 100  # Sauvegarde tous les N pas
    },
    "visualization": {
        "window_width": 1400,
        "window_height": 1000,
        "background_color": "#000011",
        "show_trails": True,
        "trail_length": 5000,
        "show_orbit_lines": True
    },
    "orbits": {
        "terre": {
            "semi_major_axis": 1.0,  # AU
            "eccentricity": 0.0167,
            "inclination": 0.0  # radians
        },
        "lune": {
            "semi_major_axis": 0.00257,  # AU
            "eccentricity": 0.0549,
            "inclination": 5.145 * np.pi / 180  # radians
        }
    }
}

# Paramètres ajustables utilisateur
ADJUSTABLE_PARAMS = {
    "terre_eccentricity": {"min": 0.0, "max": 0.5, "default": 0.0167, "step": 0.001},
    "lune_eccentricity": {"min": 0.0, "max": 0.3, "default": 0.0549, "step": 0.001},
    "time_scale": {"min": 1.0, "max": 10000.0, "default": 1000.0, "step": 100.0},
    "simulation_speed": {"min": 0.1, "max": 10.0, "default": 1.0, "step": 0.1}
}

# Ports pour interface web (si activée)
WEB_PORT = 7501
WEB_HOST = "127.0.0.1"

# Chemins fichiers
DATA_DIR = "data"
EXPORT_CSV = f"{DATA_DIR}/orbits.csv"

# Couleurs par défaut
COLORS = {
    "Soleil": "#FFD700",
    "Terre": "#4169E1", 
    "Lune": "#C0C0C0",
    "Mars": "#CD5C5C",
    "Jupiter": "#D8CA9D"
}

def get_default_config() -> Dict[str, Any]:
    """Retourne la configuration par défaut."""
    return DEFAULT_CONFIG.copy()

def validate_config(config: Dict[str, Any]) -> bool:
    """Valide la cohérence de la configuration."""
    required_keys = ["bodies", "simulation", "visualization"]
    return all(key in config for key in required_keys)