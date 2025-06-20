import threading
import time
from integrated_system import IntegratedSystem
from config import Config

def main():
    config = Config()
    system = IntegratedSystem(config)
    
    try:
        system.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nArrêt du système...")
        system.stop()

if __name__ == "__main__":
    main()