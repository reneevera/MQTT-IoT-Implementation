import tkinter as tk
from tkinter import scrolledtext
import threading
import paho.mqtt.client as mqtt
import json
from datetime import datetime
from renee_generator import DataGenerator
import time
import random

# MQTT settings
broker = "localhost"
port = 1883
topic = "phLevel"
client = mqtt.Client()

class PublisherApp:
    def __init__(self, master):
        self.master = master
        master.title("Publisher_")

        # Adding GUI elements
        self.start_button = tk.Button(master, text="Start Publishing", command=self.start_publishing)
        self.start_button.pack()

        self.log = scrolledtext.ScrolledText(master, state='disabled', height=10)
        self.log.pack()
        
        # Connecting to the broker
        client.connect(broker, port)

    def publish_sensor_data(self):
        packet_id = 0
        while True:
            packet_id += 1
            ph_value = DataGenerator.generate_data()
            timestamp = datetime.now().isoformat()
            payload = {
                "timestamp": timestamp,
                "packet_id": packet_id,
                "ph_value": ph_value
            }
            client.publish(topic, json.dumps(payload))
            self.update_log(f"Published: {payload}")
            time.sleep(random.uniform(1, 5))  # Random sleep time to simulate irregular data generation.

    def start_publishing(self):
        # Start a new thread to run the publishing loop
        self.publishing_thread = threading.Thread(target=self.publish_sensor_data)
        self.publishing_thread.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
        self.publishing_thread.start()
        self.start_button['state'] = 'disabled'

    def update_log(self, message):
        self.log['state'] = 'normal'
        if self.log.index('end-1c').split('.')[0] == '11.0':  # If there are 10 entries, delete the first
            self.log.delete('1.0', '2.0')
        self.log.insert(tk.END, message + '\n')
        self.log['state'] = 'disabled'

root = tk.Tk()
app = PublisherApp(root)
root.mainloop()
