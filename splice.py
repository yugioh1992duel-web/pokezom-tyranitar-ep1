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
q1 = quote_clip('dex_a'); q2 = quote_clip('dex_b')
print('quote durations:', len(q1)/SR, len(q2)/SR)

# splice boundaries: index of word AFTER which we insert
i_q1 = next(i for i,w in enumerate(words) if w['w'].lower().startswith('quote'))
i_q2 = next(i for i,w in enumerate(words) if w['w'].lower()=='as' and words[i-1]['w'].lower().startswith('magazine'))
print('splice after word idx', i_q1, words[i_q1], '|', i_q2, words[i_q2])

def sil(sec): return np.zeros(int(sec*SR), dtype=np.float32)
chunks = []
cur = max(0, int((words[0]['s'] - 0.25) * SR))
for i, w in enumerate(words):
    if i == len(words) - 1: break
    nxt = words[i+1]
    gap = nxt['s'] - w['e']
    end_here = int((w['e'] + 0.05) * SR)
    if i == i_q1:
        chunks.append(main[cur:end_here]); chunks.append(sil(0.35)); chunks.append(q1); chunks.append(sil(0.30))
        cur = int((nxt['s'] - 0.05) * SR)
    elif i == i_q2:
        chunks.append(main[cur:end_here]); chunks.append(sil(0.30)); chunks.append(q2); chunks.append(sil(0.25))
        cur = int((nxt['s'] - 0.05) * SR)
    elif gap > 0.55:
        chunks.append(main[cur:int((w['e'] + 0.19) * SR)])
        cur = int((nxt['s'] - 0.19) * SR)
chunks.append(main[cur:int((words[-1]['e'] + 0.35) * SR)])
out = np.concatenate(chunks)
print('assembled duration:', len(out)/SR)
save(out, 'vo_spliced_raw.wav')
# timestamps of the joins in the assembled file, for verification
t = 0.0; marks = []
ci = 0
for c in chunks:
    d = len(c)/SR
    if ci in (1,5): pass
    t += d; ci += 1
