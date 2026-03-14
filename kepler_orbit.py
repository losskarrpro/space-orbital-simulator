import numpy as np
from scipy.optimize import newton
import math

class KeplerOrbit:
    """
    Classe principale pour les calculs orbitaux basés sur les lois de Kepler.
    Supporte les orbites elliptiques avec paramètres ajustables.
    """
    
    def __init__(self, semi_major_axis, eccentricity, true_anomaly=0.0, 
                 gravitational_parameter=1.327e20, time_step=0.01):
        """
        Initialise une orbite keplérienne.
        
        Args:
            semi_major_axis (float): Demi-grand axe (m)
            eccentricity (float): Excentricité (0 <= e < 1)
            true_anomaly (float): Anomalie vraie initiale (radians)
            gravitational_parameter (float): Paramètre gravitationnel μ (m³/s²)
            time_step (float): Pas de temps pour intégration (s)
        """
        if eccentricity >= 1.0:
            raise ValueError("Excentricité doit être < 1 pour orbite elliptique")
        
        self.a = semi_major_axis  # Demi-grand axe
        self.e = eccentricity     # Excentricité
        self.nu = true_anomaly    # Anomalie vraie
        self.mu = gravitational_parameter
        self.dt = time_step
        
        # Paramètres dérivés
        self.p = self.a * (1 - self.e**2)  # Paramètre de l'orbite
        self.period = 2 * np.pi * np.sqrt(self.a**3 / self.mu)  # Période orbitale
        
    def get_position(self):
        """
        Calcule la position cartésienne (r, θ) à l'anomalie vraie actuelle.
        
        Returns:
            tuple: (r, theta) en coordonnées polaires
        """
        r = self.p / (1 + self.e * np.cos(self.nu))
        return r, self.nu
    
    def get_cartesian_position(self):
        """
        Position en coordonnées cartésiennes (x, y).
        
        Returns:
            tuple: (x, y)
        """
        r, theta = self.get_position()
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y
    
    def true_to_eccentric_anomaly(self, nu):
        """
        Convertit anomalie vraie vers anomalie excentrique.
        
        Args:
            nu (float): Anomalie vraie (radians)
            
        Returns:
            float: Anomalie excentrique E (radians)
        """
        def kepler_eq(E):
            return E - self.e * np.sin(E) - nu
        
        E0 = nu  # Approximation initiale
        return newton(kepler_eq, E0)
    
    def eccentric_to_mean_anomaly(self, E):
        """
        Convertit anomalie excentrique vers anomalie moyenne.
        
        Args:
            E (float): Anomalie excentrique (radians)
            
        Returns:
            float: Anomalie moyenne M (radians)
        """
        return E - self.e * np.sin(E)
    
    def update_orbit(self, delta_time=None):
        """
        Met à jour l'orbite sur un pas de temps.
        
        Args:
            delta_time (float, optional): Pas de temps personnalisé
            
        Returns:
            tuple: Position mise à jour (x, y)
        """
        if delta_time is None:
            delta_time = self.dt
            
        # Anomalie vraie précédente pour calcul de vitesse angulaire
        nu_prev = self.nu
        
        # Anomalie moyenne M = n * t (n = vitesse moyenne angulaire)
        n = np.sqrt(self.mu / self.a**3)
        M = n * delta_time
        
        # Résolution de l'équation de Kepler pour nouvelle anomalie excentrique
        def kepler_eq(E):
            return E - self.e * np.sin(E) - M
        
        E_new = newton(kepler_eq, M)
        
        # Nouvelle anomalie vraie
        self.nu = 2 * np.arctan2(
            np.sqrt(1 + self.e) * np.sin(E_new / 2),
            np.sqrt(1 - self.e) * np.cos(E_new / 2)
        )
        
        return self.get_cartesian_position()
    
    def get_orbit_trajectory(self, num_points=1000):
        """
        Génère la trajectoire complète de l'orbite.
        
        Args:
            num_points (int): Nombre de points
            
        Returns:
            np.ndarray: Tableau de positions [x, y]
        """
        nu_array = np.linspace(0, 2*np.pi, num_points)
        positions = []
        
        for nu in nu_array:
            r = self.p / (1 + self.e * np.cos(nu))
            x = r * np.cos(nu)
            y = r * np.sin(nu)
            positions.append([x, y])
            
        return np.array(positions)
    
    def get_orbital_elements(self):
        """
        Retourne tous les éléments orbitaux.
        
        Returns:
            dict: Éléments orbitaux
        """
        return {
            'semi_major_axis': self.a,
            'eccentricity': self.e,
            'period': self.period,
            'semi_latus_rectum': self.p,
            'true_anomaly': self.nu
        }
    
    def simulate_orbit(self, total_time, num_steps=None):
        """
        Simule l'orbite sur une durée totale.
        
        Args:
            total_time (float): Durée totale de simulation (s)
            num_steps (int, optional): Nombre d'étapes
            
        Returns:
            dict: Historique des positions et temps
        """
        if num_steps is None:
            num_steps = int(total_time / self.dt)
            
        times = np.zeros(num_steps)
        positions = np.zeros((num_steps, 2))
        
        for i in range(num_steps):
            times[i] = i * self.dt
            positions[i] = self.update_orbit(self.dt)
            
        return {
            'time': times,
            'positions': positions,
            'elements': self.get_orbital_elements()
        }
    
    def reset(self, true_anomaly=0.0):
        """Remet l'orbite à l'anomalie vraie spécifiée."""
        self.nu = true_anomaly
    
    @staticmethod
    def earth_orbit():
        """Orbite terrestre standard."""
        return KeplerOrbit(
            semi_major_axis=1.496e11,  # 1 AU
            eccentricity=0.0167,
            gravitational_parameter=1.327e20  # μ_Soleil
        )
    
    @staticmethod
    def moon_orbit():
        """Orbite lunaire standard."""
        return KeplerOrbit(
            semi_major_axis=3.844e8,
            eccentricity=0.0549,
            gravitational_parameter=3.986e14  # μ_Terre
        )