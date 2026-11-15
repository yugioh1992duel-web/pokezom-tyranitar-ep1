import json, os, shutil

B = os.path.dirname(os.path.abspath(__file__))
words = json.load(open(os.path.join(B, 'vo_final_timings.json')))['words']
types = json.load(open('/home/hatch/workspace/pokezom_factory/types.json'))
template = open(os.path.join(B, 'template/index.html')).read()
GOLD = {"600","700","hundred","rocket","jet","engine","loading","dark","mega","mountain","mountains","maps","dubious","billion","fifty-five","55","shadow","parents","cocoon","robot","machine","redrawn"}

def captions(start, end):
    ws = [w for w in words if start <= w['s'] < end]
    chunks, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 9 or (len(cur) >= 5 and w['w'].rstrip().endswith(('.', '!', '?'))):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    return [[round(c[0]['s'] - start, 2), ' '.join(w['w'] for w in c),
             [round(w['s'] - start, 2) for w in c],
             [i for i, w in enumerate(c) if w['w'].lower().strip('.,!?') in GOLD]] for c in chunks]

def hero(name, size=760, x=1080, y=185, tin=0.3, tout=None, sil=0, punch=None):
    h = {"art": name + ".png", "sil": name + "_sil.png", "x": x, "y": y, "size": size,
         "in": tin, "silUntil": sil, "idle": [tin + 1.2, 999]}
    if tout is not None: h["out"] = tout
    if punch: h["punch"] = punch
    return h

def hl(t, html, out, x=70, y=560, size=76): return {"at": t, "html": html, "out": out, "x": x, "y": y, "size": size}
def chip(t, html, out, x=70, y=880): return {"at": t, "html": html, "out": out, "x": x, "y": y}
def clip(seq, frames, t, dur, label=None, framed=False):
    c = {"dir": seq, "frames": frames, "at": t, "dur": dur, "mode": "framed" if framed else "full"}
    if label: c["label"] = label
    if framed: c.update({"x": 520, "y": 250, "w": 880, "h": 494})
    return c

