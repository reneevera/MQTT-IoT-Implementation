import tkinter as tk
from tkinter import scrolledtext
import paho.mqtt.client as mqtt
import json

# MQTT settingscls
broker = "localhost"
port = 1883
topic = "phLevel"
client = mqtt.Client()

class SubscriberApp:
    def __init__(self, master):
        self.master = master
        master.title("Subscriber_")

        self.log = scrolledtext.ScrolledText(master, state='disabled', height=10)
        self.log.pack()

        self.close_button = tk.Button(master, text="Close", command=master.destroy)
        self.close_button.pack()

        # Setting up the MQTT client
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(broker, port)
        client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        self.update_log(f"Received: {payload}")

    def update_log(self, message):
        self.log['state'] = 'normal'
        if self.log.index('end-1c').split('.')[0] == '11.0':  # If there are 10 entries, delete the first
            self.log.delete('1.0', '2.0')
        self.log.insert(tk.END, message + '\n')
        self.log['state'] = 'disabled'

root = tk.Tk()
app = SubscriberApp(root)
root.mainloop()
