import numpy as np
import wave
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.signal import spectrogram

plt.rcParams.update({"font.family": "serif", "font.size": 10, "axes.titlesize": 11, "axes.edgecolor": "black", "figure.facecolor": "white"})

def load_wav(path):
    with wave.open(path, 'rb') as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32), w.getframerate()

print("Loading raw and cleaned audio")
raw_audio, sr = load_wav("war-intercept.wav")
clean_audio, _ = load_wav("warinterceptCleaned.wav")
print(f"Raw: {len(raw_audio)/sr:.1f} s, cleaned: {len(clean_audio)/sr:.1f} s")

# ---------------------------------------------------------
# GRAPH 1: Standard 2D FFT Spectrum
# ---------------------------------------------------------
print("Plotting FFT spectrum (figure 1)")
freqs = np.fft.rfftfreq(len(raw_audio), d=1/sr)
raw_rfft = np.abs(np.fft.rfft(raw_audio))
clean_rfft = np.abs(np.fft.rfft(clean_audio))
raw_mag = 20 * np.log10(raw_rfft + 1e-9)
clean_mag = 20 * np.log10(clean_rfft + 1e-9)

idx_700 = np.where((freqs >= 695) & (freqs <= 705))[0]
if len(idx_700) > 0:
    print(f"700 Hz peak: {np.max(raw_mag[idx_700]):.1f} dB before, {np.max(clean_mag[idx_700]):.1f} dB after")

fig, axes = plt.subplots(2, 1, figsize=(10, 6))
axes[0].plot(freqs, raw_mag, color='black', linewidth=0.6)
axes[0].set_title('Raw recording')
axes[0].set_xlim(0, 5000); axes[0].grid(True, linestyle=':', alpha=0.5)
axes[0].set_ylabel('Magnitude (dB)')

axes[1].plot(freqs, clean_mag, color='black', linewidth=0.6)
axes[1].set_title('After cleaning')
axes[1].set_xlim(0, 5000); axes[1].grid(True, linestyle=':', alpha=0.5)
axes[1].set_ylabel('Magnitude (dB)'); axes[1].set_xlabel('Frequency (Hz)')

plt.tight_layout()
plt.savefig("02fig1_fft.png", dpi=150)
plt.close()

# ---------------------------------------------------------
# GRAPH 2: Standard 2D Spectrogram (Time vs Frequency)
# ---------------------------------------------------------
print("Plotting spectrogram (figure 2)")
fig, axes = plt.subplots(2, 1, figsize=(10, 6))
print("Using the first 30 seconds")
for ax, audio, title, cmap in zip(axes, [raw_audio, clean_audio], ['Raw recording', 'After cleaning'], ['gray_r', 'gray_r']):
    segment = audio[:sr*30] # First 30 seconds
    f, t, Sxx = spectrogram(segment, fs=sr, nperseg=1024, noverlap=512)
    mask = f <= 5000
    ax.pcolormesh(t, f[mask], 10*np.log10(Sxx[mask] + 1e-12), shading='gouraud', cmap=cmap, vmin=-80, vmax=0)
    ax.set_title(title); ax.set_ylabel('Frequency (Hz)')
axes[1].set_xlabel('Time (seconds)')
plt.tight_layout()
plt.savefig("02fig2_spectrogram.png", dpi=150)
plt.close()

# ---------------------------------------------------------
# GRAPH 3: The 3D FFT Waterfall Plot
# ---------------------------------------------------------
print("Plotting 3D spectrum (figure 3), this can take a while")
fig = plt.figure(figsize=(14, 6))

# We take a small 1.5 second snippet so the 3D render doesn't crash the computer
snippet_raw = raw_audio[sr*10 : int(sr*11.5)]
print("Using the slice from 10.0 s to 11.5 s")
snippet_clean = clean_audio[sr*10 : int(sr*11.5)]

for i, (audio, title, color_map) in enumerate(zip([snippet_raw, snippet_clean], 
                                                  ['Raw recording', 'After cleaning'], 
                                                  ['Greys', 'Greys'])):
    
    f, t, Sxx = spectrogram(audio, fs=sr, nperseg=512, noverlap=256)
    
    # Filter to only show 0 to 4000 Hz for better visibility
    mask = (f >= 0) & (f <= 4000)
    f_masked = f[mask]
    Sxx_masked = 10 * np.log10(Sxx[mask, :] + 1e-10)
    
    # Create 3D Meshgrid
    T, F = np.meshgrid(t, f_masked)
    
    ax = fig.add_subplot(1, 2, i+1, projection='3d')
    
    # Plot the 3D surface
    surf = ax.plot_surface(T, F, Sxx_masked, cmap=color_map, edgecolor='none', alpha=0.9)
    
    ax.set_title(title, pad=20)
    ax.set_xlabel('Time (sec)')
    ax.set_ylabel('Freq (Hz)')
    ax.set_zlabel('Magnitude (dB)')
    
    # Adjust viewing angle for best 3D perspective
    ax.view_init(elev=35, azim=-45)

plt.tight_layout()
plt.savefig("02fig3_3D_FFT.png", dpi=200)
plt.close()

print("Saved fft.png, spectrogram.png, 3D_FFT.png")
