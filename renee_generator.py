import time
import random
from datetime import datetime

class DataGenerator:
    # Removed the interval attribute since it's not used in the updated publisher

    @staticmethod
    def generate_data():
        # Generate data with a pattern and random elements
        # Simulate "wild data" with some probability
        ph_value = random.uniform(6.5, 8.5)  # Example pH range
        wild_data_chance = random.randint(0, 1000)
        if wild_data_chance == 0:  # Simulate wild data
            ph_value = random.uniform(0, 14)  # Completely off the charts

        # Using consistent timestamp format (ISO 8601)
        timestamp = datetime.now().isoformat()

        # Add a timestamp and packet ID
        data = {
            'timestamp': timestamp,
            'packet_id': random.randint(1000, 9999),
            'ph_value': ph_value
        }
        return data
