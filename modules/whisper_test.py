import whisper
import time

# Lancement du chronomètre
start_time = time.time()

# Chargement du modèle
model = whisper.load_model("base")

# Transcription avec retour détaillé
result = model.transcribe("data/test_audio.wav", verbose=True)

# Temps total de traitement
end_time = time.time()
print(f"\n⏱️ Temps d'exécution : {end_time - start_time:.2f} secondes\n")

# Affichage des segments avec timestamps
print("🗣️ Segments détectés :\n")
for segment in result["segments"]:
    start = segment["start"]
    end = segment["end"]
    text = segment["text"]
    print(f"[{start:.2f}s - {end:.2f}s] {text}")
