"""Procedural SFX + original music loops (pure python) -> public/assets/audio/{sfx,music}/*.wav
All sounds are synthesised from scratch here (no samples)."""
import array, json, math, os, random, wave

SR = 22050
OUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'assets', 'audio')
for d in ('sfx', 'music'): os.makedirs(os.path.join(OUT, d), exist_ok=True)
rnd = random.Random(42)
TAU = 2 * math.pi
MAN = {'sfx': {}, 'music': {}}

# ------------------------------------------------------------------ core
def N(sec): return int(sec * SR)
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)

def tone(freq, dur, wave_='sine', vib=0.0, vib_rate=5.5, pw=0.5):
    """freq: number or function(t)->Hz."""
    n = N(dur); out = [0.0] * n; ph = 0.0
    f = freq if callable(freq) else (lambda t, F=freq: F)
    for i in range(n):
        t = i / SR
        fr = f(t) * (1 + vib * math.sin(TAU * vib_rate * t))
        ph = (ph + fr / SR) % 1.0
        if wave_ == 'sine': v = math.sin(TAU * ph)
        elif wave_ == 'square': v = 1.0 if ph < pw else -1.0
        elif wave_ == 'saw': v = 2 * ph - 1
        elif wave_ == 'tri': v = 4 * abs(ph - 0.5) - 1
        else: v = 0
        out[i] = v
    return out

def noise(dur): return [rnd.uniform(-1, 1) for _ in range(N(dur))]

def env(x, a=0.005, d=0.05, s=0.7, r=0.05, hold=None):
    n = len(x); A, D, R = N(a), N(d), N(r)
    H = n - R if hold is None else N(hold)
    out = [0.0] * n
    for i in range(n):
        if i < A: g = i / max(1, A)
        elif i < A + D: g = 1 - (1 - s) * (i - A) / max(1, D)
        elif i < H: g = s
        else: g = s * max(0.0, 1 - (i - H) / max(1, R))
        out[i] = x[i] * g
    return out

def expdec(x, tau):
    return [v * math.exp(-i / SR / tau) for i, v in enumerate(x)]

def lp(x, cutoff):
    """one-pole low-pass; cutoff number or function(t)."""
    out = [0.0] * len(x); y = 0.0
    for i, v in enumerate(x):
        c = cutoff(i / SR) if callable(cutoff) else cutoff
        a = 1 - math.exp(-TAU * c / SR)
        y += a * (v - y); out[i] = y
    return out

def hp(x, cutoff):
    lo = lp(x, cutoff); return [a - b for a, b in zip(x, lo)]

def bp(x, lo_c, hi_c): return hp(lp(x, hi_c), lo_c)

def gain(x, g): return [v * g for v in x]

def mix(*tracks, offsets=None):
    offsets = offsets or [0] * len(tracks)
    n = max(N(o) + len(t) for t, o in zip(tracks, offsets))
    out = [0.0] * n
    for t, o in zip(tracks, offsets):
        s = N(o)
        for i, v in enumerate(t): out[s + i] += v
    return out

def cat(*parts):
    out = []
    for p in parts: out += p
    return out

def silence(d): return [0.0] * N(d)

def normalize(x, peak=0.89):
    m = max(1e-9, max(abs(v) for v in x)); return [v * peak / m for v in x]

def softclip(x, drive=1.2): return [math.tanh(v * drive) / math.tanh(drive) for v in x]

def fade(x, fin=0.003, fout=0.01):
    n = len(x); a, b = N(fin), N(fout)
    for i in range(min(a, n)): x[i] *= i / a
    for i in range(min(b, n)): x[n - 1 - i] *= i / b
    return x

