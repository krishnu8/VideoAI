from utility.stt.whisper_stt import generate_timed_captions as whisper_captions


def generate_timed_captions(audio_filename):
    """Transcribe audio using local Whisper model and return timed caption pairs."""
    return whisper_captions(audio_filename)
