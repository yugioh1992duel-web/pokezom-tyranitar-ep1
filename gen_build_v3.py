import json, os, shutil

B = os.path.dirname(os.path.abspath(__file__))
words = json.load(open(os.path.join(B, 'vo_final_v3_timings.json')))['words']
types = json.load(open('/home/hatch/workspace/pokezom_factory/types.json'))
template = open(os.path.join(B, 'template/index.html')).read()
GOLD = {"600","700","hundred","rocket","jet","engine","loading","dark","mega","mountain","mountains","maps","dubious","billion","fifty-five","55","shadow","parents","cocoon","robot","machine","redrawn","buries"}

# ---- caption dictionary pass: whisper garbles -> script-canonical spellings ----
FIX = {'tyrannatar': 'Tyranitar', 'tyranitar': 'Tyranitar', 'larvatar': 'Larvitar', 'larvitar': 'Larvitar',
       'pupatar': 'Pupitar', 'pupitar': 'Pupitar',
       'suikun': 'Suicune', 'swee-koon': 'Suicune', 'pokerstar': 'PokéStar',
       'volcanian': 'Volcanion', 'elaine': 'Alain', "elaine's": "Alain's",
       'berries': 'buries', 'sandstream': 'Sand Stream', "game's": 'games',
       'eighteats': 'It eats', 'retrawn': 'redrawn'}
MERGE = {('pew', '-patar'): 'Pupitar', ('re', '-drawn'): 'redrawn', ('re', '-draw'): 'redraw'}

def fix_words(ws):
    out, i = [], 0
    while i < len(ws):
        w = ws[i]; raw = w['w']; core = raw.strip('.,!?'); trail = raw[len(raw.rstrip('.,!?')):] if raw.rstrip('.,!?') != raw else ''
        low = core.lower()
        nxt = ws[i + 1]['w'].strip('.,!?').lower() if i + 1 < len(ws) else ''
        nxt2 = ws[i + 2]['w'].strip('.,!?').lower() if i + 2 < len(ws) else ''
        prv = ws[i - 1]['w'].strip('.,!?').lower() if i > 0 else ''
        prv2 = ws[i - 2]['w'].strip('.,!?').lower() if i > 1 else ''
        if (low, nxt) in MERGE:
            merged = MERGE[(low, nxt)]
            t2 = ws[i + 1]['w']; tr2 = t2[len(t2.rstrip('.,!?')):] if t2.rstrip('.,!?') != t2 else ''
            out.append({'w': merged + tr2, 's': w['s'], 'e': ws[i + 1]['e']}); i += 2; continue
        if low == 'breaks' and out and out[-1]['w'].strip('.,!?').lower() == 'no':
            out.append({'w': 'brakes' + trail, 's': w['s'], 'e': w['e']}); i += 1; continue
        # capitalization pass (v3): proper nouns whisper lowercases
        cap = None
        if low == 'gold' and nxt == 'and' and nxt2 == 'silver': cap = 'Gold'
        elif low == 'silver' and prv == 'and' and prv2 == 'gold': cap = 'Silver'
        elif low == 'mega' and nxt in ('tyranitar', 'evolutions', 'evolution', 'wave', 'evolves'): cap = 'Mega'
        elif low == 'shadow' and nxt == 'tyranitar': cap = 'Shadow'
        elif low == 'iron' and nxt == 'thorns': cap = 'Iron'
        elif low == 'thorns' and prv == 'iron': cap = 'Thorns'
        if cap:
            out.append({'w': cap + trail, 's': w['s'], 'e': w['e']}); i += 1; continue
        if low in FIX:
            rep = FIX[low]
            parts = rep.split(' ')
            parts[-1] = parts[-1] + trail
            out.append({'w': ' '.join(parts), 's': w['s'], 'e': w['e']}); i += 1; continue
        out.append(w); i += 1
    return out

def captions(start, end):
    ws = [w for w in fix_words(words) if start <= w['s'] < end
          and not (w['w'].strip('.,!?').lower() == 'subscribe' and w['s'] > 440)]
    chunks, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 9 or (len(cur) >= 5 and w['w'].rstrip().endswith(('.', '!', '?'))):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    return [[round(c[0]['s'] - start, 2), ' '.join(w['w'] for w in c),
             [round(w['s'] - start, 2) for w in c],
             [i for i, w in enumerate(c) if w['w'].lower().strip('.,!?') in GOLD]] for c in chunks]

