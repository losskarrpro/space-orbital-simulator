"""
exporter.py - Export des données de simulation vers CSV
Exporte positions, vitesses, temps et autres paramètres des corps célestes.
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any
import numpy as np
from bodies import CelestialBody


class OrbitExporter:
    """Classe pour exporter les données d'orbite vers CSV."""
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_simulation(
        self,
        bodies: List[CelestialBody],
        times: np.ndarray,
        positions: np.ndarray,
        velocities: np.ndarray,
        energies: np.ndarray = None,
        filename: str = None
    ) -> str:
        """
        Exporte une simulation complète vers CSV.
        
        Args:
            bodies: Liste des corps célestes
            times: Tableau des temps (s)
            positions: Tableau des positions [N, num_bodies, 3]
            velocities: Tableau des vitesses [N, num_bodies, 3]
            energies: Tableau des énergies (optionnel)
            filename: Nom du fichier (auto-généré si None)
        
        Returns:
            Chemin du fichier CSV généré
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"orbits_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        num_steps, num_bodies, _ = positions.shape
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # En-tête
            header = ['time_s', 'step']
            for i, body in enumerate(bodies):
                header.extend([
                    f'{body.name}_x_km',
                    f'{body.name}_y_km', 
                    f'{body.name}_z_km',
                    f'{body.name}_vx_km_s',
                    f'{body.name}_vy_km_s',
                    f'{body.name}_vz_km_s',
                    f'{body.name}_speed_km_s',
                    f'{body.name}_distance_km'
                ])
            
            if energies is not None:
                for i in range(num_bodies):
                    header.extend([f'body_{i}_energy_J'])
            
            writer.writerow(header)
            
            # Données
            for step in range(num_steps):
                row = [times[step], step]
                
                for i in range(num_bodies):
                    pos = positions[step, i]
                    vel = velocities[step, i]
                    
                    speed = np.linalg.norm(vel)
                    distance = np.linalg.norm(pos)
                    
                    row.extend([
                        pos[0], pos[1], pos[2],
                        vel[0], vel[1], vel[2],
                        speed, distance
                    ])
                
                if energies is not None:
                    row.extend(energies[step])
                
                writer.writerow([f"{x:.6f}" if isinstance(x, (int, float)) else x for x in row])
        
        return filepath
    
    def export_body_summary(
        self,
        bodies: List[CelestialBody],
        filename: str = "bodies_summary.csv"
    ) -> str:
        """Exporte un résumé des propriétés des corps."""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'name', 'mass_kg', 'radius_km', 'mu_km3_s2',
                'semi_major_axis_km', 'eccentricity', 'inclination_rad',
                'period_s', 'color'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for body in bodies:
                writer.writerow({
                    'name': body.name,
                    'mass_kg': f"{body.mass:.2e}",
                    'radius_km': body.radius,
                    'mu_km3_s2': f"{body.mu:.2e}",
                    'semi_major_axis_km': body.semi_major_axis,
                    'eccentricity': body.eccentricity,
                    'inclination_rad': body.inclination,
                    'period_s': body.period,
                    'color': body.color
                })
        
        return filepath
    
    def export_kepler_elements(
        self,
        bodies: List[CelestialBody],
        filename: str = "kepler_elements.csv"
    ) -> str:
        """Exporte les éléments de Kepler pour chaque corps."""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'name', 'a_km', 'e', 'i_rad', 'Omega_rad', 'omega_rad', 'nu_rad'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for body in bodies:
                writer.writerow({
                    'name': body.name,
                    'a_km': body.semi_major_axis,
                    'e': body.eccentricity,
                    'i_rad': body.inclination,
                    'Omega_rad': body.longitude_ascending_node,
                    'omega_rad': body.argument_periapsis,
                    'nu_rad': 0.0  # Anomalie vraie initiale
                })
        
        return filepath
    
    def export_multiple_simulations(
        self,
        simulations: List[Dict[str, Any]],
        base_filename: str = "simulation_batch"
    ) -> List[str]:
        """
        Exporte plusieurs simulations en batch.
        
        Args:
            simulations: Liste de dicts avec 'bodies', 'times', 'positions', 'velocities'
            base_filename: Nom de base pour les fichiers
        
        Returns:
            Liste des chemins des fichiers générés
        """
        files = []
        for i, sim in enumerate(simulations):
            filename = f"{base_filename}_sim_{i+1}.csv"
            filepath = self.export_simulation(
                sim['bodies'], sim['times'], sim['positions'], sim['velocities'],
                filename=filename
            )
            files.append(filepath)
        return files


def main():
    """Exemple d'utilisation de l'exporteur."""
    from bodies import Earth, Moon, Sun
    import numpy as np
    
    # Corps de test
    bodies = [Sun(), Earth(), Moon()]
    
    # Données simulées
    num_steps = 1000
    times = np.linspace(0, 30*24*3600, num_steps)  # 30 jours
    positions = np.random.rand(num_steps, 3, 3) * 1e8
    velocities = np.random.rand(num_steps, 3, 3) * 1e3
    
    exporter = OrbitExporter()
    filepath = exporter.export_simulation(bodies, times, positions, velocities)
    print(f"Simulation exportée: {filepath}")
    
    summary_path = exporter.export_body_summary(bodies)
    print(f"Résumé exporté: {summary_path}")


if __name__ == "__main__":
    main()