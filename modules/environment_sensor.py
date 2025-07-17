import random
import time
import threading
import json

class EnvironmentSensor:
    def __init__(self, config):
        self.config = config
        self.running = False
        
    def read_sensors(self):
        return {
            "co2": random.randint(400, 2000),
            "temperature": round(random.uniform(18.0, 30.0), 1),
            "humidity": random.randint(30, 80),
            "noise": random.randint(30, 80)
        }
    
    def monitor_environment(self):
        while self.running:
            env_data = self.read_sensors()
            with open(self.config.ENV_DATA_FILE, "w") as f:
                json.dump(env_data, f)
            time.sleep(self.config.ENV_UPDATE_INTERVAL)
    
    def start(self):
        self.running = True
        self.sensor_thread = threading.Thread(target=self.monitor_environment, daemon=True)
        self.sensor_thread.start()
    
    def stop(self):
        self.running = False
        if hasattr(self, 'sensor_thread'):
            self.sensor_thread.join()