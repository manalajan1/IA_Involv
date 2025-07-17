# 🎓 IA Involvement — Dashboard de Suivi d’Attention et d’Environnement en Classe

Ce projet vise à développer une plateforme intelligente permettant aux enseignants de **mesurer l’attention**, la **qualité de l’environnement** et la **participation en classe** à l’aide de l’IA. Le système utilise des capteurs, de la vision par ordinateur et de l’audio pour fournir un retour en temps réel via un dashboard web.

## 🔧 Stack Technique

- **Backend** : Python (Flask)
- **Frontend** : HTML + Bootstrap + Plotly.js
- **Modèles IA** :
  - Analyse visuelle (détection du regard, attention, présence)
  - STT (Speech-To-Text) avec Whisper pour la transcription audio
  - Analyse environnementale (son, température, humidité, CO2)
- **Base de données** : Fichiers plats (.txt / .json)
- **Monitoring (à venir)** : Grafana + Prometheus / InfluxDB
- **Mode de déploiement** : local (localhost:5000)

---

## 🚀 Fonctionnalités principales

### 👁️ Suivi de l'attention
- Détection de visages
- Calcul de score d’attention individuel et global
- Graphique des fluctuations d’attention
- Suggestions pédagogiques automatiques

### 🔊 Suivi audio (STT)
- Transcription automatique avec Whisper
- Identification des locuteurs (formateur vs étudiants)
- Mesure du temps de parole et du bruit ambiant
- Analyse de pertinence du sujet abordé

### 🌡️ Suivi environnemental
- Température, humidité, CO2, bruit ambiant
- Affichage sous forme de graphique
- Calcul d’un indice de confort et d’impact sur l’attention

### 💬 Feedback étudiant
- Formulaire de retour sur l’environnement, le confort et l’attention
- Stockage des feedbacks
- Visualisation centralisée dans une page dédiée

