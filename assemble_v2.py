import subprocess, os, sys, json

B = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(B, 'gh_downloads_v2')
SEGS = ['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']
EXPECT = {'s0': 23.58, 's1': 68.16, 's2': 54.68, 's3': 79.22, 's4': 30.18,
          's5': 36.50, 's6': 45.28, 's7': 60.98, 's8': 52.00}

def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

files = []
for s in SEGS:
    cands = []
    for root, _, fs in os.walk(os.path.join(DL, 'section-' + s)):
        for f in fs:
            if f.endswith('.mp4'): cands.append(os.path.join(root, f))
    assert cands, f'no render found for {s}'
    p = sorted(cands)[0]
    d = dur(p)
    print(f'{s}: {p.split("/")[-1]} {d:.2f}s (expect ~{EXPECT[s]})')
    assert abs(d - EXPECT[s]) < 1.2, f'{s} duration off by {d - EXPECT[s]:.2f}s'
    files.append(p)

lst = os.path.join(B, 'concat_v2.txt')
open(lst, 'w').write('\n'.join(f"file '{p}'" for p in files))
joined = os.path.join(B, 'joined_v2.mp4')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', joined], check=True)
print('joined:', round(dur(joined), 2), 's')

out = '/home/hatch/workspace/your_files/pokezom_longform/Every_Tyranitar_Explained_v2.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', joined, '-i', os.path.join(B, 'mix_final_v2.wav'),
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11', '-c:a', 'aac', '-b:a', '192k',
                '-shortest', out], check=True)
print('FINAL:', out, round(dur(out), 2), 's', round(os.path.getsize(out) / 1e6, 1), 'MB')
