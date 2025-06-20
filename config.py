class Config:
    def __init__(self):
        # Audio
        self.SAMPLE_RATE = 44100
        self.CHANNELS = 1
        self.AUDIO_THRESHOLD = 5.0
        self.BUFFER_SECONDS = 5
        
        # Vidéo
        self.ATTENTION_HISTORY_SIZE = 50
        self.EYE_CLOSED_THRESHOLD = 5
        self.ALERT_DURATION = 7  # secondes
        
        # Environnement
        self.ENV_UPDATE_INTERVAL = 5  # secondes
        
        # Interface
        self.UI_UPDATE_INTERVAL = 2  # secondes
        self.ALERT_THRESHOLD = 40  # %
        
        # Chemins des fichiers
        self.AUDIO_DATA_FILE = "data/audio_level.txt"
        self.ATTENTION_DATA_FILE = "data/score.txt"
        self.HISTORY_DATA_FILE = "data/attention_history.txt"
        self.ENV_DATA_FILE = "data/environment.txt"