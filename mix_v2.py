import subprocess, numpy as np, os

SR = 48000
B = os.path.dirname(os.path.abspath(__file__))
CRIES = '/home/hatch/workspace/pokezom_kaiju_build/assets/cries'
SFX = '/home/hatch/workspace/your_files/pokezom_sfx_starter_pack'
BGM = '/home/hatch/workspace/pokezom_kaiju_build/assets/bgm/final_battle_rival.mp3'

def load(path, sr=SR):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(sr), '-f', 'f32le', '-'])
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()

vo = load(os.path.join(B, 'vo_final_v2.wav'))
DUR = len(vo) / SR
mix = vo.copy()

# BGM bed at 0.08, looped to length, 3s fade-out
bgm = load(BGM)
reps = int(np.ceil(len(mix) / len(bgm)))
bed = np.tile(bgm, (reps, 1))[:len(mix)] * 0.08
fade = int(3 * SR)
bed[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix += bed

# jet whoosh: FFT-band noise sweep (low -> high), 0.7s
rng = np.random.default_rng(7)
n = int(0.7 * SR)
noise = rng.standard_normal(n).astype(np.float32)
F = np.fft.rfft(noise); freqs = np.fft.rfftfreq(n, 1 / SR)
swept = np.zeros(n, dtype=np.float32)
steps = 24
for k in range(steps):
    s0, s1 = k * n // steps, (k + 1) * n // steps
    fc = 300 * (2400 / 300) ** (k / (steps - 1))
    band = np.exp(-0.5 * ((freqs - fc) / (fc * 0.55)) ** 2)
    seg = np.fft.irfft(F * band, n)
    env = np.sin(np.pi * (k + 0.5) / steps) ** 1.5
    swept[s0:s1] = seg[s0:s1] * env
swept /= (np.abs(swept).max() + 1e-9)
whoosh = np.stack([swept, swept], axis=1)
np.save(os.path.join(B, 'whoosh_jet.npy'), whoosh)

def place(arr, at, gain):
    i = int(at * SR)
    j = min(len(mix), i + len(arr))
    mix[i:j] += arr[:j - i] * gain

# cries ducked -6dB vs v1 (0.55 -> 0.28); Mega cry moved onto the spoken name (s7 rel 7.6)
place(load(f'{CRIES}/246.ogg'), 24.2, 0.28)
place(load(f'{CRIES}/247.ogg'), 92.3, 0.28)
place(load(f'{CRIES}/248.ogg'), 147.2, 0.28)
place(load(f'{CRIES}/248.ogg'), 345.2, 0.28)
# jet whoosh on the Pupitar rocket beat
place(whoosh, 115.7, 0.7)
# accents
place(load(f'{SFX}/level_up.ogg'), 146.9, 0.45)
place(load(f'{SFX}/level_up.ogg'), 427.5, 0.5)
place(load(f'{SFX}/stat_up.ogg'), 345.5, 0.45)
place(load(f'{SFX}/hit_super_effective.ogg'), 212.8, 0.5)
for t in (401.66, 405.60, 411.14, 417.78, 423.94, 427.48):
    place(load(f'{SFX}/ui_select.ogg'), t, 0.4)

peak = np.abs(mix).max()
print('pre-norm peak:', round(float(peak), 3), 'duration:', round(DUR, 2))
if peak > 0.98: mix *= 0.98 / peak
p = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_s16le', os.path.join(B, 'mix_final_v2.wav')], input=mix.astype(np.float32).tobytes())
assert p.returncode == 0
print('mix_final_v2.wav written')