SEGS = [
 dict(id='s0', start=0.0, dur=23.58, types=["Rock","Dark"], formLabel="",
      clips=[clip("seqC2", 108, 0, 4.5)],
      heroes=[hero("Pupitar", 720, tin=5.0, tout=7.8, sil=99), hero("Iron_Thorns", 760, tin=7.8, tout=12.4, sil=99), hero("Mega_Tyranitar", 820, tin=12.4, tout=15.3, sil=99)],
      titleCard={"at": 15.5, "big": "EVERY TYRANITAR", "sub": "EXPLAINED — AND RANKED", "out": 23.3}),
 dict(id='s1', start=23.58, dur=68.16, types=["Rock","Ground"], formLabel="FORM 1 OF 6",
      heroes=[hero("Larvitar", 700, x=1100, y=210)],
      nameBlock={"name": "LARVITAR", "sub": "THE ROCK SKIN POKÉMON · #246", "pills": ["Rock","Ground"], "at": 0.5},
      headlines=[hl(9.2, "IT HAS NEVER SEEN<br/>ITS <span class='gold'>PARENTS' FACES</span>", 16.6)],
      quoteCard={"at": 17.0, "text": "It feeds on soil. After it has eaten a large mountain, it will fall asleep so it can grow.", "src": "POKÉDEX — POKÉMON GOLD", "out": 31.0},
      chips=[chip(54.04, "FOUND ONLY AT <span class='gold'>MT. SILVER</span>", 62.5)]),
 dict(id='s2', start=91.74, dur=54.68, types=["Rock","Ground"], formLabel="FORM 2 OF 6",
      heroes=[hero("Pupitar", 760, punch=23.7)],
      nameBlock={"name": "PUPITAR", "sub": "THE HARD SHELL POKÉMON · #247", "pills": ["Rock","Ground"], "at": 0.5},
      headlines=[hl(23.4, "A COCOON WITH<br/>A <span class='gold'>JET ENGINE</span>", 30.5),
                 hl(35.7, "IT'S NOT SLEEPING.<br/>IT'S <span class='gold'>LOADING.</span>", 41.5)],
      chips=[chip(41.7, "EVOLVES AT LEVEL <span class='gold'>55</span>", 49.0)]),
 dict(id='s3', start=146.42, dur=81.58, types=["Rock","Dark"], formLabel="FORM 3 OF 6",
      heroes=[hero("Tyranitar", 820, punch=1.2)],
      nameBlock={"name": "TYRANITAR", "sub": "THE ARMOR POKÉMON · #248", "pills": ["Rock","Dark"], "at": 0.6},
      statAnim={"at": 2.6, "from": 0, "to": 600, "label": "TOTAL STATS", "x": 70, "y": 880, "out": 14.0},
      headlines=[hl(23.2, "IT TURNS TO THE<br/><span class='gold'>DARK SIDE</span>", 26.5)],
      quoteCard={"at": 26.8, "text": "If it rampages, it knocks down mountains and buries rivers. Maps must be redrawn afterward.", "src": "POKÉDEX — DIAMOND · PEARL · PLATINUM", "out": 38.6},
      chips=[chip(41.4, "ABILITY: <span class='gold'>SAND STREAM</span> — A STORM ON ENTRY", 49.5)],
      clips=[clip("seqA", 288, 68.9, 12.0, "CELEBI: VOICE OF THE FOREST (2001)")]),
 dict(id='s4', start=228.0, dur=30.18, types=["Steel","Electric"], formLabel="BONUS FORM",
      heroes=[hero("Mecha_Tyranitar", 800)],
      nameBlock={"name": "MECHA TYRANITAR", "sub": "POKÉSTAR STUDIOS · MOVIE PROP", "pills": ["Steel","Electric"], "at": 0.5},
      chips=[chip(14.6, "<span class='gold'>M-T</span> — THE ORIGINAL PROP", 18.6),
             chip(18.9, "<span class='gold'>M-T TWO</span> — ELECTRIC UPGRADE", 22.0)],
      headlines=[hl(22.3, "GAME FREAK BUILT IT<br/>AS A <span class='gold'>JOKE</span>", 29.8)]),
 dict(id='s5', start=258.18, dur=36.5, types=["Dark","Rock"], formLabel="FORM 4 OF 6",
      heroes=[hero("Shadow_Tyranitar", 820)],
      nameBlock={"name": "SHADOW TYRANITAR", "sub": "POKÉMON COLOSSEUM · THE FINAL BOSS'S ACE", "pills": ["Dark","Rock"], "at": 0.5},
      chips=[chip(14.9, "<span class='gold'>+20% ATTACK</span>", 17.9),
             chip(18.1, "<span class='red'>−20% DEFENSE</span>", 21.5)],
      headlines=[hl(34.6, "THE SAFETY IS <span class='gold'>OFF</span>", 36.3)]),
 dict(id='s6', start=294.68, dur=47.3, types=["Rock","Electric"], formLabel="FORM 5 OF 6",
      heroes=[hero("Iron_Thorns", 800)],
      nameBlock={"name": "IRON THORNS", "sub": "PARADOX POKÉMON · #995", "pills": ["Rock","Electric"], "at": 0.5},
      quoteCard={"at": 15.9, "text": "A Tyranitar from one billion years into the future.", "src": "POKÉDEX — POKÉMON SCARLET", "out": 22.4},
      chips=[chip(22.9, "SOURCE: A <span class='gold'>DUBIOUS</span> MAGAZINE", 27.5),
             chip(27.8, "<span class='gold'>570</span> TOTAL STATS", 31.0),
             chip(31.3, "ABILITY: <span class='gold'>QUARK DRIVE</span>", 36.0)]),
 dict(id='s7', start=341.98, dur=60.98, types=["Rock","Dark"], formLabel="FORM 6 OF 6",
      heroes=[hero("Mega_Tyranitar", 860, punch=8.1)],
      nameBlock={"name": "MEGA TYRANITAR", "sub": "MEGA EVOLUTION · SINCE 2013", "pills": ["Rock","Dark"], "at": 0.6},
      statAnim={"at": 7.9, "from": 600, "to": 700, "label": "TOTAL STATS", "x": 70, "y": 880, "out": 30.0},
      headlines=[hl(14.5, "ATTACK 164 — HIGHER THAN<br/>MOST <span class='gold'>LEGENDARIES</span>", 20.5)],
      clips=[clip("seqB", 192, 32.3, 8.0, "MEGA EVOLUTION SPECIAL — VS ALAIN"),
             clip("seqD", 144, 42.0, 6.0, "THE MEGA WAVE ARMY — VOLCANION (2016)", framed=True)]),
 dict(id='s8', start=402.96, dur=52.0, types=["Rock","Dark"], formLabel="THE RANKING",
      ranking={"slots": [{"art": a + ".png", "x": 34 + i * 314, "y": 330, "w": 280, "num": 6 - i, "name": n, "in": 0.4 + i * 0.15}
                          for i, (a, n) in enumerate([("Larvitar","LARVITAR"),("Pupitar","PUPITAR"),("Shadow_Tyranitar","SHADOW"),("Iron_Thorns","IRON THORNS"),("Tyranitar","TYRANITAR"),("Mega_Tyranitar","MEGA TYRANITAR")])],
               "hits": [{"idx": i, "t": t} for i, t in enumerate([3.08, 7.02, 12.56, 19.20, 25.36, 28.90])]},
      headlines=[hl(35.0, "YOUR TURN — <span class='gold'>VOTE BELOW!</span>", 45.3, x=480, y=130, size=84)],
      chips=[chip(45.5, "NEXT EPISODE: <span class='gold'>EVERY DRAGONITE</span>", 51.6, x=620, y=950)]),
]

for cfg in SEGS:
    cfg['world'] = cfg['types']
    cfg['duration'] = cfg['dur']
    cfg['captions'] = captions(cfg['start'], cfg['start'] + cfg['dur'])
    d = os.path.join(B, 'segments', cfg['id']); os.makedirs(os.path.join(d, 'assets'), exist_ok=True)
    html = template.replace('/*__CONFIG__*/', json.dumps(cfg)).replace('/*__TYPES__*/', json.dumps(types)).replace('__DURATION__', str(cfg['dur']))
    open(os.path.join(d, 'index.html'), 'w').write(html)
    json.dump({"$schema":"https://hyperframes.heygen.com/schema/hyperframes.json","registry":"https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry","paths":{"blocks":"compositions","components":"compositions/components","assets":"assets"}}, open(os.path.join(d, 'hyperframes.json'), 'w'), indent=2)
    arts = [h['art'][:-4] for h in cfg.get('heroes', [])] + [s['art'][:-4] for s in cfg.get('ranking', {}).get('slots', [])]
    for a in set(arts):
        for suf in ('.png', '_sil.png'):
            src = os.path.join(B, 'assets', a + suf)
            if os.path.exists(src): shutil.copy(src, os.path.join(d, 'assets', a + suf))
    for c in cfg.get('clips', []):
        shutil.copytree(os.path.join(B, 'assets', c['dir']), os.path.join(d, 'assets', c['dir']), dirs_exist_ok=True)
    shutil.copy('/home/hatch/workspace/pokezom_tristorm_build/hf/assets/gsap.min.js', os.path.join(d, 'assets', 'gsap.min.js'))
    print(cfg['id'], 'ok, caps', len(cfg['captions']))
print('ALL SEGMENTS REBUILT')
