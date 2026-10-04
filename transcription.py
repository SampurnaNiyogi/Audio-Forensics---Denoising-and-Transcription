import whisper
import json
import wave
import numpy as np

def load_wav_for_whisper(path):
    with wave.open(path, 'rb') as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

print("Loading Whisper (small)")
model = whisper.load_model("small")

print("Transcribing warinterceptCleaned.wav, this takes a few minutes")
audio_data = load_wav_for_whisper("warinterceptCleaned.wav")

result = model.transcribe(
    audio_data,
    language='en',
    beam_size=10,
    best_of=10,
    temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
    condition_on_previous_text=False,
    compression_ratio_threshold=2.4,
    logprob_threshold=-1.0,
    no_speech_threshold=0.6
)

text = result['text'].strip()
with open("03transcript.txt", "w", encoding="utf-8") as f:
    f.write(text)

word_count = len(text.split())
print(f"{word_count} words transcribed")
print("transcripted.txt")
