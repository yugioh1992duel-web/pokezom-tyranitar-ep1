import json, subprocess, numpy as np
SR = 24000
def load(path):
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',path,'-ac','1','-ar',str(SR),'-f','f32le','-'])
    return np.frombuffer(raw, dtype=np.float32).copy()
def save(arr, path):
    p = subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','pcm_s16le',path], input=arr.astype(np.float32).tobytes())
    assert p.returncode == 0
main = load('main_raw.wav')
qa = load('quotes_daro_raw.wav')
ws = json.load(open('quotes_daro_timings.json'))['words']
# Q1 = words[0..15] "If ... afterward." ; Q2 = words[16..] "A Tyranitar ... future?"
q1w, q2w = ws[:15], ws[15:]
def clip(a, wlist):
    s = max(0, int((wlist[0]['s'] - 0.12) * SR)); e = min(len(a), int((wlist[-1]['e'] + 0.15) * SR))
    return a[s:e]
q1, q2 = clip(qa, q1w), clip(qa, q2w)
print('q1 secs:', len(q1)/SR, ' q2 secs:', len(q2)/SR)
def sil(sec): return np.zeros(int(sec*SR), dtype=np.float32)
cut1 = int(173.60 * SR); cut2 = int(301.24 * SR)
out = np.concatenate([main[:cut1], sil(0.05), q1, sil(0.30), main[cut1:cut2], sil(0.30), q2, sil(0.25), main[cut2:]])
print('VO v2 duration:', len(out)/SR)
save(out, 'vo_final_v2.wav')
