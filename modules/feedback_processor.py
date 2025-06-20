import os

class FeedbackProcessor:
    def __init__(self, feedback_file):
        self.feedback_file = feedback_file

    def get_latest_feedback(self):
        if not os.path.exists(self.feedback_file):
            return None

        with open(self.feedback_file, 'r') as f:
            lines = f.readlines()
            if not lines:
                return None
            last = lines[-1].strip()

        # Ex: 2025-06-19 21:00 | Son: Bonne, Confort: Acceptable, Attention: 7, Commentaire: ...
        try:
            parts = last.split('|')
            sound_quality = parts[1].split(':')[1].strip()
            comfort = parts[2].split(':')[1].strip()
            attention = int(parts[3].split(':')[1].strip())
            return {
                "sound_quality": sound_quality,
                "comfort": comfort,
                "attention_level": attention
            }
        except:
            return None

    def compute_environment_adjustment(self):
        feedback = self.get_latest_feedback()
        if not feedback:
            return 0

        comfort = feedback["comfort"]

        # Ajustement selon le confort
        if comfort == "Confortable":
            return 0
        elif comfort == "Acceptable":
            return -5
        elif comfort == "Inconfortable":
            return -10
        return 0
