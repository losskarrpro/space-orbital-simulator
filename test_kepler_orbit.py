import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import kepler_orbit

class TestKeplerOrbit(unittest.TestCase):
    
    def setUp(self):
        self.a = 1.0  # demi-grand axe (UA)
        self.e = 0.0167  # excentricité Terre
        self.mu = 1.327e20  # paramètre gravitationnel Soleil (m³/s²)
        
    def test_perihelion_distance(self):
        """Test calcul distance périhélie"""
        expected = self.a * (1 - self.e)
        result = kepler_orbit.perihelion_distance(self.a, self.e)
        self.assertAlmostEqual(result, expected, places=10)
        self.assertGreater(result, 0)
    
    def test_aphelion_distance(self):
        """Test calcul distance aphélie"""
        expected = self.a * (1 + self.e)
        result = kepler_orbit.aphelion_distance(self.a, self.e)
        self.assertAlmostEqual(result, expected, places=10)
        self.assertGreater(result, 0)
    
    def test_orbital_period_kepler3(self):
        """Test 3ème loi de Kepler"""
        expected = 2 * np.pi * np.sqrt(self.a**3)
        result = kepler_orbit.orbital_period_kepler3(self.a)
        self.assertAlmostEqual(result, expected, places=10)
    
    def test_orbital_period_gravitational(self):
        """Test période orbitale avec paramètre gravitationnel"""
        expected = 2 * np.pi * np.sqrt(self.a**3 * 1.496e11**3 / self.mu)
        result = kepler_orbit.orbital_period_gravitational(self.a, self.mu)
        self.assertAlmostEqual(result / (365.25*24*3600), expected / (365.25*24*3600), places=6)
    
    def test_eccentricity_bounds(self):
        """Test contraintes excentricité [0,1)"""
        with self.assertRaises(ValueError):
            kepler_orbit.perihelion_distance(self.a, -0.1)
        with self.assertRaises(ValueError):
            kepler_orbit.perihelion_distance(self.a, 1.1)
        with self.assertRaises(ValueError):
            kepler_orbit.aphelion_distance(self.a, -0.1)
        with self.assertRaises(ValueError):
            kepler_orbit.aphelion_distance(self.a, 1.1)
    
    def test_zero_eccentricity_circle(self):
        """Test orbite circulaire (e=0)"""
        peri = kepler_orbit.perihelion_distance(self.a, 0.0)
        aphe = kepler_orbit.aphelion_distance(self.a, 0.0)
        self.assertAlmostEqual(peri, self.a)
        self.assertAlmostEqual(aphe, self.a)
    
    def test_extreme_eccentricity(self):
        """Test orbite très elliptique (e→1)"""
        e = 0.999
        peri = kepler_orbit.perihelion_distance(self.a, e)
        aphe = kepler_orbit.aphelion_distance(self.a, e)
        self.assertAlmostEqual(peri + aphe, 2 * self.a, places=10)
        self.assertLess(peri, 0.01 * self.a)
    
    def test_mean_motion(self):
        """Test vitesse angulaire moyenne"""
        period = kepler_orbit.orbital_period_kepler3(self.a)
        expected = 2 * np.pi / period
        result = kepler_orbit.mean_motion(self.a)
        self.assertAlmostEqual(result, expected, places=10)
    
    def test_vis_viva_equation(self):
        """Test équation vis-viva"""
        r_peri = kepler_orbit.perihelion_distance(self.a, self.e)
        r_aphe = kepler_orbit.aphelion_distance(self.a, self.e)
        
        v_peri = kepler_orbit.vis_viva(self.a, self.e, r_peri)
        v_aphe = kepler_orbit.vis_viva(self.a, self.e, r_aphe)
        
        self.assertGreater(v_peri, v_aphe)
        self.assertGreater(v_peri, 0)
        self.assertGreater(v_aphe, 0)

class TestKeplerOrbitEdgeCases(unittest.TestCase):
    
    def test_small_semi_major_axis(self):
        """Test avec très petit demi-grand axe"""
        a_small = 1e-6
        peri = kepler_orbit.perihelion_distance(a_small, 0.5)
        self.assertGreater(peri, 0)
    
    def test_large_semi_major_axis(self):
        """Test avec très grand demi-grand axe"""
        a_large = 1e6
        period = kepler_orbit.orbital_period_kepler3(a_large)
        self.assertGreater(period, 1e10)  # très longue période

if __name__ == '__main__':
    unittest.main(verbosity=2)