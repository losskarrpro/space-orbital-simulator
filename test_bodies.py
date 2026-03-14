import unittest
import numpy as np
from bodies import CelestialBody, SolarSystem

class TestCelestialBody(unittest.TestCase):
    
    def setUp(self):
        self.earth = CelestialBody(
            name="Earth",
            mass=5.972e24,
            radius=6371e3,
            position=np.array([1.496e11, 0, 0]),
            velocity=np.array([0, 29780, 0]),
            color=(0, 0.5, 1)
        )
        
        self.moon = CelestialBody(
            name="Moon",
            mass=7.342e22,
            radius=1737e3,
            position=np.array([1.496e11 + 384400e3, 0, 0]),
            velocity=np.array([0, 29780 - 1022, 0]),
            color=(0.8, 0.8, 0.8)
        )
    
    def test_initialization(self):
        """Test l'initialisation d'un corps céleste"""
        self.assertEqual(self.earth.name, "Earth")
        self.assertEqual(self.earth.mass, 5.972e24)
        self.assertEqual(self.earth.radius, 6371e3)
        self.assertTrue(np.allclose(self.earth.position, [1.496e11, 0, 0]))
        self.assertTrue(np.allclose(self.earth.velocity, [0, 29780, 0]))
        self.assertEqual(self.earth.color, (0, 0.5, 1))
    
    def test_position_getter_setter(self):
        """Test les getters/setters de position"""
        new_pos = np.array([1.5e11, 1e9, 0])
        self.earth.position = new_pos
        self.assertTrue(np.allclose(self.earth.position, new_pos))
    
    def test_velocity_getter_setter(self):
        """Test les getters/setters de vitesse"""
        new_vel = np.array([100, 29700, 50])
        self.earth.velocity = new_vel
        self.assertTrue(np.allclose(self.earth.velocity, new_vel))
    
    def test_distance_to(self):
        """Test le calcul de distance entre deux corps"""
        distance = self.earth.distance_to(self.moon)
        expected_distance = 384400e3  # distance Terre-Lune moyenne
        self.assertAlmostEqual(distance, expected_distance, delta=1e3)
    
    def test_gravitational_parameter(self):
        """Test le calcul du paramètre gravitationnel μ = GM"""
        G = 6.67430e-11
        mu_earth = self.earth.mass * G
        self.assertAlmostEqual(self.earth.mu, mu_earth, places=5)
    
    def test_invalid_mass(self):
        """Test l'erreur pour masse négative"""
        with self.assertRaises(ValueError):
            CelestialBody("Invalid", mass=-1, radius=1e6, 
                         position=np.zeros(3), velocity=np.zeros(3))
    
    def test_invalid_radius(self):
        """Test l'erreur pour rayon négatif"""
        with self.assertRaises(ValueError):
            CelestialBody("Invalid", mass=1e24, radius=-1e6, 
                         position=np.zeros(3), velocity=np.zeros(3))

class TestSolarSystem(unittest.TestCase):
    
    def setUp(self):
        self.system = SolarSystem()
    
    def test_initialization(self):
        """Test l'initialisation du système solaire avec corps par défaut"""
        self.assertGreater(len(self.system.bodies), 0)
        self.assertIn("Sun", [body.name for body in self.system.bodies])
        self.assertIn("Earth", [body.name for body in self.system.bodies])
    
    def test_add_body(self):
        """Test l'ajout d'un nouveau corps"""
        test_body = CelestialBody("Test", 1e24, 1e7, np.zeros(3), np.zeros(3))
        self.system.add_body(test_body)
        self.assertIn(test_body, self.system.bodies)
        self.assertEqual(len(self.system.bodies), 4)  # 3 défaut + 1 test
    
    def test_get_body_by_name(self):
        """Test la récupération d'un corps par son nom"""
        sun = self.system.get_body("Sun")
        self.assertIsNotNone(sun)
        self.assertEqual(sun.name, "Sun")
        self.assertEqual(sun.mass, 1.989e30)
    
    def test_get_body_not_found(self):
        """Test la gestion d'un corps inexistant"""
        with self.assertRaises(ValueError):
            self.system.get_body("Mars")  # Pas dans le système de base
    
    def test_total_mass(self):
        """Test le calcul de la masse totale"""
        total_mass = sum(body.mass for body in self.system.bodies)
        self.assertAlmostEqual(self.system.total_mass, total_mass)

if __name__ == '__main__':
    unittest.main()