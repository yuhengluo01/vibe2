import numpy as np, subprocess, wave, sys, os
SR = 44100; D = float(sys.argv[1])
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bgm", "vibe_bgm.mp3"), "-t", str(D), "-f", "f32le",
                      "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
bgm = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64); n = len(bgm); t = np.arange(n) / SR
bgm /= np.max(np.abs(bgm))
g = np.clip((D - t) / 1.8, 0, 1)
def ramp(t,a,b): return np.clip((t-a)/(b-a),0,1)
X1,X2=8*2.1258,44*2.1258
calm = 0.42
env_ = np.ones(n)
env_ = np.where(t<X1, calm*(1-ramp(t,15.9,16.35))+0.0*ramp(t,15.9,16.35), env_)
env_ = np.where((t>=36*2.1258)&(t<X2), calm+(1-calm)*(1-ramp(t,76.53,77.6)) - calm*ramp(t,92.55,93.0), env_)
env_ = np.clip(env_,0,1)
g = g*env_
bgm *= g[:, None]
sfx = np.load("sfx.npy")[:n]; sfx = np.pad(sfx, (0, n - len(sfx)))
mix = bgm * 0.8 + np.stack([sfx, sfx], 1) * 0.42
mix = np.tanh(mix * 1.1); mix *= 0.89 / np.max(np.abs(mix))
with wave.open("audio.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("mixed", n / SR)
