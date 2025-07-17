import time
import threading
import json
import csv
from datetime import datetime
import os
from modules.feedback_processor import FeedbackProcessor

class DataIntegrator:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.feedback_processor = FeedbackProcessor("data/student_feedback.txt")
        self.last_integrated_data = None  # Pour accès rapide au dernier état

    def integrate_data(self):
        while self.running:
            try:
                attention_data = self.read_attention_data()
                audio_data = self.read_audio_data()
                env_data = self.read_environment_data()

                # ➕ Ajustement de l'environnement via feedback étudiant
                adjustment = self.feedback_processor.compute_environment_adjustment()
                env_data["adjustment"] = adjustment  # pour traçabilité

                overall_score = self.calculate_overall_score(attention_data, audio_data, env_data)
                integrated_data = {
                    "timestamp": datetime.now().isoformat(),
                    "attention": attention_data,
                    "audio": audio_data,
                    "environment": env_data,
                    "overall_score": overall_score
                }
                self.last_integrated_data = integrated_data

                self.update_history(integrated_data)

            except Exception as e:
                print(f"Erreur d'intégration des données: {str(e)}")

            time.sleep(self.config.UI_UPDATE_INTERVAL)

    def read_attention_data(self):
        try:
            with open(self.config.ATTENTION_DATA_FILE, "r") as f:
                content = f.read().strip().split('\n')
                avg_score = float(content[0])
                individual_scores = {}
                for line in content[1:]:
                    face_id, score = line.split(':')
                    individual_scores[face_id] = float(score)
                return {"average": avg_score, "individual": individual_scores}
        except:
            return {"average": 0, "individual": {}}

    def read_audio_data(self):
        try:
            with open(self.config.AUDIO_DATA_FILE, "r") as f:
                data = {}
                for line in f.readlines():
                    key, val = line.strip().split(':')
                    data[key] = float(val)
                return data
        except:
            return {"volume": 0, "talking": 0, "noise": 0}

    def read_environment_data(self):
        try:
            with open(self.config.ENV_DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {"co2": 0, "temperature": 0, "humidity": 0, "noise": 0}

    @staticmethod
    def calculate_overall_score(attention, audio, env):
        attention_weight = 0.6
        audio_weight = 0.2
        env_weight = 0.2

        env_factor = 1 - min(1, (env['co2'] - 400) / 1600)
        env_factor *= (30 - env['temperature']) / 12 if env['temperature'] > 24 else 1

        score = (attention['average'] * attention_weight +
                 audio['talking'] * audio_weight +
                 env_factor * 100 * env_weight)

        # ➕ Appliquer ajustement du feedback étudiant
        score += env.get("adjustment", 0)

        return max(0, min(100, score))

    def update_history(self, data):
        try:
            with open(self.config.HISTORY_DATA_FILE, "a") as f:
                f.write(f"{data['overall_score']}\n")

            with open(self.config.HISTORY_DATA_FILE, "r") as f:
                lines = f.readlines()
            if len(lines) > 100:
                with open(self.config.HISTORY_DATA_FILE, "w") as f:
                    f.writelines(lines[-100:])
        except Exception as e:
            print(f"Erreur de mise à jour de l'historique: {str(e)}")

    def export_attention_csv(self, csv_path="data/attention_scores.csv"):
        """ Exporte les scores d'attention individuels en CSV """
        attention_data = self.read_attention_data()
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["etudiant", "score"])
            for etudiant, score in attention_data["individual"].items():
                writer.writerow([etudiant, score])
        return csv_path

    def get_last_report(self):
        """ Retourne un rapport détaillé du dernier état intégré """
        return self.last_integrated_data

    def start(self):
        self.running = True
        self.integrator_thread = threading.Thread(target=self.integrate_data, daemon=True)
        self.integrator_thread.start()

    def stop(self):
        self.running = False
        if hasattr(self, 'integrator_thread'):
            self.integrator_thread.join()