def save(kind, name, x, desc, loop=False, peak=0.89, do_fade=True):
    x = normalize(x, peak)
    if do_fade and not loop: x = fade(x)
    p = os.path.join(OUT, kind, name + '.wav')
    w = wave.open(p, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(array.array('h', [int(max(-1, min(1, v)) * 32767) for v in x]).tobytes()); w.close()
    MAN[kind][name] = dict(file='assets/audio/%s/%s.wav' % (kind, name), seconds=round(len(x) / SR, 2), loop=loop, use=desc)
    print('%-6s %-20s %.2fs' % (kind, name, len(x) / SR))

# ------------------------------------------------------------------ SFX
def sweep(f0, f1, dur, curve=1.0):
    return lambda t: f0 + (f1 - f0) * (min(1, t / dur) ** curve)

def sfx():
    save('sfx', 'ui_hover', env(tone(1400, 0.04, 'sine'), 0.002, 0.03, 0, 0.005), 'Menu item hover', peak=0.4)
    save('sfx', 'ui_click', mix(env(tone(sweep(900, 1500, 0.05), 0.07, 'square', pw=0.3), 0.001, 0.06, 0, 0.01), gain(expdec(noise(0.02), 0.004), 0.3)), 'Menu click', peak=0.5)
    save('sfx', 'ui_confirm', cat(env(tone(midi(76), 0.08, 'square'), 0.002, 0.07, 0.2, 0.01), env(tone(midi(83), 0.16, 'square'), 0.002, 0.1, 0.3, 0.05)), 'Start level / confirm', peak=0.45)
    save('sfx', 'ui_back', cat(env(tone(midi(76), 0.07, 'square'), 0.002, 0.06, 0.2, 0.01), env(tone(midi(69), 0.12, 'square'), 0.002, 0.1, 0.3, 0.03)), 'Back / cancel', peak=0.45)
    save('sfx', 'ui_locked', mix(env(tone(140, 0.25, 'square'), 0.002, 0.2, 0.3, 0.05), env(tone(147, 0.25, 'square'), 0.002, 0.2, 0.3, 0.05)), 'Clicked a locked level', peak=0.5)

    # weapons
    thwip = mix(env(tone(sweep(1800, 350, 0.09, 0.5), 0.12, 'sine'), 0.001, 0.1, 0, 0.02),
                gain(env(bp(noise(0.08), 800, 5000), 0.001, 0.06, 0, 0.02), 0.6))
    save('sfx', 'dart_fire', thwip, 'Dart pistol shot (thwip!)')
    save('sfx', 'dart_hit', mix(expdec(tone(sweep(300, 120, 0.06), 0.15, 'sine'), 0.04),
                                gain(env(tone(lambda t: 520 + 120 * math.sin(TAU * 28 * t), 0.35, 'sine'), 0.005, 0.3, 0, 0.05), 0.35)), 'Dart sticks (thunk + boing)')
    save('sfx', 'net_fire', mix(expdec(tone(sweep(160, 60, 0.15), 0.25, 'sine'), 0.08), gain(env(lp(noise(0.35), sweep(3000, 400, 0.35)), 0.01, 0.3, 0, 0.05), 0.7)), 'Net launcher (whoomp)')
    save('sfx', 'net_hit', gain(env(bp(noise(0.4), 1500, 6000), 0.005, 0.1, 0.3, 0.2), 1), 'Net lands on something (rustle)')
    sq = [v * (0.6 + 0.4 * math.sin(TAU * 32 * i / SR)) for i, v in enumerate(bp(noise(0.25), 1200, 4000))]
    save('sfx', 'water_fire', env(sq, 0.005, 0.1, 0.5, 0.08), 'Water blaster squirt')
    save('sfx', 'water_splash', env(lp(noise(0.4), sweep(6000, 800, 0.4)), 0.002, 0.15, 0.2, 0.2), 'Water hits / balloon drips')
    save('sfx', 'pillow_fire', mix(expdec(tone(sweep(110, 45, 0.2), 0.3, 'sine'), 0.1), gain(env(lp(noise(0.3), 900), 0.005, 0.2, 0, 0.05), 1.2)), 'Pillow cannon (fwump)')
    save('sfx', 'pillow_hit', env(lp(noise(0.3), sweep(2500, 300, 0.3)), 0.002, 0.25, 0, 0.05), 'Pillow impact (poof)')
    save('sfx', 'empty_click', env(hp(noise(0.03), 2000), 0.001, 0.02, 0, 0.005), 'Out of ammo click', peak=0.5)
    save('sfx', 'reload', cat(env(hp(noise(0.04), 1500), 0.001, 0.03, 0, 0.005), silence(0.12), env(bp(noise(0.06), 600, 3000), 0.001, 0.05, 0, 0.01)), 'Reload / pump', peak=0.6)

    # movement
    for k in range(3):
        st = env(lp(noise(0.08), 900 + k * 250), 0.002, 0.05, 0, 0.02)
        save('sfx', 'footstep_%d' % (k + 1), mix(st, gain(expdec(tone(70 + k * 8, 0.08), 0.02), 0.5)), 'Footstep variant (randomise pitch 0.9-1.1)', peak=0.5)
    save('sfx', 'jump', env(tone(sweep(220, 640, 0.18, 0.7), 0.22, 'sine', vib=0.02, vib_rate=20), 0.005, 0.18, 0, 0.03), 'Jump (cartoon boing up)', peak=0.55)
    save('sfx', 'land', mix(expdec(tone(sweep(120, 50, 0.1), 0.18), 0.05), gain(env(lp(noise(0.12), 700), 0.001, 0.1, 0, 0.02), 0.8)), 'Land', peak=0.65)
    save('sfx', 'slide_whistle_up', env(tone(sweep(400, 1600, 0.5, 1.4), 0.55, 'sine', vib=0.01, vib_rate=7), 0.02, 0.3, 0.8, 0.05), 'Comedy rise (wall-run, big jump)', peak=0.5)
    save('sfx', 'slide_whistle_down', env(tone(sweep(1500, 300, 0.6, 0.8), 0.65, 'sine', vib=0.01, vib_rate=7), 0.02, 0.3, 0.8, 0.05), 'Comedy fall (fell off roof)', peak=0.5)
    save('sfx', 'tackle', cat(mix(expdec(tone(sweep(90, 40, 0.15), 0.3), 0.1), gain(env(lp(noise(0.25), 1200), 0.001, 0.2, 0, 0.05), 1.2)), silence(0.05),
                               env(tone(lambda t: 330 + 90 * math.sin(TAU * 18 * t), 0.4), 0.005, 0.35, 0, 0.05)), 'Tackle the groom (thud + boing)')
    save('sfx', 'whoosh', env(bp(noise(0.35), 300, 2500), 0.12, 0.15, 0.2, 0.1), 'Fast movement / swing')

    # creatures
    def honk(f0, dur):
        x = tone(lambda t: f0 * (1 + 0.25 * min(1, t / 0.05)) * (1 - 0.15 * t / dur), dur, 'saw', vib=0.03, vib_rate=30)
        x = mix(bp(x, 500, 1600), gain(bp(x, 2000, 3200), 0.6))
        return env(x, 0.01, 0.05, 0.85, 0.06)
    save('sfx', 'honk_1', honk(390, 0.32), 'Goose honk')
    save('sfx', 'honk_2', cat(honk(420, 0.18), silence(0.05), honk(440, 0.24)), 'Goose double honk (angry)')
    save('sfx', 'honk_charge', cat(*[honk(460 + i * 15, 0.12) + silence(0.03) for i in range(5)]), 'Goose charging (HONKHONKHONK)')
    meow = tone(lambda t: 520 + 380 * math.sin(math.pi * min(1, t / 0.55)), 0.6, 'saw', vib=0.015)
    save('sfx', 'meow', env(mix(bp(meow, 600, 1800), gain(bp(meow, 2200, 3500), 0.5)), 0.04, 0.1, 0.8, 0.15), 'Cat meow (it knocked something over)')
    save('sfx', 'cat_knock', cat(env(bp(noise(0.05), 2000, 6000), 0.001, 0.04, 0, 0.01), silence(0.25),
                                 mix(env(tone(1700, 0.5), 0.001, 0.4, 0, 0.1), gain(env(tone(2300, 0.4), 0.001, 0.3, 0, 0.1), 0.6), gain(expdec(noise(0.3), 0.05), 0.5))), 'Something falls & shatters (alerts grandma)')
    save('sfx', 'balloon_squeak', env(tone(lambda t: 900 + 400 * math.sin(TAU * 6 * t) + 200 * math.sin(TAU * 31 * t), 0.4, 'tri'), 0.01, 0.1, 0.7, 0.1), 'Balloon animal squeak / bite', peak=0.5)
    save('sfx', 'balloon_pop', mix(expdec(noise(0.25), 0.02), gain(expdec(tone(sweep(400, 80, 0.05), 0.1), 0.02), 0.6)), 'Balloon pop')

    # bosses & objects
    bell = lambda f, d: expdec(mix(tone(f, d), gain(tone(f * 2.76, d), 0.4), gain(tone(f * 5.4, d), 0.2)), 0.25)
    ring = []
    for i in range(12):
        ring += mix(bell(1650 if i % 2 else 1520, 0.083), gain(expdec(hp(noise(0.01), 3000), 0.002), 0.6))
    save('sfx', 'alarm_ring', ring, 'Alarm clock boss ringing (loopable ~1s)', loop=True)
    save('sfx', 'snooze_bonk', mix(expdec(tone(sweep(220, 55, 0.25), 0.6, 'sine'), 0.2), gain(expdec(tone(sweep(880, 300, 0.2), 0.4, 'tri'), 0.1), 0.4),
                                   gain(expdec(lp(noise(0.2), 2000), 0.04), 0.6)), 'Hit the snooze button (BONK)')
    save('sfx', 'boss_hurt', mix(env(tone(sweep(300, 150, 0.3), 0.35, 'square', vib=0.08, vib_rate=25), 0.005, 0.3, 0, 0.05)), 'Boss damaged', peak=0.6)
    expl = mix(expdec(lp(noise(1.5), sweep(4000, 200, 1.2)), 0.35), gain(expdec(tone(sweep(90, 30, 1.0), 1.2), 0.4), 1.2))
    save('sfx', 'boss_defeat', cat(expl, bell(1046, 0.6), bell(1318, 0.6), bell(1568, 1.2)), 'Boss defeated (kaboom + bells)')
    save('sfx', 'router_beep', cat(env(tone(1760, 0.08, 'square'), 0.001, 0.07, 0.4, 0.01), silence(0.08), env(tone(1760, 0.08, 'square'), 0.001, 0.07, 0.4, 0.01)), 'Router beep', peak=0.35)
    save('sfx', 'power_down', env(tone(sweep(800, 60, 0.7, 0.5), 0.75, 'square'), 0.002, 0.7, 0.3, 0.05), 'Unplug (power down)', peak=0.45)
    save('sfx', 'power_up', env(tone(sweep(80, 1200, 0.6, 1.5), 0.65, 'square'), 0.002, 0.6, 0.5, 0.05), 'Plug back in (power up)', peak=0.45)
    save('sfx', 'slurp', env([v * (0.4 + 0.6 * abs(math.sin(TAU * 7 * i / SR))) for i, v in enumerate(bp(noise(0.9), 400, 2500))], 0.05, 0.3, 0.7, 0.2), 'Forced to eat soup (slurp)')
    save('sfx', 'gulp', mix(expdec(tone(sweep(300, 120, 0.12), 0.2), 0.06), gain(expdec(tone(sweep(200, 500, 0.08), 0.12), 0.04), 0.5)), 'Gulp')
    save('sfx', 'munch', cat(*[env(bp(noise(0.07), 1000, 5000), 0.001, 0.05, 0, 0.01) + silence(0.09) for _ in range(4)]), 'Balloon animals eating the cake')
    save('sfx', 'snore', cat(*[env(lp(noise(1.0), 400), 0.4, 0.4, 0.6, 0.2) + env(tone(sweep(900, 1300, 0.6), 0.8, 'sine'), 0.2, 0.3, 0.3, 0.2) for _ in range(1)]), 'Tranquillised NPC snoring (loopable)', loop=True)

    # feedback / stingers
    save('sfx', 'clue_found', cat(*[env(mix(tone(midi(n), 0.11, 'sine'), gain(tone(midi(n) * 2, 0.11, 'sine'), 0.3)), 0.002, 0.1, 0.3, 0.02) for n in (84, 88, 91)],
                                  env(tone(midi(96), 0.35), 0.002, 0.3, 0.2, 0.05)), 'New dossier clue unlocked')
    save('sfx', 'wrong_target', cat(env(tone(110, 0.22, 'square'), 0.002, 0.05, 0.9, 0.02), silence(0.06), env(tone(104, 0.4, 'square'), 0.002, 0.05, 0.9, 0.05)), 'Darted the wrong Gary (buzzer)', peak=0.55)
    save('sfx', 'spotted', mix(env(tone(sweep(400, 1200, 0.15), 0.4, 'saw'), 0.005, 0.1, 0.6, 0.2), gain(env(tone(sweep(600, 1800, 0.15), 0.4, 'saw'), 0.005, 0.1, 0.6, 0.2), 0.5)), 'You were spotted! (!)', peak=0.5)
    save('sfx', 'crowd_gasp', env(bp(noise(1.0), 400, 2200), 0.15, 0.2, 0.5, 0.5), 'Office gasps')
    save('sfx', 'pickup', cat(env(tone(midi(88), 0.07, 'square'), 0.001, 0.06, 0.3, 0.01), env(tone(midi(95), 0.18, 'square'), 0.001, 0.15, 0.3, 0.03)), 'Pickup collected', peak=0.4)
    save('sfx', 'confetti', mix(expdec(noise(0.08), 0.01), *[gain(expdec(tone(rnd.uniform(2000, 5000), 0.3), 0.08), 0.15) for _ in range(8)]), 'Confetti pop', peak=0.6)
    save('sfx', 'timer_tick', env(tone(2400, 0.03, 'square'), 0.001, 0.02, 0, 0.005), 'Countdown tick', peak=0.3)
    # sad trombone (original voicing)
    trom = []
    for n, d in ((58, 0.45), (57, 0.45), (56, 0.45), (55, 1.4)):
        x = tone(midi(n), d, 'saw', vib=0.012 if d > 1 else 0.004, vib_rate=5)
        trom += env(lp(x, lambda t: 600 + 900 * math.sin(math.pi * min(1, t / 0.3))), 0.03, 0.1, 0.8, 0.1)
    save('sfx', 'mission_failed', trom, 'Mission failed stinger (wah wah wah waaah)')
    fan = []
    for n, d in ((67, 0.12), (72, 0.12), (76, 0.12), (79, 0.3), (76, 0.12), (79, 0.7)):
        fan += env(mix(tone(midi(n), d, 'square', pw=0.3), gain(tone(midi(n - 12), d, 'saw'), 0.4)), 0.004, 0.05, 0.7, 0.04)
    chord = mix(*[env(tone(midi(n), 0.9, 'saw'), 0.01, 0.2, 0.6, 0.4) for n in (60, 64, 67, 72)])
    save('sfx', 'mission_complete', mix(fan, lp(chord, 2500), offsets=[0, 0.78]), 'Mission complete fanfare')
    # Gary's hum (THE tell) - original little tune, hummed
    hum = []
    for n, d in ((62, 0.3), (64, 0.3), (66, 0.6), (64, 0.3), (62, 0.3), (59, 0.9), (61, 0.3), (62, 0.3), (64, 0.6), (62, 1.0)):
        x = tone(midi(n), d, 'tri', vib=0.01, vib_rate=5.5)
        hum += env(lp(x, 900), 0.04, 0.05, 0.85, 0.06)
    save('sfx', 'gary_hum', cat(hum, silence(0.6)), 'The REAL Gary hums this (positional audio, loop). Decoys never hum.', loop=True)


# ------------------------------------------------------------------ instruments
def inst(name, f, d, v=1.0):
    if name == 'bass':
        x = expdec(tone(f, d + 0.05, 'tri'), 0.35); x = mix(x, gain(expdec(tone(f * 2, d + 0.05, 'sine'), 0.1), 0.3))
        return env(x, 0.004, 0.05, 0.9, 0.04, hold=d)
    if name == 'vibe':
        x = mix(tone(f, d + 0.4, 'sine'), gain(tone(f * 4, d + 0.4, 'sine'), 0.25))
        x = [s * (1 + 0.25 * math.sin(TAU * 5 * i / SR)) for i, s in enumerate(x)]
        return expdec(env(x, 0.002, 0.05, 0.9, 0.3, hold=d + 0.1), 0.45)
    if name == 'pizz':
        return expdec(mix(tone(f, 0.25, 'tri'), gain(tone(f * 2, 0.25), 0.4)), 0.06)
    if name == 'brass':
        x = tone(f, d, 'saw', vib=0.006)
        return env(lp(x, lambda t: 500 + 2200 * min(1, t / 0.06) * math.exp(-t * 3)), 0.02, 0.08, 0.7, 0.06)
    if name == 'stab':
        return env(lp(tone(f, d, 'saw'), 1800), 0.004, 0.05, 0.4, 0.05)
    if name == 'lead':
        return env(lp(tone(f, d, 'square', vib=0.004, pw=0.25), 3500), 0.005, 0.05, 0.7, 0.04)
    if name == 'chip':
        return env(tone(f, d, 'square', pw=0.5), 0.002, 0.03, 0.6, 0.02)
    if name == 'tuba':
        return env(lp(tone(f, d, 'saw'), 420), 0.02, 0.05, 0.8, 0.05)
    if name == 'box':
        return expdec(mix(tone(f, d + 0.6, 'sine'), gain(tone(f * 3.01, d + 0.6), 0.25), gain(tone(f * 5.2, d + 0.6), 0.08)), 0.35)
    if name == 'clar':
        return env(lp(tone(f, d, 'square', vib=0.006, pw=0.5), 1400), 0.03, 0.05, 0.8, 0.05)
    if name == 'arp':
        return env(lp(tone(f, d, 'saw'), 2600), 0.002, 0.04, 0.3, 0.02)
    raise KeyError(name)

def drum(name):
    if name == 'kick': return mix(expdec(tone(sweep(130, 42, 0.08), 0.3), 0.09), gain(expdec(lp(noise(0.02), 3000), 0.005), 0.4))
    if name == 'snare': return mix(gain(expdec(hp(noise(0.2), 1200), 0.05), 0.8), gain(expdec(tone(190, 0.12), 0.04), 0.5))
    if name == 'brush': return gain(env(hp(noise(0.18), 2500), 0.03, 0.05, 0.4, 0.08), 0.35)
    if name == 'hat': return gain(expdec(hp(noise(0.05), 6000), 0.012), 0.45)
    if name == 'ride': return gain(mix(expdec(hp(noise(0.3), 5000), 0.08), gain(expdec(tone(4200, 0.3), 0.1), 0.15)), 0.35)
    if name == 'clap': return gain(cat(expdec(bp(noise(0.012), 900, 4000), 0.004), expdec(bp(noise(0.012), 900, 4000), 0.004), expdec(bp(noise(0.12), 900, 4000), 0.03)), 0.7)
    if name == 'bell': return expdec(mix(tone(1650, 0.4), gain(tone(1650 * 2.76, 0.4), 0.3)), 0.12)
    raise KeyError(name)

def song(name, bpm, beats, parts, desc, swing=0.0):
    """parts: list of (instrument, volume, [(beat, len_beats, midi_or_drum)])."""
    spb = 60.0 / bpm; total = N(beats * spb)
    buf = [0.0] * (total + N(2.0))
    for ins, vol, notes in parts:
        for b, L, n in notes:
            if swing and abs((b * 2) % 2 - 1) < 1e-6: b += swing * 0.5
            x = drum(n) if isinstance(n, str) else inst(ins, midi(n), L * spb)
            s = N(b * spb)
            for i, v in enumerate(x):
                buf[(s + i) % total if s + i >= total else s + i] += v * vol
    out = softclip(buf[:total], 1.1)
    save('music', name, out, desc, loop=True, peak=0.8)

def seq(start, pattern, step=1.0, length=None):
    """pattern of midi numbers / None (rest) / drum names, evenly spaced."""
    return [(start + i * step, length or step * 0.9, n) for i, n in enumerate(pattern) if n is not None]


def music():
    # ---- MENU: sly spy-jazz, A minor, 110bpm, 8 bars
    walk = [45, 48, 52, 55, 45, 52, 50, 48, 50, 53, 57, 55, 50, 57, 53, 52, 52, 56, 59, 62, 52, 50, 48, 47, 45, 48, 52, 55, 52, 56, 59, 56]
    mel = [(0.5, .5, 76), (1, .5, 79), (1.5, 1, 81), (3, .5, 80), (3.5, .5, 81), (4, 1.5, 76), (6, .5, 74), (6.5, .5, 72), (7, 1, 69),
           (8.5, .5, 74), (9, .5, 77), (9.5, 1, 81), (11, .5, 79), (11.5, .5, 77), (12, 1.5, 74), (14, .5, 72), (14.5, .5, 74), (15, 1, 77),
           (16.5, .5, 80), (17, .5, 83), (17.5, 1, 86), (19, .5, 84), (19.5, .5, 83), (20, 1, 80), (21, 1, 76), (22, .5, 74), (22.5, .5, 76), (23, 1, 80),
           (24.5, .5, 81), (25, .5, 84), (25.5, 1, 88), (27, 1, 84), (28, 1.5, 81), (30, .5, 80), (30.5, .5, 76), (31, 1, 71)]
    chords = {0: (57, 60, 64), 8: (57, 62, 65), 16: (56, 59, 62), 24: (57, 60, 64)}
    stabs = []
    for bar in range(8):
        c = chords[(bar // 2) * 8]
        for n in c: stabs.append((bar * 4 + 2.5, 0.3, n))
    ride = [(b * 0.5 + (0.17 if b % 2 else 0), 0.2, 'ride') for b in range(64) if b % 4 != 1]
    song('music_menu', 110, 32, [('bass', 0.9, seq(0, walk, 1, 0.9)), ('vibe', 0.55, mel), ('stab', 0.18, stabs),
                                 ('d', 1, ride), ('d', 1, [(b + 1, .5, 'brush') for b in range(0, 32, 2)])], 'Main menu / level select (spy jazz)')

    # ---- OFFICE: tip-toe pizzicato, D minor, 104bpm
    bassp = []
    for bar in range(8):
        root = [50, 50, 46, 45, 50, 50, 46, 45][bar]
        bassp += seq(bar * 4, [root - 12, None, root - 5, None, root - 12, None, root - 5, root - 6], 0.5, 0.2)
    melo = [(0, .5, 62), (0.5, .5, 64), (1, .5, 65), (2, .5, 68), (2.5, 1, 69), (4, .5, 70), (4.5, .5, 69), (5, .5, 68), (5.5, 1.5, 69),
            (8, .5, 62), (8.5, .5, 64), (9, .5, 65), (10, .5, 68), (10.5, 1, 69), (12, .5, 74), (12.5, .5, 73), (13, .5, 72), (13.5, .5, 71), (14, 2, 70),
            (16, .5, 62), (16.5, .5, 64), (17, .5, 65), (18, .5, 68), (18.5, 1, 69), (20, .5, 70), (20.5, .5, 69), (21, .5, 68), (21.5, 1.5, 69),
            (24, .5, 65), (24.5, .5, 64), (25, .5, 62), (25.5, .5, 61), (26, 2, 62), (29, .5, 57), (29.5, .5, 61), (30, 2, 62)]
    song('music_office', 104, 32, [('pizz', 0.9, bassp), ('clar', 0.32, melo), ('d', 1, [(b * 0.5, .2, 'hat') for b in range(64) if b % 2 == 1]),
                                   ('d', 1, [(b, .2, 'brush') for b in range(1, 32, 2)])], 'L1 Office: sneaky tip-toe')

    # ---- CHASE: driving, E minor, 156bpm, 8 bars
    roots = [40, 40, 36, 38, 40, 40, 36, 35]
    bassc = []
    for bar, r in enumerate(roots): bassc += seq(bar * 4, [r, r, r + 12, r, r, r + 12, r, r + 10], 0.5, 0.4)
    riff = [76, 79, 81, 83, 86, 83, 81, 79, 76, 79, 81, 83, 81, 79, 76, None]
    lead = seq(0, riff, 0.5, 0.42) + seq(8, [72, 76, 79, 81, 84, 81, 79, 76, 74, 78, 81, 83, 81, 78, 74, None], 0.5, 0.42) + \
        seq(16, riff, 0.5, 0.42) + seq(24, [72, 76, 79, 76, 71, 74, 78, 74, 76, None, 76, None, 83, 81, 79, 78], 0.5, 0.42)
    drums = [(b, .2, 'kick') for b in range(32)] + [(b, .2, 'snare') for b in range(1, 32, 2)] + [(b * 0.5, .1, 'hat') for b in range(64)]
    song('music_chase', 156, 32, [('bass', 0.8, bassc), ('lead', 0.3, lead), ('d', 1, drums)], 'L2 Rooftop chase: fast & frantic')

    # ---- PARK: goofy oom-pah, F major, 120bpm
    ch = [(41, (57, 60, 65)), (36, (55, 60, 64)), (41, (57, 60, 65)), (36, (55, 58, 64)), (46, (58, 62, 65)), (41, (57, 60, 65)), (36, (55, 58, 64)), (41, (57, 60, 65))]
    tuba, pah = [], []
    for bar, (r, c) in enumerate(ch):
        tuba += [(bar * 4, .8, r), (bar * 4 + 2, .8, r - 5)]
        for b in (1, 3):
            for n in c: pah.append((bar * 4 + b, 0.35, n))
    melp = seq(0, [72, None, 74, 76, 77, None, 76, 74, 72, None, 67, None, 69, 70, 72, None], 0.5, 0.4) + \
        seq(8, [70, None, 69, 67, 65, None, 67, 69, 70, 72, 74, 72, 70, None, 67, None], 0.5, 0.4) + \
        seq(16, [72, None, 74, 76, 77, None, 79, 81, 82, None, 81, 79, 77, None, 74, None], 0.5, 0.4) + \
        seq(24, [72, 70, 69, 67, 65, None, 72, None, 65, None, None, None, 60, 65, None, None], 0.5, 0.4)
    song('music_park', 120, 32, [('tuba', 0.9, tuba), ('stab', 0.12, pah), ('clar', 0.3, melp), ('d', 1, [(b, .2, 'hat') for b in range(1, 32, 2)])],
         'L3 Goose park: goofy oom-pah')

    # ---- GRANDMA: music-box waltz 3/4, C major, 96bpm, 12 bars (36 beats)
    prog = [(48, (64, 67)), (43, (62, 65)), (48, (64, 67)), (45, (64, 69)), (41, (65, 69)), (43, (62, 67)), (48, (64, 67)), (43, (62, 65)),
            (48, (64, 67)), (45, (64, 69)), (43, (62, 65)), (48, (64, 67))]
    wb, wc = [], []
    for bar, (r, c) in enumerate(prog):
        wb.append((bar * 3, 0.9, r))
        for b in (1, 2):
            for n in c: wc.append((bar * 3 + b, 0.5, n))
    wm = [(0, 2, 76), (2, 1, 79), (3, 2, 77), (5, 1, 74), (6, 2, 76), (8, 1, 72), (9, 3, 72), (12, 2, 77), (14, 1, 81), (15, 2, 79), (17, 1, 77),
          (18, 1, 76), (19, 1, 77), (20, 1, 79), (21, 3, 74), (24, 2, 76), (26, 1, 79), (27, 2, 81), (29, 1, 77), (30, 1, 74), (31, 1, 76), (32, 1, 74), (33, 3, 72)]
    song('music_grandma', 96, 36, [('bass', 0.6, wb), ('box', 0.18, wc), ('box', 0.5, wm)], 'L4 Grandma house: music-box waltz (creepy-cosy)')

    # ---- PARTY: chip polka, G major, 144bpm
    pr = [(43, (59, 62, 67)), (38, (57, 62, 66)), (43, (59, 62, 67)), (38, (57, 60, 66)), (36, (60, 64, 67)), (43, (59, 62, 67)), (38, (57, 62, 66)), (43, (59, 62, 67))]
    pb, pc = [], []
    for bar, (r, c) in enumerate(pr):
        pb += [(bar * 4, .4, r), (bar * 4 + 1, .4, r + 7), (bar * 4 + 2, .4, r), (bar * 4 + 3, .4, r + 7)]
        for b in (0.5, 1.5, 2.5, 3.5):
            for n in c: pc.append((bar * 4 + b, 0.2, n))
    pm = seq(0, [79, 78, 79, 83, 81, 79, 78, 76, 74, None, 74, 76, 78, 79, 81, None], 0.5, 0.4) + \
        seq(8, [83, 81, 79, 78, 76, 74, 72, 71, 69, None, 72, 71, 69, 67, 66, None], 0.5, 0.4) + \
        seq(16, [79, 78, 79, 83, 81, 79, 78, 76, 84, None, 84, 83, 81, 79, 78, None], 0.5, 0.4) + \
        seq(24, [76, 78, 79, 81, 83, 81, 79, 78, 79, None, 74, None, 79, None, None, None], 0.5, 0.4)
    song('music_party', 144, 32, [('bass', 0.8, pb), ('chip', 0.1, pc), ('chip', 0.28, pm),
                                  ('d', 1, [(b, .2, 'kick') for b in range(0, 32, 2)] + [(b, .2, 'clap') for b in range(1, 32, 2)])], 'L5 Birthday party defence: chiptune polka')

    # ---- BOSS: urgent, C minor, 140bpm
    arps, bb = [], []
    prog = [(36, (60, 63, 67, 72)), (32, (56, 60, 63, 68)), (34, (58, 62, 65, 70)), (31, (55, 59, 62, 67))] * 2
    for bar, (r, c) in enumerate(prog):
        arps += seq(bar * 4, list(c) * 4, 0.25, 0.22)
        bb += seq(bar * 4, [r, r, r + 12, r, r, r + 12, r, r + 12], 0.5, 0.4)
    stabm = seq(0, [72, None, None, 75, None, None, 74, None], 0.5, 0.4) + seq(16, [72, None, None, 75, None, None, 79, 77], 0.5, 0.4)
    drums = [(b, .2, 'kick') for b in range(32)] + [(b, .2, 'snare') for b in range(1, 32, 2)] + [(b * 0.5 + 0.5, .1, 'hat') for b in range(0, 64, 2)] + \
        [(b * 4, .2, 'bell') for b in range(8)]
    song('music_boss', 140, 32, [('arp', 0.16, arps), ('bass', 0.85, bb), ('brass', 0.3, stabm), ('d', 1, drums)], 'L6 Alarm clock boss fight')


if __name__ == '__main__':
    sfx(); music()
    with open(os.path.join(OUT, '_manifest_audio.json'), 'w') as f: json.dump(MAN, f, indent=1)
