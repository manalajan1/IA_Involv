from flask import Flask, render_template, jsonify, request
import threading
import time
import json
import os
from datetime import datetime
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

class TeacherInterface:
    def __init__(self, config):
        self.config = config
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
        self.app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def dashboard():
            return render_template('dashboard.html')

        @self.app.route('/data')
        def get_data():
            data = self.get_current_data()
            data['attention_chart'] = self.generate_attention_chart(data['history'])
            data['environment_chart'] = self.generate_environment_chart(data['environment'])
            return jsonify(data)

        @self.app.route('/export', methods=['POST'])
        def export_data():
            try:
                data = self.get_current_data()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_attention_{timestamp}.json"
                with open(filename, "w") as f:
                    json.dump(data, f, indent=2)
                return jsonify({"status": "success", "filename": filename})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})

        @self.app.route('/feedback', methods=['GET', 'POST'])
        def feedback_page():
            if request.method == 'POST':
                sound = request.form['sound_quality']
                comfort = request.form['environment_comfort']
                attention = request.form['attention_level']
                comment = request.form['comment']
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                feedback = f"{now} | Son: {sound}, Confort: {comfort}, Attention: {attention}, Commentaire: {comment}\n"
                feedback_path = os.path.join('data', 'student_feedback.txt')
                with open(feedback_path, 'a') as f:
                    f.write(feedback)
                return "✅ Merci pour votre retour ! <a href='/feedback'>Retour</a>"
            return render_template('feedback.html')

        @self.app.route('/feedbacks')
        def show_feedbacks():
            feedbacks = []
            feedback_file = os.path.join("data", "student_feedback.txt")
            if os.path.exists(feedback_file):
                with open(feedback_file, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        parts = line.strip().split('|')
                        if len(parts) >= 5:
                            feedbacks.append({
                                "date": parts[0].strip(),
                                "sound": parts[1].split(':')[1].strip(),
                                "comfort": parts[2].split(':')[1].strip(),
                                "attention": parts[3].split(':')[1].strip(),
                                "comment": parts[4].split(':')[1].strip() if ':' in parts[4] else ''
                            })
            return render_template("feedback_list.html", feedbacks=feedbacks)

    def get_current_data(self):
        try:
            if os.path.exists(self.config.HISTORY_DATA_FILE):
                with open(self.config.HISTORY_DATA_FILE, "r") as f:
                    history = [float(line.strip()) for line in f.readlines()]
                    current_score = history[-1] if history else 0
            else:
                current_score = 0
                history = []

            attention_data = self.read_attention_details()
            audio_data = self.read_audio_data()
            env_data = self.read_environment_data()

            return {
                "score": current_score,
                "history": history,
                "attention": attention_data,
                "audio": audio_data,
                "environment": env_data,
                "alert_threshold": self.config.ALERT_THRESHOLD,
                "update_interval": self.config.UI_UPDATE_INTERVAL
            }
        except Exception as e:
            print(f"Erreur de lecture des données: {str(e)}")
            return {
                "score": 0,
                "history": [],
                "attention": {"average": 0, "individual": {}},
                "audio": {"volume": 0, "talking": 0, "noise": 0},
                "environment": {"co2": 0, "temperature": 0, "humidity": 0, "noise": 0},
                "alert_threshold": self.config.ALERT_THRESHOLD,
                "update_interval": self.config.UI_UPDATE_INTERVAL
            }

    def read_attention_details(self):
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

    def generate_attention_chart(self, history):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=history[-20:],
            mode='lines',
            name='Attention'
        ))
        fig.update_layout(
            yaxis_range=[0, 100],
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def generate_environment_chart(self, env_data):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["CO2", "Température", "Humidité"],
            y=[env_data['co2'], env_data['temperature'], env_data['humidity']],
            name='Environnement'
        ))
        fig.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def start(self):
        self.app.run(debug=False, use_reloader=False, port=5000)

    def stop(self):
        pass
