#!/usr/bin/env python3
"""
Space Orbital Simulator - Application principale
Simulation interactive des orbites planétaires selon la loi de Kepler
"""

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button, RadioButtons

from config import Config
from kepler_orbit import KeplerOrbit
from bodies import CelestialBody, SolarSystem
from visualizer import OrbitVisualizer
from exporter import OrbitExporter

class OrbitalSimulator:
    def __init__(self, config):
        self.config = config
        self.solar_system = SolarSystem()
        self.visualizer = OrbitVisualizer(config)
        self.exporter = OrbitExporter()
        self.orbit_calculator = KeplerOrbit()
        
        # Paramètres de simulation
        self.time = 0.0
        self.dt = config.timestep
        self.running = False
        
        # Corps principaux
        self.primary = self.solar_system.bodies['Sun']
        self.secondary = self.solar_system.bodies['Earth']
        self.moon = self.solar_system.bodies['Moon']
        
        # Figure et axes
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.fig.suptitle('Space Orbital Simulator - Lois de Kepler', fontsize=16, fontweight='bold')
        
        # Interface utilisateur
        self.setup_ui()
        
        # Animation
        self.ani = None
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur interactive"""
        self.ax.set_xlim(-2.5, 2.5)
        self.ax.set_ylim(-2.5, 2.5)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_facecolor('black')
        
        # Sliders pour les paramètres
        ax_ecc = plt.axes([0.15, 0.02, 0.25, 0.03])
        self.slider_ecc = Slider(ax_ecc, 'Excentricité', 0.0, 0.99, valinit=0.0167, valstep=0.001)
        
        ax_speed = plt.axes([0.55, 0.02, 0.25, 0.03])
        self.slider_speed = Slider(ax_speed, 'Vitesse (x)', 0.1, 5.0, valinit=1.0, valstep=0.1)
        
        ax_time = plt.axes([0.15, 0.07, 0.25, 0.03])
        self.slider_time = Slider(ax_time, 'Temps (jours)', 0, 365, valinit=0, valstep=1)
        
        # Boutons de contrôle
        ax_play = plt.axes([0.85, 0.02, 0.05, 0.04])
        self.btn_play = Button(ax_play, '▶')
        
        ax_pause = plt.axes([0.91, 0.02, 0.05, 0.04])
        self.btn_pause = Button(ax_pause, '⏸')
        
        ax_reset = plt.axes([0.02, 0.02, 0.06, 0.04])
        self.btn_reset = Button(ax_reset, 'Reset')
        
        ax_export = plt.axes([0.10, 0.02, 0.04, 0.04])
        self.btn_export = Button(ax_export, 'CSV')
        
        # Radio buttons pour sélection du corps central
        ax_radio = plt.axes([0.02, 0.12, 0.1, 0.15])
        self.radio_bodies = RadioButtons(ax_radio, ['Soleil', 'Terre', 'Lune'])
        
        # Connexion des callbacks
        self.slider_ecc.on_changed(self.update_eccentricity)
        self.slider_speed.on_changed(self.update_speed)
        self.slider_time.on_changed(self.update_time)
        self.btn_play.on_clicked(self.play)
        self.btn_pause.on_clicked(self.pause)
        self.btn_reset.on_clicked(self.reset)
        self.btn_export.on_clicked(self.export_data)
        self.radio_bodies.on_clicked(self.change_central_body)
        
    def update_eccentricity(self, val):
        """Mise à jour de l'excentricité de l'orbite"""
        ecc = self.slider_ecc.val
        self.secondary.orbit.eccentricity = ecc
        self.update_simulation()
        
    def update_speed(self, val):
        """Mise à jour de la vitesse de simulation"""
        self.dt = self.config.timestep * self.slider_speed.val
        self.update_simulation()
        
    def update_time(self, val):
        """Saut temporel direct"""
        self.time = self.slider_time.val * 86400  # Conversion jours -> secondes
        self.update_simulation()
        
    def change_central_body(self, label):
        """Changement du corps central de référence"""
        if label == 'Soleil':
            self.primary = self.solar_system.bodies['Sun']
        elif label == 'Terre':
            self.primary = self.solar_system.bodies['Earth']
        elif label == 'Lune':
            self.primary = self.solar_system.bodies['Moon']
        self.update_simulation()
        
    def play(self, event):
        """Démarrage de l'animation"""
        if not self.running:
            self.running = True
            self.ani = FuncAnimation(self.fig, self.animate, interval=50, blit=False, cache_frame_data=False)
            
    def pause(self, event):
        """Pause de l'animation"""
        self.running = False
        if self.ani:
            self.ani.event_source.stop()
            
    def reset(self, event):
        """Remise à zéro de la simulation"""
        self.time = 0.0
        self.slider_time.set_val(0)
        self.running = False
        if self.ani:
            self.ani.event_source.stop()
        self.update_simulation()
        
    def export_data(self, event):
        """Export des données d'orbite en CSV"""
        data = self.generate_orbit_data()
        filename = self.exporter.export(data, prefix='orbit_simulation')
        print(f"Données exportées: {filename}")
        
    def generate_orbit_data(self, steps=1000):
        """Génération des données d'orbite pour export"""
        times = np.linspace(0, self.config.simulation_duration, steps)
        positions = []
        
        for t in times:
            pos = self.orbit_calculator.calculate_position(
                self.secondary.orbit, t
            )
            positions.append({
                'time_days': t / 86400,
                'x_AU': pos[0],
                'y_AU': pos[1],
                'distance_AU': np.linalg.norm(pos),
                'true_anomaly_deg': np.degrees(self.orbit_calculator.true_anomaly)
            })
        return positions
        
    def update_simulation(self):
        """Mise à jour de la simulation avec les nouveaux paramètres"""
        self.visualizer.clear()
        self.visualizer.draw_orbit_system(self.solar_system, self.primary, self.time)
        self.visualizer.draw_trajectories(self.solar_system)
        plt.draw()
        
    def animate(self, frame):
        """Frame d'animation"""
        if self.running:
            self.time += self.dt
            days = self.time / 86400
            self.slider_time.set_val(days)
            
            self.visualizer.clear()
            self.visualizer.draw_orbit_system(self.solar_system, self.primary, self.time)
            self.visualizer.draw_trajectories(self.solar_system)
            
            # Mise à jour du titre avec infos
            period = self.secondary.orbit.period / 86400
            ecc = self.secondary.orbit.eccentricity
            self.fig.suptitle(
                f'Space Orbital Simulator - t={days:.1f}j | P={period:.1f}j | e={ecc:.3f}', 
                fontsize=14
            )
            
        return []
    
    def run(self):
        """Lancement de la simulation"""
        print("🚀 Space Orbital Simulator démarré!")
        print("Utilisez les sliders pour ajuster les paramètres")
        print("▶/⏸ pour play/pause, Reset pour remise à zéro, CSV pour export")
        
        self.update_simulation()
        plt.tight_layout()
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Space Orbital Simulator')
    parser.add_argument('--duration', type=float, default=365.0, help='Durée simulation (jours)')
    parser.add_argument('--timestep', type=float, default=3600.0, help='Pas de temps (secondes)')
    parser.add_argument('--export', action='store_true', help='Export automatique CSV')
    
    args = parser.parse_args()
    
    # Configuration personnalisée
    config = Config(
        simulation_duration=args.duration * 86400,
        timestep=args.timestep
    )
    
    # Lancement de la simulation
    simulator = OrbitalSimulator(config)
    
    if args.export:
        print("Export des données...")
        data = simulator.generate_orbit_data()
        filename = simulator.exporter.export(data)
        print(f"Export terminé: {filename}")
    else:
        simulator.run()

if __name__ == "__main__":
    main()