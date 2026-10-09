"""
Path configuration helper for dataset and assets.
Ensures data files are correctly located regardless of execution working directory.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DESTINATIONS_CSV = os.path.join(DATA_DIR, "destinations.csv")
RATINGS_CSV = os.path.join(DATA_DIR, "user_ratings.csv")
