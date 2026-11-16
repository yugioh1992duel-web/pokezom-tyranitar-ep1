import json, subprocess, numpy as np
SR = 24000
def load(path):
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',path,'-ac','1','-ar',str(SR),'-f','f32le','-'])
    return np.frombuffer(raw, dtype=np.float32).copy()
def save(arr, path):
    p = subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','pcm_s16le',path], input=arr.astype(np.float32).tobytes())
    assert p.returncode == 0
main = load('main_raw.wav'); qa = load('quotes_daro_raw.wav')
ws = json.load(open('quotes_daro_timings.json'))['words']
q1w, q2w = ws[:15], ws[15:]
def clip(a, wlist):
    s = max(0, int((wlist[0]['s'] - 0.12) * SR)); e = min(len(a), int((wlist[-1]['e'] + 0.15) * SR))
    return a[s:e]
q1, q2 = clip(qa, q1w), clip(qa, q2w)
def rms(a): return float(np.sqrt(np.mean(a.astype(np.float64)**2)))
# gentle level match: quote takes vs main's local level near the joins
loc1 = main[int(165*SR):int(180*SR)]; loc2 = main[int(294*SR):int(310*SR)]
for name, q, loc in [('Q1', q1, loc1), ('Q2', q2, loc2)]:
    g = rms(loc) / max(rms(q), 1e-6)
    print(name, 'rms', round(rms(q),4), 'local main rms', round(rms(loc),4), 'gain', round(g,3))
    if name == 'Q1': q1 = (q1 * np.clip(g, 0.65, 1.3)).astype(np.float32)
    else: q2 = (q2 * np.clip(g, 0.65, 1.3)).astype(np.float32)
def sil(sec): return np.zeros(int(sec*SR), dtype=np.float32)
def fade(a, ms=20):
    n = int(ms/1000*SR); a = a.copy()
    if len(a) > 2*n:
        r = np.linspace(0, 1, n, dtype=np.float32)
        a[:n] *= r; a[-n:] *= r[::-1]
    return a
# word-boundary cuts (main_raw timings): Q1 @173.60 (as v2); Q2 split at 301.24 = end of "as" / start of "a"
cut1 = int(173.60 * SR); cut2 = int(301.24 * SR)
out = np.concatenate([
    main[:cut1], sil(0.12), fade(q1), sil(0.22),
    main[cut1:cut2], sil(0.16), fade(q2), sil(0.20),
    main[cut2:]])
print('VO v3 duration:', round(len(out)/SR, 2), '(v2 was 450.58)')
save(out, 'vo_final_v3.wav')
