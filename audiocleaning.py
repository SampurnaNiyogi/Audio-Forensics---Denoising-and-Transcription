import numpy as np
import wave
import noisereduce as nr
from scipy.signal import stft, istft, butter, filtfilt

def load_wav(path):
    with wave.open(path, 'rb') as w:
        sr = w.getframerate()
        raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0, sr

def save_wav(path, audio, sr):
    audio = np.clip(audio, -1.0, 1.0)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((audio * 32767.0).astype(np.int16).tobytes())

print("Reading war-intercept.wav")
audio, sr = load_wav("war-intercept.wav")
print(f"{len(audio):,} samples at {sr} Hz ({len(audio)/sr:.2f} s)")

print("Removing jamming tones in the STFT domain")
f, t, Zxx = stft(audio, fs=sr, nperseg=4096, noverlap=2048)
print(f"STFT size: {Zxx.shape[0]} bins x {Zxx.shape[1]} frames")

jam_bands = [(690, 710), (1390, 1410), (2590, 2610), (2790, 2810), (4190, 4210)]
bins_deleted = 0
for low_f, high_f in jam_bands:
    idx = np.where((f >= low_f) & (f <= high_f))[0]
    Zxx[idx, :] *= 0.001
    bins_deleted += len(idx)

print(f"Attenuated {bins_deleted} frequency bins in every frame")

_, audio_recovered = istft(Zxx, fs=sr)
audio = audio_recovered[:len(audio)] 

print("Reducing tape hiss")
audio = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.85, n_fft=2048)

print("Applying 300-3400 Hz bandpass filter")
b, a = butter(4, [300 / (0.5 * sr), 3400 / (0.5 * sr)], btype='band')
audio = filtfilt(b, a, audio)

print("Boosting voice (gain of 15)")
pre_boost_max = np.max(np.abs(audio))
audio = np.tanh(audio * 15.0)

max_val = np.max(np.abs(audio))
if max_val > 0:
    audio = (audio / max_val) * 0.95

print(f"Peak level before boost: {pre_boost_max:.4f}, after: {np.max(np.abs(audio)):.4f}")

save_wav("warinterceptCleaned.wav", audio, sr)
print("Saved warinterceptCleaned.wav")