def hero(name, size=760, x=1080, y=185, tin=0.3, tout=None, sil=0, punch=None, white=False, evoIn=False, evoOutAt=None, jet=None):
    h = {"art": name + ".png", "sil": name + "_sil.png", "x": x, "y": y, "size": size,
         "in": tin, "silUntil": sil, "idle": [tin + 1.2, 999]}
    if tout is not None: h["out"] = tout
    if punch: h["punch"] = punch
    if white: h["white"] = name + "_white.png"
    if evoIn: h["evoIn"] = True
    if evoOutAt is not None: h["evoOutAt"] = evoOutAt
    if jet is not None: h["jet"] = {"at": jet}
    return h

def hl(t, html, out, x=70, y=560, size=76): return {"at": t, "html": html, "out": out, "x": x, "y": y, "size": size}
def chip(t, html, out, x=70, y=880): return {"at": t, "html": html, "out": out, "x": x, "y": y}
def clip(seq, frames, t, dur, label=None, framed=False, hideHud=False):
    c = {"dir": seq, "frames": frames, "at": t, "dur": dur, "mode": "framed" if framed else "full"}
    if label: c["label"] = label
    if framed: c.update({"x": 520, "y": 250, "w": 880, "h": 494})
    if hideHud: c["hideHud"] = True
    return c
def still(img, at, out, label=None, x=70, y=545, w=700, h=330, fit=None):
    s = {"img": img, "at": at, "out": out, "x": x, "y": y, "w": w, "h": h}
    if label: s["label"] = label
    if fit: s["fit"] = fit
    return s

def have(img): return os.path.exists(os.path.join(B, 'assets', img))

