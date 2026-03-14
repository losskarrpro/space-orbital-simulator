"""
bodies.py - Modèles des corps célestes (Soleil, Terre, Lune) avec paramètres orbitaux ajustables
Pour la simulation d'orbites selon la loi de Kepler
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
import math

@dataclass
class CelestialBody:
    """Classe de base pour un corps céleste"""
    name: str
    mass: float  # kg
    radius: float  # m
    color: str
    position: np.ndarray = np.array([0.0, 0.0])
    velocity: np.ndarray = np.array([0.0, 0.0])
    
    def __post_init__(self):
        self.position = np.array(self.position, dtype=float)
        self.velocity = np.array(self.velocity, dtype=float)

class Sun(CelestialBody):
    """Modèle du Soleil"""
    def __init__(self):
        super().__init__(
            name="Soleil",
            mass=1.989e30,  # kg
            radius=6.96e8,  # m
            color="#FFD700",
            position=np.array([0.0, 0.0]),
            velocity=np.array([0.0, 0.0])
        )

class Earth(CelestialBody):
    """Modèle de la Terre avec orbite elliptique ajustable autour du Soleil"""
    def __init__(
        self,
        semi_major_axis: float = 1.496e11,  # m (1 UA)
        eccentricity: float = 0.0167,
        true_anomaly: float = 0.0,
        orbital_speed_factor: float = 1.0
    ):
        # Paramètres orbitaux Terre-Soleil
        self.semi_major_axis = semi_major_axis
        self.eccentricity = max(0.0, min(0.99, eccentricity))  # Limite excentricité
        self.true_anomaly = true_anomaly
        self.orbital_speed_factor = orbital_speed_factor
        
        # Position initiale selon anomalie vraie
        self._update_position_from_orbit()
        
        # Vitesse orbitale (calculée via conservation de l'énergie angulaire)
        self.velocity = self._calculate_orbital_velocity()
        
        super().__init__(
            name="Terre",
            mass=5.972e24,  # kg
            radius=6.371e6,  # m
            color="#4169E1",
            position=self.position,
            velocity=self.velocity
        )
    
    def _update_position_from_orbit(self):
        """Calcule la position selon les paramètres orbitaux de Kepler"""
        # Distance radiale r = a(1-e²)/(1+ecosθ)
        r = self.semi_major_axis * (1 - self.eccentricity**2) / (1 + self.eccentricity * np.cos(self.true_anomaly))
        
        # Coordonnées polaires vers cartésiennes
        self.position = np.array([
            r * np.cos(self.true_anomaly),
            r * np.sin(self.true_anomaly)
        ])
    
    def _calculate_orbital_velocity(self) -> np.ndarray:
        """Calcule la vitesse orbitale tangentielle"""
        # Constante gravitationnelle
        G = 6.67430e-11
        mu = G * 1.989e30  # Paramètre gravitationnel Soleil
        
        # Distance radiale
        r = np.linalg.norm(self.position)
        
        # Vitesse orbitale (v = sqrt[μ(2/r - 1/a)])
        v_magnitude = np.sqrt(mu * (2/r - 1/self.semi_major_axis)) * self.orbital_speed_factor
        
        # Direction tangentielle (perpendiculaire à la position)
        position_unit = self.position / r
        tangent_unit = np.array([-position_unit[1], position_unit[0]])
        
        return v_magnitude * tangent_unit
    
    def update_orbit(self, delta_time: float, dt_anomaly: float = 0.01):
        """Met à jour la position orbitale"""
        self.true_anomaly += dt_anomaly * self.orbital_speed_factor
        self._update_position_from_orbit()
        self.velocity = self._calculate_orbital_velocity()

class Moon(CelestialBody):
    """Modèle de la Lune en orbite autour de la Terre"""
    def __init__(
        self,
        earth_position: np.ndarray,
        semi_major_axis: float = 3.844e8,  # m
        eccentricity: float = 0.0549,
        true_anomaly: float = 0.0,
        orbital_speed_factor: float = 1.0
    ):
        self.semi_major_axis = semi_major_axis
        self.eccentricity = max(0.0, min(0.99, eccentricity))
        self.true_anomaly = true_anomaly
        self.orbital_speed_factor = orbital_speed_factor
        self.earth_position = earth_position.copy()
        
        # Position relative à la Terre
        self._update_moon_position()
        absolute_position = self.earth_position + self.position
        
        # Vitesse relative + vitesse de la Terre
        relative_velocity = self._calculate_moon_velocity()
        super_velocity = np.array([0.0, 0.0])  # À ajuster si Terre en mouvement
        
        super().__init__(
            name="Lune",
            mass=7.342e22,  # kg
            radius=1.737e6,  # m
            color="#C0C0C0",
            position=absolute_position,
            velocity=relative_velocity + super_velocity
        )
    
    def _update_moon_position(self):
        """Met à jour la position relative à la Terre"""
        r = self.semi_major_axis * (1 - self.eccentricity**2) / \
            (1 + self.eccentricity * np.cos(self.true_anomaly))
        
        self.position = np.array([
            r * np.cos(self.true_anomaly),
            r * np.sin(self.true_anomaly)
        ])
    
    def _calculate_moon_velocity(self) -> np.ndarray:
        """Calcule la vitesse orbitale de la Lune autour de la Terre"""
        G = 6.67430e-11
        mu_earth = G * 5.972e24  # Terre
        
        r = np.linalg.norm(self.position)
        v_magnitude = np.sqrt(mu_earth * (2/r - 1/self.semi_major_axis)) * self.orbital_speed_factor
        
        position_unit = self.position / r
        tangent_unit = np.array([-position_unit[1], position_unit[0]])
        
        return v_magnitude * tangent_unit
    
    def update_orbit(self, earth_position: np.ndarray, delta_time: float, dt_anomaly: float = 0.013):
        """Met à jour l'orbite de la Lune autour de la nouvelle position de la Terre"""
        self.earth_position = earth_position.copy()
        self.true_anomaly += dt_anomaly * self.orbital_speed_factor
        self._update_moon_position()
        self.position = self.earth_position + self.position
        self.velocity = self._calculate_moon_velocity()

