import unittest
import matplotlib.pyplot as plt
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visualizer import Visualizer, create_animation, plot_orbit_snapshot
from bodies import CelestialBody
from kepler_orbit import KeplerOrbit
from config import CONFIG

class TestVisualizer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sun = CelestialBody(
            name="Sun",
            mass=1.989e30,
            position=np.array([0.0, 0.0]),
            velocity=np.array([0.0, 0.0]),
            radius=6.96e8,
            color='yellow'
        )
        
        self.earth = CelestialBody(
            name="Earth",
            mass=5.972e24,
            position=np.array([1.496e11, 0.0]),
            velocity=np.array([0.0, 29780.0]),
            radius=6.371e6,
            color='blue'
        )
        
        self.moon = CelestialBody(
            name="Moon",
            mass=7.342e22,
            position=np.array([1.496e11 + 3.84e8, 0.0]),
            velocity=np.array([0.0, 29780.0 + 1022.0]),
            radius=1.737e6,
            color='gray'
        )
        
        self.bodies = [self.sun, self.earth, self.moon]
        self.orbit = KeplerOrbit(self.earth, self.sun)
        
    def test_visualizer_initialization(self):
        """Test Visualizer class initialization."""
        viz = Visualizer(self.bodies, self.orbit)
        self.assertEqual(viz.bodies, self.bodies)
        self.assertEqual(viz.orbit, self.orbit)
        self.assertIsInstance(viz.fig, plt.Figure)
        self.assertEqual(len(viz.ax), 1)
        
    @patch('matplotlib.pyplot.show')
    def test_plot_orbit_snapshot(self, mock_show):
        """Test orbit snapshot plotting."""
        positions = {
            'Sun': np.array([[0.0, 0.0]]),
            'Earth': np.array([[1.496e11, 0.0]]),
            'Moon': np.array([[1.496e11 + 3.84e8, 0.0]])
        }
        
        fig, ax = plot_orbit_snapshot(self.bodies, positions, scale=1e9)
        
        self.assertIsInstance(fig, plt.Figure)
        self.assertIsInstance(ax, plt.Axes)
        self.assertTrue(ax.get_xlim()[0] < 0)
        self.assertTrue(ax.get_xlim()[1] > 2)
        self.assertTrue(ax.get_ylim()[0] < 0)
        self.assertTrue(ax.get_ylim()[1] > 0)
        mock_show.assert_called_once()
        
    @patch('matplotlib.pyplot.pause')
    @patch('matplotlib.pyplot.clf')
    def test_create_animation_frame(self, mock_clf, mock_pause):
        """Test single animation frame creation."""
        viz = Visualizer(self.bodies, self.orbit)
        dt = 86400  # 1 day
        
        viz.create_animation_frame(dt)
        
        mock_clf.assert_called_once()
        mock_pause.assert_called_once()
        
    @patch('matplotlib.pyplot.show')
    def test_create_animation(self, mock_show):
        """Test animation creation."""
        viz = Visualizer(self.bodies, self.orbit)
        
        with patch.object(viz, 'create_animation_frame') as mock_frame:
            create_animation(viz, num_frames=5, dt=86400)
            
        self.assertEqual(mock_frame.call_count, 5)
        mock_show.assert_called_once()
        
    def test_visualizer_scale_factor(self):
        """Test dynamic scale factor calculation."""
        viz = Visualizer(self.bodies, self.orbit)
        
        # Test with large distances
        max_dist = 2e11
        scale = viz._calculate_scale(max_dist)
        self.assertAlmostEqual(scale, 1e9, delta=1e8)
        
        # Test with small distances
        max_dist_small = 1e9
        scale_small = viz._calculate_scale(max_dist_small)
        self.assertAlmostEqual(scale_small, 1e7, delta=1e6)
        
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.subplot')
    def test_interactive_controls(self, mock_subplot, mock_figure):
        """Test interactive control initialization."""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_figure.return_value = mock_fig
        mock_subplot.return_value = mock_ax
        
        viz = Visualizer(self.bodies, self.orbit)
        viz.setup_interactive_controls()
        
        mock_fig.canvas.mpl_connect.assert_any_call('button_press_event', ANY)
        mock_fig.canvas.mpl_connect.assert_any_call('key_press_event', ANY)
        
    def test_update_body_positions(self):
        """Test body position updates in visualizer."""
        viz = Visualizer(self.bodies, self.orbit)
        initial_positions = [body.position.copy() for body in self.bodies]
        
        viz.update_body_positions(86400)  # 1 day
        
        # Positions should have changed
        for i, body in enumerate(self.bodies):
            if body.name != "Sun":  # Sun should be stationary
                self.assertFalse(np.array_equal(body.position, initial_positions[i]))
                
    @patch('matplotlib.pyplot.title')
    def test_update_plot_title(self, mock_title):
        """Test dynamic title updates."""
        viz = Visualizer(self.bodies, self.orbit)
        time_step = 86400 * 30  # 30 days
        
        viz.update_plot_title(time_step)
        mock_title.assert_called_once()
        title_call = mock_title.call_args[0][0]
        self.assertIn("t = 30.0 days", str(title_call))
        
    def test_trail_management(self):
        """Test orbital trail length management."""
        viz = Visualizer(self.bodies, self.orbit)
        viz.max_trail_length = 10
        
        # Simulate multiple updates
        for i in range(20):
            viz.update_trails()
            
        for body in self.bodies:
            self.assertLessEqual(len(body.orbit_trail), viz.max_trail_length)

class TestVisualizerEdgeCases(unittest.TestCase):
    
    def test_empty_bodies_list(self):
        """Test visualizer with empty bodies list."""
        with self.assertRaises(ValueError):
            Visualizer([], KeplerOrbit(None, None))
            
    def test_single_body_system(self):
        """Test visualizer with single body."""
        single_body = [self.sun]
        orbit = KeplerOrbit(self.sun, self.sun)  # Self-orbit
        
        viz = Visualizer(single_body, orbit)
        self.assertIsInstance(viz, Visualizer)
        
    def test_extreme_scale(self):
        """Test visualizer with extreme distance scales."""
        extreme_body = CelestialBody(
            name="Extreme",
            mass=1e20,
            position=np.array([1e15, 0.0]),  # Very far
            velocity=np.array([0.0, 1e3]),
            radius=1e6,
            color='red'
        )
        
        bodies = [self.sun, extreme_body]
        viz = Visualizer(bodies, KeplerOrbit(extreme_body, self.sun))
        
        scale = viz._calculate_scale(1e15)
        self.assertAlmostEqual(scale, 1e12, delta=1e11)

if __name__ == '__main__':
    unittest.main(verbosity=2)