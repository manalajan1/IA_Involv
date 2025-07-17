import threading
from modules.audio_analyzer import AudioAnalyzer
from modules.face_analyzer import FaceAnalyzer
from modules.environment_sensor import EnvironmentSensor
from modules.data_integrator import DataIntegrator
from modules.teacher_interface import TeacherInterface

class IntegratedSystem:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.audio_analyzer = AudioAnalyzer(config)
        self.face_analyzer = FaceAnalyzer(config)
        self.env_sensor = EnvironmentSensor(config)
        self.data_integrator = DataIntegrator(config)
        self.teacher_interface = TeacherInterface(config)
        
    def start(self):
        self.running = True
        self.audio_analyzer.start()
        self.face_analyzer.start()
        self.env_sensor.start()
        self.data_integrator.start()
        self.teacher_interface.start()
        print("Système AI Involvment démarré avec succès")
        
    def stop(self):
        self.running = False
        self.audio_analyzer.stop()
        self.face_analyzer.stop()
        self.env_sensor.stop()
        self.data_integrator.stop()
        self.teacher_interface.stop()