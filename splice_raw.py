import json, subprocess, numpy as np
SR = 24000
def load(path):
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',path,'-ac','1','-ar',str(SR),'-f','f32le','-'])
    return np.frombuffer(raw, dtype=np.float32).copy()
def save(arr, path):
    p = subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','pcm_s16le',path], input=arr.astype(np.float32).tobytes())
    assert p.returncode == 0
main = load('main_raw.wav')
words = json.load(open('main_raw_timings.json'))['words']
def quote_clip(name):
    a = load(name + '.wav')
    ws = json.load(open(name + '_timings.json'))['words']
    s = max(0, int((ws[0]['s'] - 0.12) * SR)); e = min(len(a), int((ws[-1]['e'] + 0.15) * SR))
    return a[s:e]
q1, q2 = quote_clip('dex_a'), quote_clip('dex_b')
def sil(sec): return np.zeros(int(sec*SR), dtype=np.float32)
# split 1: middle of the natural gap after "Quote," (173.24 -> 173.94)
cut1 = int(173.60 * SR)
# split 2: exactly at end of "as" (301.24), where quote 2 completes the sentence
cut2 = int(301.24 * SR)
out = np.concatenate([main[:cut1], sil(0.05), q1, sil(0.30), main[cut1:cut2], sil(0.30), q2, sil(0.25), main[cut2:]])
print('uncut assembled duration:', len(out)/SR)
save(out, 'vo_final.wav')
