import whisper

model = whisper.load_model("base")  # ou "small" ou "medium" selon ta RAM

result = model.transcribe("data/test_audio.wav")
print("Transcription :")
print(result["text"])
