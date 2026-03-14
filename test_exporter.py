import unittest
import os
import csv
import tempfile
from unittest.mock import patch, mock_open
from io import StringIO
import pandas as pd

from exporter import export_orbits_to_csv, export_body_data_to_csv
from bodies import CelestialBody
from config import ORBIT_CONFIG


class TestExporter(unittest.TestCase):
    
    def setUp(self):
        self.test_bodies = [
            CelestialBody(name="Sun", mass=1.989e30, radius=696340000, color="yellow"),
            CelestialBody(name="Earth", mass=5.972e24, radius=6371000000, color="blue"),
            CelestialBody(name="Moon", mass=7.342e22, radius=1737400000, color="gray")
        ]
        
        self.test_orbit_data = [
            {"time": 0.0, "body": "Earth", "x": 1.496e11, "y": 0.0, "vx": 0.0, "vy": 29780.0, "distance": 1.496e11},
            {"time": 86400.0, "body": "Earth", "x": 1.495e11, "y": 2.59e9, "vx": -179.0, "vy": 29780.0, "distance": 1.496e11},
            {"time": 172800.0, "body": "Moon", "x": 1.496e11 + 3.84e8, "y": 0.0, "vx": 0.0, "vy": 1022.0, "distance": 3.84e8}
        ]
    
    def test_export_orbits_to_csv_valid_data(self):
        """Test export avec données d'orbite valides"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            filename = tmp_file.name
            
            export_orbits_to_csv(self.test_orbit_data, filename)
            
            # Vérifier que le fichier existe et n'est pas vide
            self.assertTrue(os.path.exists(filename))
            self.assertGreater(os.path.getsize(filename), 0)
            
            # Vérifier le contenu CSV
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                self.assertEqual(len(rows), 3)
                self.assertEqual(rows[0]['time'], '0.0')
                self.assertEqual(rows[0]['body'], 'Earth')
                self.assertEqual(rows[0]['x'], '149600000000.0')
                self.assertEqual(rows[1]['body'], 'Earth')
                self.assertEqual(rows[2]['body'], 'Moon')
            
            os.unlink(filename)
    
    def test_export_orbits_to_csv_empty_data(self):
        """Test export avec liste vide"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            filename = tmp_file.name
            
            export_orbits_to_csv([], filename)
            
            with open(filename, 'r') as f:
                content = f.read()
                self.assertIn('time,body,x,y,vx,vy,distance', content)
                self.assertEqual(len(content.splitlines()), 1)  # Seulement l'en-tête
            
            os.unlink(filename)
    
    def test_export_body_data_to_csv(self):
        """Test export des données des corps célestes"""
        expected_csv = """name,mass,radius,color
Sun,1.989e+30,696340000,yellow
Earth,5.972e+24,6371000000,blue
Moon,7.342e+22,1737400000,gray
"""
        
        with patch('builtins.open', mock_open(read_data='')) as mocked_file:
            export_body_data_to_csv(self.test_bodies, 'test_bodies.csv')
            
            handle = mocked_file()
            handle.write.assert_called_once_with(expected_csv)
    
    def test_export_body_data_to_csv_empty_list(self):
        """Test export avec liste de corps vide"""
        with patch('builtins.open', mock_open(read_data='')) as mocked_file:
            export_body_data_to_csv([], 'test_empty.csv')
            
            handle = mocked_file()
            handle.write.assert_called_once()
            written_content = handle.write.call_args[0][0]
            self.assertIn('name,mass,radius,color', written_content)
            self.assertEqual(written_content.count('\n'), 1)  # Seulement l'en-tête
    
    def test_csv_format_validation_with_pandas(self):
        """Test validation du format CSV avec pandas"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            filename = tmp_file.name
            
            export_orbits_to_csv(self.test_orbit_data, filename)
            
            # Charger avec pandas pour valider le format
            df = pd.read_csv(filename)
            
            expected_columns = ['time', 'body', 'x', 'y', 'vx', 'vy', 'distance']
            self.assertListEqual(list(df.columns), expected_columns)
            self.assertEqual(len(df), 3)
            self.assertFalse(df.isnull().values.any())
            
            os.unlink(filename)
    
    def test_invalid_filename_handling(self):
        """Test gestion des noms de fichiers invalides"""
        with self.assertRaises(ValueError):
            export_orbits_to_csv(self.test_orbit_data, '')
        
        with self.assertRaises(ValueError):
            export_orbits_to_csv(self.test_orbit_data, None)
    
    def test_data_types_preservation(self):
        """Test préservation des types de données numériques"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            filename = tmp_file.name
            
            export_orbits_to_csv(self.test_orbit_data, filename)
            
            df = pd.read_csv(filename)
            self.assertTrue(pd.api.types.is_numeric_dtype(df['time']))
            self.assertTrue(pd.api.types.is_numeric_dtype(df['x']))
            self.assertTrue(pd.api.types.is_numeric_dtype(df['distance']))
            
            os.unlink(filename)


if __name__ == '__main__':
    unittest.main(verbosity=2)