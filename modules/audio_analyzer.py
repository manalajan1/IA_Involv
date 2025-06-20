import sounddevice as sd
import numpy as np
import time
from collections import deque
import threading

class AudioAnalyzer:
    def __init__(self, config):
        self.config = config
        self.audio_buffer = deque(maxlen=int(config.SAMPLE_RATE * config.BUFFER_SECONDS))
        self.volume_history = deque(maxlen=100)
        self.talking = False
        self.talk_start_time = 0
        self.total_talk_time = 0
        self.stream = None
        self.running = False
        
    def audio_callback(self, indata, frames, time_info, status):  # <-- nom corrigé ici
        volume = np.linalg.norm(indata) * 10
        self.volume_history.append(volume)
        
        if volume > self.config.AUDIO_THRESHOLD:
            if not self.talking:
                self.talking = True
                self.talk_start_time = time.time()
        else:
            if self.talking:
                self.talking = False
                self.total_talk_time += time.time() - self.talk_start_time
        
        self.audio_buffer.extend(indata[:, 0])
    
    def analyze_audio(self):
        while self.running:
            avg_volume = np.mean(self.volume_history) if self.volume_history else 0
            talk_percent = (self.total_talk_time / self.config.UI_UPDATE_INTERVAL) * 100
            self.total_talk_time = 0
            
            with open(self.config.AUDIO_DATA_FILE, "w") as f:
                f.write(f"volume:{avg_volume:.2f}\n")
                f.write(f"talking:{talk_percent:.1f}\n")
                f.write(f"noise:{avg_volume * 0.3:.2f}\n")
            
            time.sleep(self.config.UI_UPDATE_INTERVAL)
    
    def start(self):
        self.running = True
        self.stream = sd.InputStream(
            callback=self.audio_callback,
            channels=self.config.CHANNELS,
            samplerate=self.config.SAMPLE_RATE,
            blocksize=int(self.config.SAMPLE_RATE * 0.1)
        )
        self.stream.start()
        self.analysis_thread = threading.Thread(target=self.analyze_audio, daemon=True)
        self.analysis_thread.start()
    
    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        if hasattr(self, 'analysis_thread'):
            self.analysis_thread.join()