class SolarSystem:
    """Système solaire simplifié (Soleil + Terre + Lune)"""
    def __init__(
        self,
        earth_eccentricity: float = 0.0167,
        moon_eccentricity: float = 0.0549,
        earth_speed_factor: float = 1.0,
        moon_speed_factor: float = 1.0
    ):
        self.sun = Sun()
        self.earth = Earth(
            eccentricity=earth_eccentricity,
            orbital_speed_factor=earth_speed_factor
        )
        self.moon = Moon(
            earth_position=self.earth.position,
            eccentricity=moon_eccentricity,
            orbital_speed_factor=moon_speed_factor
        )
        
        self.bodies: List[CelestialBody] = [self.sun, self.earth, self.moon]
        self.time = 0.0
    
    def update(self, delta_time: float):
        """Met à jour toutes les positions"""
        # Mise à jour Terre autour du Soleil
        self.earth.update_orbit(delta_time)
        
        # Mise à jour Lune autour de la Terre
        self.moon.update_orbit(self.earth.position, delta_time)
        
        self.time += delta_time
    
    def get_body_positions(self) -> Dict[str, np.ndarray]:
        """Retourne les positions de tous les corps"""
        return {body.name: body.position for body in self.bodies}
    
    def get_body_data(self) -> List[Dict]:
        """Retourne les données complètes pour export"""
        data = []
        for body in self.bodies:
            data.append({
                'time': self.time,
                'name': body.name,
                'x': body.position[0],
                'y': body.position[1],
                'vx': body.velocity[0],
                'vy': body.velocity[1],
                'mass': body.mass
            })
        return data
    
    def set_earth_eccentricity(self, ecc: float):
        """Ajuste l'excentricité de l'orbite terrestre"""
        self.earth.eccentricity = max(0.0, min(0.99, ecc))
        self.earth._update_position_from_orbit()
        self.earth.velocity = self.earth._calculate_orbital_velocity()
        self.moon.earth_position = self.earth.position.copy()
        self.moon.update_orbit(self.earth.position, 0.0)
    
    def set_parameters(self, params: Dict[str, float]):
        """Ajuste les paramètres du système"""
        if 'earth_ecc' in params:
            self.set_earth_eccentricity(params['earth_ecc'])
        if 'earth_speed' in params:
            self.earth.orbital_speed_factor = params['earth_speed']
        if 'moon_ecc' in params:
            self.moon.eccentricity = max(0.0, min(0.99, params['moon_ecc']))
        if 'moon_speed' in params:
            self.moon.orbital_speed_factor = params['moon_speed']

def create_default_system() -> SolarSystem:
    """Crée le système solaire par défaut"""
    return SolarSystem()

if __name__ == "__main__":
    # Test unitaire simple
    system = create_default_system()
    print("Système solaire initialisé:")
    print(f"Terre à: {system.earth.position}")
    print(f"Lune à: {system.moon.position}")
    print(f"Excentricité Terre: {system.earth.eccentricity}")