# v3 segment map — boundaries re-measured on vo_final_v3 word timings
# (splice delta lands inside s6: s7/s8 shift -0.20s; s4/s5 ~0; s6 start -0.02)
SEGS = [
 dict(id='s0', start=0.0, dur=23.58, types=["Rock","Dark"], formLabel="",
      envFX=[{"kind": "dust", "at": 0.0, "out": 23.4}],
      clips=[clip("seqC2", 108, 0, 5.8)],
      heroes=[hero("Pupitar", 720, tin=5.5, tout=7.8, sil=99), hero("Iron_Thorns", 760, tin=7.8, tout=12.4, sil=99), hero("Mega_Tyranitar", 820, tin=12.4, tout=15.3, sil=99)],
      titleCard={"at": 15.5, "big": "EVERY TYRANITAR", "sub": "EXPLAINED — AND RANKED", "out": 23.3}),
 dict(id='s1', start=23.58, dur=68.16, types=["Rock","Ground"], formLabel="FORM 1 OF 6",
      envFX=[{"kind": "dust", "at": 0.0, "out": 68.0}],
      heroes=[hero("Larvitar", 700, x=1100, y=210, white=True, evoOutAt=66.9)],
      nameBlock={"name": "LARVITAR", "sub": "THE ROCK SKIN POKÉMON · #246", "pills": ["Rock","Ground"], "at": 0.5},
      headlines=[hl(9.2, "IT HAS NEVER SEEN<br/>ITS <span class='gold'>PARENTS' FACES</span>", 16.6)],
      quoteCard={"at": 17.0, "text": "It feeds on soil. After it has eaten a large mountain, it will fall asleep so it can grow.", "src": "POKÉDEX — POKÉMON GOLD", "out": 31.0},
      chips=[chip(24.8, "BORN UNDERGROUND <span class='gold'>✓</span>", 31.5),
             chip(25.8, "EAT A MOUNTAIN <span class='gold'>✓</span>", 31.5),
             chip(26.8, "TAKE A NAP <span class='gold'>✓</span>", 31.5)],
      stills=[still("still_ash.jpg", 40.6, 43.4 if have("still_mother.jpg") else 48.0, "ASH'S LARVITAR — JOHTO")]
             + ([still("still_mother.jpg", 43.5, 49.8, "ITS MOTHER — A TYRANITAR")] if have("still_mother.jpg") else [])
             + [still("still_mtsilver_red.jpg" if have("still_mtsilver_red.jpg") else "still_mtsilver.jpg", 53.5, 62.0, "FOUND ONLY AT MT. SILVER")]),
 dict(id='s2', start=91.74, dur=54.68, types=["Rock","Ground"], formLabel="FORM 2 OF 6",
      envFX=[{"kind": "dust", "at": 0.0, "out": 54.5}],
      heroes=[hero("Pupitar", 760, punch=24.1, sil=1.15, white=True, evoIn=True, evoOutAt=53.5, jet=24.05)],
      nameBlock={"name": "PUPITAR", "sub": "THE HARD SHELL POKÉMON · #247", "pills": ["Rock","Ground"], "at": 0.5},
      quoteCard={"at": 12.2, "text": "Its shell is as hard as sheet rock, and it is also very strong. Its thrashing can topple a mountain.", "src": "POKÉDEX — POKÉMON GOLD", "out": 18.6},
      headlines=[hl(23.6, "A COCOON WITH<br/>A <span class='gold'>JET ENGINE</span>", 30.5),
                 hl(35.7, "IT'S NOT SLEEPING.<br/>IT'S <span class='gold'>LOADING.</span>", 41.5)],
      loadBar={"at": 35.7, "out": 41.5},
      chips=[chip(41.7, "EVOLVES AT LEVEL <span class='gold'>55</span>", 49.0)]),
 dict(id='s3', start=146.42, dur=79.20, types=["Rock","Dark"], formLabel="FORM 3 OF 6",
      heroes=[hero("Tyranitar", 820, punch=1.2, sil=1.15, white=True, evoIn=True)],
      nameBlock={"name": "TYRANITAR", "sub": "THE ARMOR POKÉMON · #248", "pills": ["Rock","Ground"], "at": 0.6},
      pillSwap={"at": 16.2, "pills": ["Rock", "Dark"]},
      statAnim={"at": 2.6, "from": 0, "to": 600, "label": "TOTAL STATS", "x": 70, "y": 880, "out": 14.0},
      headlines=[hl(23.2, "IT TURNS TO THE<br/><span class='gold'>DARK SIDE</span>", 26.5)],
      quoteCard={"at": 26.9, "text": "If it rampages, it knocks down mountains and buries rivers. Maps must be redrawn afterward.", "src": "POKÉDEX — DIAMOND · PEARL · PLATINUM", "out": 36.0},
      envFX=[{"kind": "sand", "at": 38.6, "out": 59.5}],
      chips=[chip(39.0, "ABILITY: <span class='gold'>SAND STREAM</span> — A STORM ON ENTRY", 46.6)],
      stills=([still("still_vgc.jpg", 51.4, 59.4, "COMPETITIVE — 20+ YEARS A TOP PICK")] if have("still_vgc.jpg") else [])
             + ([still("still_darkball.png", 60.4, 65.8, "THE DARK BALL — POKÉMON 4EVER")] if have("still_darkball.png") else []),
      clips=[clip("seqA", 288, 66.4, 12.0, "CELEBI: VOICE OF THE FOREST (2001)")]),
 dict(id='s4', start=225.62, dur=30.20, types=["Steel","Electric"], formLabel="BONUS FORM", mood="mecha",
      heroes=[hero("MT", 780, tout=18.9), hero("MT2", 780, tin=19.05)],
      nameBlock={"name": "MECHA TYRANITAR", "sub": "POKÉSTAR STUDIOS · MOVIE PROP", "pills": ["Steel"], "at": 0.5},
      pillSwap={"at": 19.0, "pills": ["Steel", "Electric"]},
      stills=([still("still_pokestar.png", 4.2, 13.2, "POKÉSTAR STUDIOS — BLACK 2 · WHITE 2")] if have("still_pokestar.png") else []),
      chips=[chip(14.6, "<span class='gold'>M-T</span> — THE ORIGINAL PROP", 18.6),
             chip(18.9, "<span class='gold'>M-T TWO</span> — ELECTRIC UPGRADE", 22.0)],
      headlines=[hl(22.3, "GAME FREAK BUILT IT<br/>AS A <span class='gold'>JOKE</span>", 29.8, y=690)]),
 dict(id='s5', start=255.82, dur=36.48, types=["Rock","Dark"], formLabel="FORM 4 OF 6", mood="shadow",
      heroes=[hero("Shadow_Tyranitar", 820)],
      nameBlock={"name": "SHADOW TYRANITAR", "sub": "COLOSSEUM · THE FINAL BOSS'S ACE", "pills": ["Rock","Dark"], "at": 0.5},
      stills=[still("still_colosseum.jpg", 1.4, 10.5, "POKÉMON COLOSSEUM (2003)", y=660, h=280),
              still("still_go.png", 11.8, 22.0, "POKÉMON GO", y=660, h=210, fit="contain")]
             + ([still("still_relicstone.png", 23.2, 30.2, "PURIFICATION — RELIC STONE, AGATE VILLAGE", y=670, w=620, h=260, fit="contain")] if have("still_relicstone.png") else []),
      chips=[chip(14.9, "<span class='gold'>+20% ATTACK</span>", 17.9, y=892),
             chip(18.1, "<span class='red'>−20% DEFENSE</span>", 21.5, y=892)],
      clips=[] if have("still_relicstone.png") else [{"dir": "seqShadow", "frames": 144, "at": 24.5, "dur": 6.0, "mode": "framed", "label": "SHADOW TYRANITAR", "x": 70, "y": 650, "w": 711, "h": 280}],
      headlines=[hl(34.6, "THE SAFETY IS <span class='gold'>OFF</span>", 36.3, y=705)]),
 dict(id='s6', start=292.30, dur=45.10, types=["Electric","Rock"], formLabel="FORM 5 OF 6", mood="future",
      envFX=[{"kind": "future", "at": 0.5, "out": 44.8}],
      heroes=[hero("Iron_Thorns", 800)],
      nameBlock={"name": "IRON THORNS", "sub": "PARADOX POKÉMON · #995", "pills": ["Rock","Electric"], "at": 0.5},
      quoteCard={"at": 16.0, "text": "A Tyranitar from one billion years into the future.", "src": "POKÉDEX — POKÉMON SCARLET", "out": 22.0},
      chips=[chip(21.3, "SOURCE: A <span class='gold'>DUBIOUS</span> MAGAZINE", 25.5),
             chip(25.8, "<span class='gold'>570</span> TOTAL STATS", 29.0),
             chip(28.4, "ABILITY: <span class='gold'>QUARK DRIVE</span>", 33.5)],
      stills=([still("still_occulture.png", 24.0, 29.2, "OCCULTURE — THE DUBIOUS MAGAZINE")] if have("still_occulture.png") else [])
             + [still("still_areazero.jpg", 33.2, 40.5, "AREA ZERO — POKÉMON VIOLET")]),
 dict(id='s7', start=337.40, dur=60.98, types=["Rock","Dark"], formLabel="FORM 6 OF 6", mood="mega",
      heroes=[hero("Mega_Tyranitar", 860, punch=8.1)],
      nameBlock={"name": "MEGA TYRANITAR", "sub": "MEGA EVOLUTION · SINCE 2013", "pills": ["Rock","Dark"], "at": 0.6},
      statAnim={"at": 7.9, "from": 600, "to": 700, "label": "TOTAL STATS", "x": 70, "y": 880, "out": 30.0},
      headlines=[hl(14.5, "ATTACK 164 — HIGHER THAN<br/>MOST <span class='gold'>LEGENDARIES</span>", 20.5, y=690)],
      envFX=[{"kind": "sand", "at": 20.4, "out": 29.0}, {"kind": "sand", "at": 48.0, "out": 60.9}],
      chips=[chip(53.6, "<span class='gold'>700</span> TOTAL STATS — A WALKING MOUNTAIN", 60.5)],
      clips=[clip("seqB", 192, 32.5, 8.0, "MEGA EVOLUTION SPECIAL — VS ALAIN"),
             clip("seqD", 144, 42.3, 6.0, "THE MEGA WAVE ARMY — VOLCANION (2016)", framed=True, hideHud=True)]),
 dict(id='s8', start=398.38, dur=52.00, types=["Rock","Dark"], formLabel="THE RANKING",
      ranking={"slots": [{"art": a + ".png", "x": 34 + i * 314, "y": 330, "w": 280, "num": 6 - i, "name": n, "in": 0.4 + i * 0.15}
                          for i, (a, n) in enumerate([("Larvitar","LARVITAR"),("Pupitar","PUPITAR"),("Shadow_Tyranitar","SHADOW"),("Iron_Thorns","IRON THORNS"),("Tyranitar","TYRANITAR"),("Mega_Tyranitar","MEGA TYRANITAR")])],
               "hits": [{"idx": i, "t": t} for i, t in enumerate([3.08, 7.02, 12.56, 19.20, 25.36, 28.90])]},
      headlines=[hl(35.0, "YOUR TURN — <span class='gold'>VOTE BELOW!</span>", 45.3, x=480, y=130, size=84)],
      chips=[chip(46.6, "NEXT EPISODE: <span class='gold'>EVERY DRAGONITE</span>", 51.7, x=620, y=790)]),
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
        for suf in ('.png', '_sil.png', '_white.png'):
            src = os.path.join(B, 'assets', a + suf)
            if os.path.exists(src): shutil.copy(src, os.path.join(d, 'assets', a + suf))
    for st in cfg.get('stills', []):
        src = os.path.join(B, 'assets', st['img'])
        if os.path.exists(src): shutil.copy(src, os.path.join(d, 'assets', st['img']))
        else: print('MISSING STILL:', cfg['id'], st['img'])
    for c in cfg.get('clips', []):
        shutil.copytree(os.path.join(B, 'assets', c['dir']), os.path.join(d, 'assets', c['dir']), dirs_exist_ok=True)
    shutil.copy('/home/hatch/workspace/pokezom_tristorm_build/hf/assets/gsap.min.js', os.path.join(d, 'assets', 'gsap.min.js'))
    print(cfg['id'], 'ok, caps', len(cfg['captions']))
print('ALL SEGMENTS REBUILT (v3)')
