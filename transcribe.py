import sys, json, subprocess, numpy as np
from faster_whisper import WhisperModel
def load(path):
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',path,'-ac','1','-ar','16000','-f','f32le','-'])
    return np.frombuffer(raw, dtype=np.float32)
model = WhisperModel('base.en', device='cpu', compute_type='int8')
for name in sys.argv[1:]:
    segs, _ = model.transcribe(load(name + '.wav'), word_timestamps=True, language='en')
    words = []
    text = []
    for s in segs:
        text.append(s.text.strip())
        for w in (s.words or []):
            words.append({'w': w.word.strip(), 's': round(w.start,2), 'e': round(w.end,2)})
    json.dump({'text': ' '.join(text), 'words': words}, open(name + '_timings.json','w'), indent=1)
    print('=====', name, f"({len(words)} words)")
    print(' '.join(text)[:600])
