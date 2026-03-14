import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Ellipse
import tkinter as tk
from tkinter import messagebox
from config import Config
from kepler_orbit import KeplerOrbit
from bodies import CelestialBody
import threading
import time

class InteractiveVisualizer:
    def __init__(self):
        self.config = Config()
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_facecolor('black')
        self.ax.set_title('Space Orbital Simulator - Interactive Kepler Orbits', color='white', fontsize=14)
        
        # Celestial bodies
        self.sun = CelestialBody('Sun', 0, 0, 1.0, 'yellow', 20)
        self.earth = CelestialBody('Earth', 1.0, 0, 0.01, 'blue', 8)
        self.moon = CelestialBody('Moon', 1.02, 0, 0.001, 'gray', 4)
        
        # Orbit objects
        self.earth_orbit = KeplerOrbit(self.sun.mass, 1.0, 0.0167, 0)
        self.moon_orbit = KeplerOrbit(self.earth.mass, 0.384e6 / 1.496e11, 0.0549, 0)
        
        # Animation and simulation state
        self.time = 0
        self.dt = 0.01
        self.is_animating = False
        self.animation = None
        
        # UI elements
        self._init_sliders()
        self._init_buttons()
        self._init_radio_buttons()
        
        # Trails
        self.earth_trail, = self.ax.plot([], [], 'b-', alpha=0.5, linewidth=1, label='Earth Trail')
        self.moon_trail, = self.ax.plot([], [], 'gray', alpha=0.5, linewidth=1, label='Moon Trail')
        
        # Labels
        self.body_labels = {}
        
        self.update_plot()
        plt.tight_layout()
        
    def _init_sliders(self):
        """Initialize slider controls"""
        plt.subplots_adjust(bottom=0.25)
        
        # Time step slider
        self.dt_slider = Slider(
            plt.axes([0.15, 0.15, 0.25, 0.03]),
            'Time Step',
            0.001, 0.1, valinit=self.dt, valfmt='%.3f'
        )
        self.dt_slider.on_changed(self._update_dt)
        
        # Earth eccentricity slider
        self.ecc_slider = Slider(
            plt.axes([0.15, 0.10, 0.25, 0.03]),
            'Earth Ecc.',
            0.0, 0.5, valinit=self.earth_orbit.eccentricity, valfmt='%.3f'
        )
        self.ecc_slider.on_changed(self._update_eccentricity)
        
        # Moon eccentricity slider
        self.moon_ecc_slider = Slider(
            plt.axes([0.55, 0.10, 0.25, 0.03]),
            'Moon Ecc.',
            0.0, 0.2, valinit=self.moon_orbit.eccentricity, valfmt='%.3f'
        )
        self.moon_ecc_slider.on_changed(self._update_moon_eccentricity)
        
        # Simulation speed slider
        self.speed_slider = Slider(
            plt.axes([0.55, 0.15, 0.25, 0.03]),
            'Speed',
            0.1, 10.0, valinit=1.0, valfmt='%.1f'
        )
        self.speed_slider.on_changed(self._update_speed)
    
    def _init_buttons(self):
        """Initialize control buttons"""
        ax_play = plt.axes([0.15, 0.05, 0.08, 0.04])
        self.play_button = Button(ax_play, 'Play')
        self.play_button.on_clicked(self._toggle_play)
        
        ax_pause = plt.axes([0.25, 0.05, 0.08, 0.04])
        self.pause_button = Button(ax_pause, 'Pause')
        self.pause_button.on_clicked(self._pause)
        
        ax_reset = plt.axes([0.35, 0.05, 0.08, 0.04])
        self.reset_button = Button(ax_reset, 'Reset')
        self.reset_button.on_clicked(self._reset)
        
        ax_trails = plt.axes([0.55, 0.05, 0.08, 0.04])
        self.trails_button = Button(ax_trails, 'Trails')
        self.trails_button.on_clicked(self._toggle_trails)
        
        self.show_trails = True
    
    def _init_radio_buttons(self):
        """Initialize radio button controls"""
        ax_radio = plt.axes([0.75, 0.05, 0.15, 0.12])
        self.view_mode = RadioButtons(ax_radio, ['Heliocentric', 'Geocentric', '3-Body'], active=0)
        self.view_mode.on_clicked(self._change_view)
    
    def _update_dt(self, val):
        self.dt = val
    
    def _update_eccentricity(self, val):
        self.earth_orbit.eccentricity = val
        self.update_plot()
    
    def _update_moon_eccentricity(self, val):
        self.moon_orbit.eccentricity = val
        self.update_plot()
    
    def _update_speed(self, val):
        self.speed_factor = val
    
    def _toggle_play(self, event):
        if not self.is_animating:
            self.is_animating = True
            self.animation = animation.FuncAnimation(
                self.fig, self._animate, interval=50, blit=False, repeat=True
            )
        else:
            self._pause(event)
    
    def _pause(self, event):
        self.is_animating = False
        if self.animation:
            self.animation.event_source.stop()
    
    def _reset(self, event):
        self.time = 0
        self.earth_trail.set_data([], [])
        self.moon_trail.set_data([], [])
        self.update_plot()
    
    def _toggle_trails(self, event):
        self.show_trails = not self.show_trails
        self.earth_trail.set_visible(self.show_trails)
        self.moon_trail.set_visible(self.show_trails)
        self.fig.canvas.draw()
    
    def _change_view(self, label):
        if label == 'Heliocentric':
            self.view_mode_index = 0
        elif label == 'Geocentric':
            self.view_mode_index = 1
        else:
            self.view_mode_index = 2
        self.update_plot()
    
    def update_plot(self):
        """Update static plot elements"""
        self.ax.clear()
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_facecolor('black')
        self.ax.set_title('Space Orbital Simulator - Interactive Kepler Orbits', color='white', fontsize=14)
        
        # Draw Sun
        self.ax.add_patch(plt.Circle((0, 0), self.sun.radius/20, color=self.sun.color))
        
        # Draw Earth orbit
        theta = np.linspace(0, 2*np.pi, 1000)
        r_earth = self.earth_orbit.get_radius(theta)
        x_earth = r_earth * np.cos(theta)
        y_earth = r_earth * np.sin(theta)
        self.ax.plot(x_earth, y_earth, 'b--', alpha=0.7, linewidth=1)
        
        # Draw Moon orbit (scaled)
        if self.view_mode_index != 1:
            r_moon = self.moon_orbit.get_radius(theta) * 100  # Scale for visibility
            x_moon = (r_moon * np.cos(theta)) + 1.0
            y_moon = r_moon * np.sin(theta)
            self.ax.plot(x_moon/100, y_moon/100, 'gray', alpha=0.5, linewidth=0.8)
        
        # Update body positions
        self._update_body_positions()
        
        # Update trails
        self._update_trails()
        
        # Update labels
        self._update_labels()
        
        self.fig.canvas.draw()
    
    def _update_body_positions(self):
        """Update positions of celestial bodies"""
        # Earth position
        earth_pos = self.earth_orbit.get_position(self.time)
        self.earth.x, self.earth.y = earth_pos
        
        # Moon position relative to Earth
        moon_pos = self.moon_orbit.get_position(self.time * 27.3)  # Lunar month scaling
        self.moon.x = self.earth.x + moon_pos[0] * 0.00257  # Scale to AU
        self.moon.y = self.earth.y + moon_pos[1] * 0.00257
        
        # Draw bodies
        self.ax.add_patch(plt.Circle((self.earth.x, self.earth.y), self.earth.radius/20, 
                                   color=self.earth.color))
        self.ax.add_patch(plt.Circle((self.moon.x, self.moon.y), self.moon.radius/20, 
                                   color=self.moon.color))
    
    def _update_trails(self):
        """Update orbit trails"""
        if self.show_trails:
            t_trail = np.linspace(max(0, self.time-2), self.time, 100)
            earth_trail_x, earth_trail_y = [], []
            moon_trail_x, moon_trail_y = [], []
            
            for t in t_trail:
                pos_e = self.earth_orbit.get_position(t)
                earth_trail_x.append(pos_e[0])
                earth_trail_y.append(pos_e[1])
                
                pos_m = self.moon_orbit.get_position(t * 27.3)
                moon_trail_x.append(self.earth_orbit.get_position(t)[0] + pos_m[0] * 0.00257)
                moon_trail_y.append(self.earth_orbit.get_position(t)[1] + pos_m[1] * 0.00257)
            
            self.earth_trail.set_data(earth_trail_x, earth_trail_y)
            self.moon_trail.set_data(moon_trail_x, moon_trail_y)
    
    def _update_labels(self):
        """Update position labels"""
        self.ax.text(0.02, 0.98, f'Time: {self.time:.2f} years', 
                    transform=self.ax.transAxes, color='white', 
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        self.ax.text(0.02, 0.92, f'Earth: ({self.earth.x:.3f}, {self.earth.y:.3f}) AU', 
                    transform=self.ax.transAxes, color='blue', 
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        self.ax.text(0.02, 0.86, f'Moon: ({self.moon.x:.3f}, {self.moon.y:.3f}) AU', 
                    transform=self.ax.transAxes, color='gray', 
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
    
    def _animate(self, frame):
        """Animation update function"""
        if self.is_animating:
            self.time += self.dt * getattr(self, 'speed_factor', 1.0)
            self.update_plot()
        return []
    
    def run(self):
        """Start the interactive visualizer"""
        plt.show()

def main():
    """Main function to run the visualizer"""
    try:
        viz = InteractiveVisualizer()
        viz.run()
    except Exception as e:
        print(f"Error running visualizer: {e}")
        tk.Tk().wm_withdraw()
        messagebox.showerror("Visualizer Error", f"Failed to start visualizer:\n{str(e)}")

if __name__ == "__main__":
    main()