def compute_global_score(audio, video, environment):
    audio_score = audio.get("score", 0)
    video_score = video.get("score", 0)
    env_score = environment.get("score", 0)
    # Pondération à ajuster selon tes besoins
    return round(0.4 * audio_score + 0.4 * video_score + 0.2 * env_score, 2)