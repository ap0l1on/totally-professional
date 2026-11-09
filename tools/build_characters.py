"""Skinned, animated characters & creatures -> public/assets/models/characters/*.glb"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from gltf_builder import Model, box, rbox, sphere, cylinder, cone, capsule, lathe, torus, tube
from anim import posed, osc, S, C, pos

OUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'assets', 'models', 'characters')
os.makedirs(OUT, exist_ok=True)
MANIFEST = {}

# =====================================================================  HUMANOID
def humanoid(name, height=1.0, width=1.0, belly=0.0, skin='#e8b48a', hair='#3b2a20',
             shirt='#f4f4f0', pants='#c9b48a', shoes='#5a3a22', sleeves='short',
             lower='pants', head_scale=1.0):
    m = Model(name, tint_groups=('skin', 'hair', 'shirt', 'pants'))
    H, W = height, width
    hipsY = 0.95 * H
    B = {
        'hips': (None, (0, hipsY, 0)),
        'spine': ('hips', (0, 1.07 * H, 0)),
        'chest': ('spine', (0, 1.27 * H, 0)),
        'neck': ('chest', (0, 1.47 * H, 0)),
        'head': ('neck', (0, 1.53 * H, 0)),
    }
    for sd, sx in (('L', 1), ('R', -1)):
        B['upperarm_' + sd] = ('chest', (sx * 0.215 * W, 1.43 * H, 0))
        B['forearm_' + sd] = ('upperarm_' + sd, (sx * 0.225 * W, 1.15 * H, 0))
        B['hand_' + sd] = ('forearm_' + sd, (sx * 0.23 * W, 0.90 * H, 0))
        B['thigh_' + sd] = ('hips', (sx * 0.1 * W, 0.90 * H, 0))
        B['shin_' + sd] = ('thigh_' + sd, (sx * 0.1 * W, 0.49 * H, 0))
        B['foot_' + sd] = ('shin_' + sd, (sx * 0.1 * W, 0.085 * H, 0))
    for b in ['hips', 'spine', 'chest', 'neck', 'head',
              'upperarm_L', 'forearm_L', 'hand_L', 'upperarm_R', 'forearm_R', 'hand_R',
              'thigh_L', 'shin_L', 'foot_L', 'thigh_R', 'shin_R', 'foot_R']:
        m.bone(b, *B[b])

    # torso
    m.add(rbox(0.36 * W + belly * 0.5, 0.2 * H, 0.23 + belly * 0.5, 0.06), pants, t=(0, 0.9 * H, 0), group='pants', bone='hips')
    m.add(rbox(0.36 * W + belly, 0.26 * H, 0.23 + belly, 0.08), shirt, t=(0, 1.09 * H, belly * 0.25), group='shirt', bone='spine')
    m.add(rbox(0.42 * W, 0.3 * H, 0.25, 0.08), shirt, t=(0, 1.31 * H, 0), group='shirt', bone='chest')
    m.add(cylinder(0.055, 0.06, 0.12, 12), skin, t=(0, 1.49 * H, 0), group='skin', bone='neck')
    # head
    hs = head_scale; hy = 1.67 * H
    m.add(rbox(0.25 * hs, 0.29 * hs, 0.26 * hs, 0.1), skin, t=(0, hy, 0.01), group='skin', bone='head')
    m.add(rbox(0.07, 0.06, 0.07, 0.025), skin, t=(0, hy - 0.01, 0.15 * hs), group='skin', bone='head')      # nose
    for sx in (1, -1):
        m.add(sphere(0.04, 10, 6), skin, t=(sx * 0.13 * hs, hy, 0), s=(0.45, 1, 0.8), group='skin', bone='head')   # ears
        m.add(sphere(0.026, 10, 6), '#ffffff', mat='gloss', t=(sx * 0.055, hy + 0.035, 0.128 * hs), s=(1, 1.15, 0.6), group='body', bone='head')
        m.add(sphere(0.015, 8, 6), '#1a1a22', mat='gloss', t=(sx * 0.055, hy + 0.033, 0.142 * hs), s=(1, 1, 0.6), group='body', bone='head')
        m.add(rbox(0.06, 0.014, 0.02, 0.006), hair, t=(sx * 0.058, hy + 0.08, 0.132 * hs), r=(0, 0, -sx * 6), group='hair', bone='head')  # brows
    m.add(rbox(0.07, 0.012, 0.02, 0.005), '#7a3b30', t=(0, hy - 0.075, 0.133 * hs), group='body', bone='head')  # mouth

    # arms
    for sd, sx in (('L', 1), ('R', -1)):
        x = sx * 0.225 * W
        upper_col = shirt if sleeves in ('short', 'long') else skin
        upper_grp = 'shirt' if sleeves in ('short', 'long') else 'skin'
        if sleeves == 'short':
            m.add(capsule(0.062, 0.08, 12), shirt, t=(x, 1.37 * H, 0), group='shirt', bone='upperarm_' + sd)
            m.add(capsule(0.052, 0.14, 12), skin, t=(x, 1.26 * H, 0), group='skin', bone='upperarm_' + sd)
        else:
            m.add(capsule(0.06, 0.2, 10), upper_col, t=(x, 1.29 * H, 0), group=upper_grp, bone='upperarm_' + sd)
        fore_col = shirt if sleeves == 'long' else skin
        fore_grp = 'shirt' if sleeves == 'long' else 'skin'
        m.add(capsule(0.05, 0.17, 10), fore_col, t=(sx * 0.228 * W, 1.03 * H, 0), group=fore_grp, bone='forearm_' + sd)
        m.add(sphere(0.055, 12, 8), skin, t=(sx * 0.232 * W, 0.865 * H, 0.005), s=(0.8, 1.2, 0.9), group='skin', bone='hand_' + sd)
        m.add(sphere(0.022, 8, 6), skin, t=(sx * 0.232 * W, 0.885 * H, 0.05), s=(1, 1.4, 1), group='skin', bone='hand_' + sd)  # thumb
        m.marker('socket_hand_' + sd, (sx * 0.232 * W, 0.84 * H, 0.03), bone='hand_' + sd)
        # legs
        lx = sx * 0.1 * W
        if lower == 'pants':
            m.add(capsule(0.08, 0.28, 10), pants, t=(lx, 0.7 * H, 0), group='pants', bone='thigh_' + sd)
            m.add(capsule(0.068, 0.3, 10), pants, t=(lx, 0.29 * H, 0), group='pants', bone='shin_' + sd)
        else:  # stockings under skirt / dress
            m.add(capsule(0.07, 0.28, 12), skin, t=(lx, 0.7 * H, 0), group='skin', bone='thigh_' + sd)
            m.add(capsule(0.058, 0.3, 12), skin, t=(lx, 0.29 * H, 0), group='skin', bone='shin_' + sd)
        m.add(rbox(0.12, 0.09, 0.26, 0.04), shoes, mat='satin', t=(lx, 0.045, 0.04), group='body', bone='foot_' + sd)

    m.marker('socket_head_top', (0, hy + 0.15, 0), bone='head')
    m.marker('socket_chest', (0, 1.3 * H, 0.14), bone='chest')
    m.marker('socket_back', (0, 1.3 * H, -0.14), bone='chest')
    m.notes['hipsY'] = round(hipsY, 3)
    human_clips(m, hipsY)
    return m


def human_clips(m, hipsY):
    def walk(p):
        return {'thigh_L': (25 * S(p), 0, 0), 'thigh_R': (-25 * S(p), 0, 0),
                'shin_L': (5 + 40 * pos(-C(p)), 0, 0), 'shin_R': (5 + 40 * pos(C(p)), 0, 0),
                'foot_L': (-10 * pos(-C(p)), 0, 0), 'foot_R': (-10 * pos(C(p)), 0, 0),
                'upperarm_L': (-22 * S(p), 0, 6), 'upperarm_R': (22 * S(p), 0, -6),
                'forearm_L': (-18, 0, 0), 'forearm_R': (-18, 0, 0),
                'hips': (0, 6 * S(p), 0), 'chest': (3, -9 * S(p), 0), 'head': (0, 3 * S(p), 0),
                'hips@pos': (0, 0.022 * C(p, 2), 0)}
    m.clip('Walk', 1.0, osc(1.0, 12, walk))

    def run(p, look=False, panic=False):
        d = {'thigh_L': (48 * S(p), 0, 0), 'thigh_R': (-48 * S(p), 0, 0),
             'shin_L': (20 + 75 * pos(-C(p)), 0, 0), 'shin_R': (20 + 75 * pos(C(p)), 0, 0),
             'upperarm_L': (-55 * S(p), 0, 10), 'upperarm_R': (55 * S(p), 0, -10),
             'forearm_L': (-85, 0, 0), 'forearm_R': (-85, 0, 0),
             'spine': (6, 0, 0), 'chest': (8, -12 * S(p), 0), 'hips': (0, 8 * S(p), 0),
             'hips@pos': (0, -0.03 + 0.045 * C(p, 2), 0)}
        if look:
            d['chest'] = (0, 35, 0); d['head'] = (-5, 75, 0)
        if panic:
            d['upperarm_L'] = (25 * S(p, 2), 0, 155 + 18 * S(p, 2))
            d['upperarm_R'] = (-25 * S(p, 2), 0, -155 - 18 * S(p, 2, 0.5))
            d['forearm_L'] = (-30 + 30 * S(p, 2), 0, 0); d['forearm_R'] = (-30 + 30 * S(p, 2, 0.5), 0, 0)
            d['head'] = (-10, 30 * S(p, 2), 0); d['chest'] = (-6, 0, 0)
        return d
    m.clip('Run', 0.6, osc(0.6, 12, run))
    m.clip('RunLookBack', 0.6, osc(0.6, 12, lambda p: run(p, look=True)))
    m.clip('Panic', 0.5, osc(0.5, 12, lambda p: run(p, panic=True)))

    def idle(p):
        return {'chest': (1.5 * S(p), 0, 0), 'head': (2 * S(p, 1, 0.3), 10 * S(p), 0),
                'upperarm_L': (0, 0, 5 + 1.5 * S(p)), 'upperarm_R': (0, 0, -5 - 1.5 * S(p)),
                'forearm_L': (-8, 0, 0), 'forearm_R': (-8, 0, 0),
                'hips@pos': (0, -0.004 * S(p, 2), 0)}
    m.clip('Idle', 4.0, osc(4.0, 16, idle))

    def hum(p):  # the real target sways to the music in his head
        return {'chest': (0, 0, 6 * S(p, 2)), 'head': (0, 12 * S(p), 14 * S(p, 2)),
                'hips': (0, 0, -4 * S(p, 2)),
                'upperarm_L': (-8 * S(p, 2), 0, 8), 'upperarm_R': (8 * S(p, 2), 0, -8),
                'forearm_L': (-25, 0, 0), 'forearm_R': (-25, 0, 0),
                'hips@pos': (0, -0.015 * pos(S(p, 4)), 0)}
    m.clip('Hum', 2.0, osc(2.0, 24, hum))

    def talk(p):
        return {'upperarm_L': (-20 - 10 * S(p, 2), 0, 12), 'upperarm_R': (-15 - 12 * S(p, 2, 0.4), 0, -12),
                'forearm_L': (-70 + 25 * S(p, 3), 20, 0), 'forearm_R': (-65 + 25 * S(p, 3, 0.3), -20, 0),
                'head': (6 * S(p, 4), 8 * S(p), 0), 'chest': (0, 5 * S(p), 0)}
    m.clip('Talk', 2.4, osc(2.4, 24, talk))

    lie = -(hipsY - 0.13)
    m.clip('Fall', 1.0, posed([
        (0.0, {}),
        (0.2, {'hips': (-12, 0, 4), 'spine': (-8, 0, 0), 'head': (-20, 0, 0), 'upperarm_L': (-40, 0, 40), 'upperarm_R': (-40, 0, -40),
               'shin_L': (30, 0, 0), 'shin_R': (25, 0, 0), 'hips@pos': (0, -0.05, 0)}),
        (0.55, {'hips': (80, 0, 0), 'upperarm_L': (-150, 0, 30), 'upperarm_R': (-150, 0, -30), 'head': (10, 0, 0),
                'hips@pos': (0, lie + 0.08, 0.1)}),
        (0.7, {'hips': (92, 0, 0), 'upperarm_L': (-170, 0, 20), 'upperarm_R': (-170, 0, -20), 'head': (-25, 0, 0),
               'thigh_L': (-15, 0, 0), 'thigh_R': (-15, 0, 0), 'hips@pos': (0, lie + 0.06, 0.12)}),
        (1.0, {'hips': (90, 0, 0), 'upperarm_L': (-175, 0, 15), 'upperarm_R': (-175, 0, -15), 'head': (-5, 25, 0),
               'shin_L': (20, 0, 0), 'hips@pos': (0, lie, 0.12)}),
    ]), loop=False)

    def sleep(p):
        return {'hips': (90, 0, 0), 'spine': (1.5 * S(p), 0, 0), 'chest': (1.5 * S(p), 0, 0),
                'upperarm_L': (-175, 0, 15), 'upperarm_R': (-175, 0, -15), 'head': (-5, 25, 0),
                'shin_L': (20, 0, 0), 'shin_R': (0, 0, 0), 'hips@pos': (0, lie + 0.006 * S(p), 0.12)}
    m.clip('Sleep', 3.0, osc(3.0, 12, sleep))

    m.clip('Wave', 1.2, osc(1.2, 12, lambda p: {
        'upperarm_R': (-10, 0, -150), 'forearm_R': (0, 0, -20 + 30 * S(p, 2)), 'head': (0, -10, -8),
        'upperarm_L': (0, 0, 6), 'chest': (0, 0, 4)}))

    m.clip('Celebrate', 0.8, osc(0.8, 16, lambda p: {
        'upperarm_L': (0, 0, 150 + 15 * S(p, 2)), 'upperarm_R': (0, 0, -150 - 15 * S(p, 2)),
        'forearm_L': (0, 0, 10), 'forearm_R': (0, 0, -10),
        'thigh_L': (-30 * pos(S(p)), 0, 0), 'thigh_R': (-30 * pos(S(p)), 0, 0),
        'shin_L': (50 * pos(S(p)), 0, 0), 'shin_R': (50 * pos(S(p)), 0, 0),
        'head': (-15, 0, 0), 'hips@pos': (0, 0.22 * pos(S(p)), 0)}))

    m.clip('Jump', 0.7, posed([
        (0.0, {}),
        (0.12, {'hips@pos': (0, -0.12, 0), 'thigh_L': (-45, 0, 0), 'thigh_R': (-45, 0, 0), 'shin_L': (80, 0, 0), 'shin_R': (80, 0, 0),
                'chest': (20, 0, 0), 'upperarm_L': (40, 0, 10), 'upperarm_R': (40, 0, -10)}),
        (0.3, {'thigh_L': (-70, 0, 0), 'shin_L': (90, 0, 0), 'thigh_R': (20, 0, 0), 'shin_R': (40, 0, 0),
               'upperarm_L': (-140, 0, 20), 'upperarm_R': (-140, 0, -20), 'chest': (-8, 0, 0)}),
        (0.55, {'thigh_L': (-50, 0, 0), 'shin_L': (60, 0, 0), 'thigh_R': (-10, 0, 0), 'shin_R': (30, 0, 0),
                'upperarm_L': (-60, 0, 40), 'upperarm_R': (-60, 0, -40)}),
        (0.7, {}),
    ]), loop=False)

    sit = -(hipsY - 0.55)
    m.clip('SitTyping', 1.0, osc(1.0, 12, lambda p: {
        'hips@pos': (0, sit, 0), 'thigh_L': (-88, 0, 3), 'thigh_R': (-88, 0, -3), 'shin_L': (88, 0, 0), 'shin_R': (88, 0, 0),
        'foot_L': (0, 0, 0), 'chest': (6, 0, 0), 'head': (12 + 2 * S(p), 4 * S(p, 0.999), 0),
        'upperarm_L': (-38, 0, 8), 'upperarm_R': (-38, 0, -8),
        'forearm_L': (-52 + 5 * S(p, 4), 0, 0), 'forearm_R': (-52 + 5 * S(p, 4, 0.5), 0, 0)}))

    m.clip('Sip', 4.0, posed([
        (0.0, {'upperarm_R': (-15, 0, -8), 'forearm_R': (-80, 0, 0), 'upperarm_L': (0, 0, 6)}),
        (1.2, {'upperarm_R': (-15, 0, -8), 'forearm_R': (-80, 0, 0), 'upperarm_L': (0, 0, 6)}),
        (1.8, {'upperarm_R': (-45, 0, -15), 'forearm_R': (-128, 0, 0), 'head': (-14, 0, 0), 'upperarm_L': (0, 0, 6)}),
        (2.6, {'upperarm_R': (-48, 0, -15), 'forearm_R': (-130, 0, 0), 'head': (-18, 0, 0), 'upperarm_L': (0, 0, 6)}),
        (3.3, {'upperarm_R': (-15, 0, -8), 'forearm_R': (-80, 0, 0), 'upperarm_L': (0, 0, 6)}),
        (4.0, {'upperarm_R': (-15, 0, -8), 'forearm_R': (-80, 0, 0), 'upperarm_L': (0, 0, 6)}),
    ]))

    m.clip('Stir', 1.4, osc(1.4, 16, lambda p: {
        'upperarm_R': (-45 + 6 * C(p), 0, -10 + 8 * S(p)), 'forearm_R': (-50 + 10 * C(p), 20 * S(p), 0),
        'upperarm_L': (-25, 0, 10), 'forearm_L': (-60, 0, 0), 'chest': (8, 0, 0), 'head': (18, 0, 0),
        'hips': (0, 3 * S(p), 0)}))

    m.clip('Point', 0.6, posed([
        (0.0, {}),
        (0.25, {'upperarm_R': (-95, 0, 0), 'forearm_R': (-5, 0, 0), 'head': (-6, 0, 0), 'chest': (-6, -12, 0),
                'upperarm_L': (-10, 0, 35), 'forearm_L': (-60, 0, 0)}),
        (0.6, {'upperarm_R': (-92, 0, 0), 'forearm_R': (-5, 0, 0), 'head': (-4, 0, 0), 'chest': (-6, -12, 0),
               'upperarm_L': (-10, 0, 35), 'forearm_L': (-60, 0, 0)}),
    ]), loop=False)


def save(m, rel):
    info = m.save(os.path.join(OUT, rel))
    MANIFEST[m.name] = info
    print('%-22s tris=%6d size=%s anims=%d' % (m.name, info['triangles'], info['size_m'], len(info['animations'])))


# ---------------------------------------------------------------- shared accessory makers
def acc_glasses(m, y, z, H=1.0, frame='#222222', round_=False, group='acc_glasses'):
    for sx in (1, -1):
        if round_:
            m.add(torus(0.036, 0.007, 16, 6), frame, mat='satin', t=(sx * 0.058, y, z), r=(90, 0, 0), group=group, bone='head')
        else:
            m.add(torus(0.05, 0.008, 4, 4), frame, mat='satin', t=(sx * 0.058, y, z), r=(90, 45, 0), s=(1, 1, 0.8), group=group, bone='head')
        m.add(box(0.06, 0.045, 0.004), '#cfe8ff', mat='glass', t=(sx * 0.058, y, z), group=group, bone='head')
        m.add(box(0.008, 0.008, 0.14), frame, t=(sx * 0.125, y + 0.005, z - 0.07), group=group, bone='head')
    m.add(box(0.04, 0.008, 0.008), frame, t=(0, y + 0.005, z), group=group, bone='head')


# =====================================================================  OFFICE WORKER (GARY)
def build_office_worker():
    m = humanoid('office_worker', shirt='#f2f2ec', pants='#c2ab7c', shoes='#5a3a22', hair='#4a3426', sleeves='short')
    hy = 1.67
    # default short hair cap
    m.add(sphere(0.142, 16, 8, 0, math.pi * 0.55), '#4a3426', t=(0, hy + 0.03, -0.005), s=(0.95, 0.95, 1.0), group='hair', bone='head')
    # belt + buttons
    m.add(rbox(0.38, 0.04, 0.25, 0.015), '#3a2a1f', t=(0, 0.985, 0), group='body', bone='hips')
    m.add(box(0.05, 0.035, 0.02), '#d9c27a', mat='metal', t=(0, 0.985, 0.128), group='body', bone='hips')
    # Gary costume wig: combover
    m.add(sphere(0.14, 16, 8, 0, math.pi * 0.42), '#5b3f2b', t=(0, hy + 0.045, 0), s=(1, 0.75, 1.0), group='acc_combover', bone='head')
    m.add(capsule(0.03, 0.2, 10), '#5b3f2b', t=(0.0, hy + 0.15, 0.02), r=(0, 0, 80), s=(1, 0.6, 1), group='acc_combover', bone='head')
    for sx in (1, -1):
        m.add(rbox(0.03, 0.12, 0.17, 0.012), '#5b3f2b', t=(sx * 0.13, hy + 0.04, -0.02), group='acc_combover', bone='head')
    # mustaches
    def stache(group, rot, off):
        for sx in (1, -1):
            m.add(capsule(0.022, 0.06, 10), '#4a2e1c', t=(sx * 0.038 + off, hy - 0.045, 0.142), r=(0, 0, sx * 70 + rot), group=group, bone='head')
    stache('acc_mustache', 0, 0)
    stache('acc_mustache_crooked', 14, 0.012)
    # glasses
    acc_glasses(m, hy + 0.03, 0.146)
    # tie + stain
    m.add(box(0.05, 0.04, 0.03), '#c0262d', t=(0, 1.43, 0.125), group='acc_tie', bone='chest')
    m.add(lathe([(0.0001, 0), (0.035, 0.03), (0.03, 0.34), (0.0001, 0.36)], 4), '#c0262d', t=(0, 1.05, 0.135), s=(1, 1, 0.25), r=(0, 45, 0), group='acc_tie', bone='chest')
    m.add(sphere(0.022, 10, 6), '#6b4426', t=(0.006, 1.2, 0.143), s=(1.2, 1.4, 0.25), group='acc_tie_stain', bone='chest')
    m.add(sphere(0.01, 8, 6), '#6b4426', t=(-0.012, 1.17, 0.143), s=(1, 1, 0.25), group='acc_tie_stain', bone='chest')
    # watches
    for sd, sx in (('L', 1), ('R', -1)):
        g = 'acc_watch_' + sd
        m.add(torus(0.05, 0.012, 14, 6), '#2b2b2b', t=(sx * 0.228, 0.95, 0), s=(1, 1.4, 1), group=g, bone='forearm_' + sd)
        m.add(cylinder(0.022, 0.022, 0.012, 14), '#e8c35a', mat='metal', t=(sx * 0.228, 0.95, 0.055), r=(90, 0, 0), group=g, bone='forearm_' + sd)
    # pen behind ear
    m.add(cylinder(0.008, 0.008, 0.14, 8), '#2a5bd7', mat='satin', t=(-0.135, hy + 0.03, -0.01), r=(75, 0, 0), group='acc_pen_ear', bone='head')
    m.add(cone(0.008, 0.02, 8), '#e6d3a8', t=(-0.135, hy + 0.01, 0.065), r=(75, 0, 0), group='acc_pen_ear', bone='head')
    # lanyard + badge
    m.add(torus(0.1, 0.008, 18, 4), '#2a6fd6', t=(0, 1.42, 0.02), r=(40, 0, 0), s=(1, 1, 1.25), group='acc_lanyard', bone='chest')
    m.add(rbox(0.07, 0.095, 0.01, 0.006), '#ffffff', t=(0, 1.26, 0.132), group='acc_lanyard', bone='chest')
    m.add(box(0.07, 0.02, 0.012), '#2a6fd6', t=(0, 1.295, 0.132), group='acc_lanyard', bone='chest')
    # party hat (Gary Day!)
    m.add(cone(0.075, 0.2, 16), '#ff4fa3', mat='satin', t=(0.03, hy + 0.22, 0), r=(0, 0, -12), group='acc_party_hat', bone='head')
    m.add(sphere(0.025, 8, 6), '#ffe14d', t=(0.05, hy + 0.32, 0), group='acc_party_hat', bone='head')
    # mug in right hand ("WORLD'S OKAYEST BOSS")
    m.add(lathe([(0.0001, 0), (0.042, 0), (0.044, 0.1), (0.036, 0.1), (0.034, 0.012), (0.0001, 0.012)], 16), '#ffffff', mat='gloss',
          t=(-0.232, 0.81, 0.06), group='acc_mug', bone='hand_R')
    m.add(torus(0.025, 0.007, 12, 6), '#ffffff', mat='gloss', t=(-0.19, 0.86, 0.06), r=(90, 0, 0), group='acc_mug', bone='hand_R')
    m.add(cylinder(0.035, 0.035, 0.004, 14), '#5b3820', t=(-0.232, 0.9, 0.06), group='acc_mug', bone='hand_R')
    m.add(cylinder(0.0441, 0.0441, 0.03, 16, caps=False), '#ffd23f', t=(-0.232, 0.86, 0.06), group='acc_mug', bone='hand_R')
    m.notes['usage'] = ('Gary costume = show acc_combover+acc_mustache(_crooked)+acc_glasses+acc_tie+acc_lanyard, hide hair. '
                        'Tells: acc_mustache (real) vs acc_mustache_crooked (fake), acc_tie_stain, acc_watch_R vs acc_watch_L, acc_pen_ear, acc_mug.')
    save(m, 'office_worker.glb')


# =====================================================================  GROOM
def build_groom():
    m = humanoid('groom', shirt='#1d1d26', pants='#1d1d26', shoes='#0e0e10', skin='#d9a27a', hair='#1c140f', sleeves='long', height=1.03, width=1.02)
    hy = 1.67 * 1.03
    m.add(sphere(0.145, 16, 8, 0, math.pi * 0.5), '#1c140f', mat='gloss', t=(0, hy + 0.03, -0.01), s=(0.96, 0.9, 1.02), group='hair', bone='head')
    m.add(capsule(0.04, 0.12, 10), '#1c140f', mat='gloss', t=(0.03, hy + 0.15, 0.08), r=(0, 0, 80), group='hair', bone='head')
    # white shirt front, bow tie, lapels, boutonniere
    m.add(box(0.12, 0.26, 0.02), '#ffffff', t=(0, 1.33 * 1.03, 0.125), group='body', bone='chest')
    for sx in (1, -1):
        m.add(box(0.05, 0.24, 0.025), '#111116', mat='satin', t=(sx * 0.07, 1.33 * 1.03, 0.128), r=(0, 0, sx * 12), group='body', bone='chest')
        m.add(cone(0.03, 0.06, 4), '#111111', t=(sx * 0.035, 1.46 * 1.03, 0.14), r=(0, 0, sx * 90), group='body', bone='chest')
        m.add(box(0.02, 0.06, 0.08), '#ffffff', t=(sx * 0.228 * 1.02, 0.94 * 1.03, 0), group='body', bone='forearm_' + ('L' if sx > 0 else 'R'))  # cuffs
    m.add(sphere(0.015, 8, 6), '#111111', t=(0, 1.46 * 1.03, 0.142), group='body', bone='chest')
    m.add(sphere(0.028, 10, 6), '#e3263a', t=(0.12, 1.42 * 1.03, 0.13), group='body', bone='chest')
    m.add(cone(0.02, 0.05, 6), '#3c8c3c', t=(0.13, 1.385 * 1.03, 0.128), r=(0, 0, 160), group='body', bone='chest')
    for i in range(3):
        m.add(sphere(0.008, 6, 4), '#222222', t=(0, (1.24 + i * 0.05) * 1.03, 0.137), group='body', bone='chest')
    # sweat drops (show while running)
    for (x, y, z) in ((0.12, hy + 0.08, 0.06), (-0.11, hy + 0.1, 0.07), (0.05, hy + 0.17, 0.11)):
        m.add(sphere(0.018, 8, 6), '#9fd8ff', mat='gloss', t=(x, y, z), s=(1, 1.5, 1), group='acc_sweat', bone='head')
    save(m, 'groom.glb')


# =====================================================================  BRIDE
def build_bride():
    m = humanoid('bride', shirt='#fbf8f2', pants='#fbf8f2', shoes='#f4f0e8', skin='#c98a64', hair='#3a2216', sleeves='none', lower='dress', height=0.97, width=0.92)
    H = 0.97; hy = 1.67 * H
    m.add(sphere(0.145, 16, 8, 0, math.pi * 0.55), '#3a2216', t=(0, hy + 0.03, -0.01), group='hair', bone='head')
    m.add(sphere(0.07, 12, 8), '#3a2216', t=(0, hy + 0.06, -0.14), group='hair', bone='head')
    m.add(lathe([(0.0001, 0.0), (0.5, 0.0), (0.42, 0.12), (0.26, 0.5), (0.19, 0.78), (0.0001, 0.8)], 24, smooth_profile=True), '#fbf8f2',
          mat='satin', t=(0, 0.12, 0), group='shirt', bone='hips')
    m.add(cone(0.24, 0.9, 20), '#ffffff', mat='glass', t=(0, hy - 0.32, -0.12), r=(-8, 0, 0), group='acc_veil', bone='head')
    m.add(torus(0.13, 0.015, 20, 6), '#f2d16b', mat='metal', t=(0, hy + 0.12, -0.01), r=(15, 0, 0), group='acc_veil', bone='head')
    # bouquet
    for i, (dx, dz) in enumerate(((0, 0), (0.04, 0.02), (-0.04, 0.02), (0.02, -0.03), (-0.02, -0.03))):
        m.add(sphere(0.035, 10, 6), ['#ff7aa2', '#ffffff', '#ffb3c8', '#ff4f7f', '#fff0a0'][i], t=(-0.22 * 0.92 + dx, 0.84 * H, 0.1 + dz),
              group='acc_bouquet', bone='hand_R')
    m.add(cone(0.035, 0.16, 8), '#4f8f3c', t=(-0.22 * 0.92, 0.76 * H, 0.1), r=(180, 0, 0), group='acc_bouquet', bone='hand_R')
    save(m, 'bride.glb')


# =====================================================================  GRANDMA
def build_grandma():
    H = 0.9
    m = humanoid('grandma', height=H, width=1.06, belly=0.05, skin='#f0c7a6', hair='#d9d9de', shirt='#8e5aa8', pants='#6a4b7a',
                 shoes='#ff9cc0', sleeves='long', lower='dress', head_scale=1.04)
    hy = 1.67 * H
    m.add(sphere(0.15, 16, 8, 0, math.pi * 0.55), '#d9d9de', t=(0, hy + 0.035, -0.01), group='hair', bone='head')
    m.add(sphere(0.08, 12, 8), '#d9d9de', t=(0, hy + 0.12, -0.08), group='hair', bone='head')   # bun
    # long skirt
    m.add(lathe([(0.0001, 0.0), (0.3, 0.0), (0.27, 0.15), (0.2, 0.55), (0.0001, 0.57)], 20, smooth_profile=True), '#6a4b7a',
          t=(0, 0.3, 0), group='pants', bone='hips')
    # cardigan buttons + collar
    for i in range(4):
        m.add(sphere(0.012, 6, 4), '#f3e3b3', mat='gloss', t=(0, (1.16 + i * 0.065) * H, 0.155), group='body', bone='chest' if i > 1 else 'spine')
    # fuzzy slippers pom-poms
    for sx in (1, -1):
        m.add(sphere(0.045, 10, 6), '#ffd0e2', t=(sx * 0.106, 0.09, 0.14), group='body', bone='foot_' + ('L' if sx > 0 else 'R'))
    # pearls
    for i in range(14):
        a = math.pi * (0.1 + 0.8 * i / 13)
        m.add(sphere(0.012, 6, 4), '#fbf6ea', mat='gloss', t=(math.cos(a) * 0.1, 1.44 * H - math.sin(a) * 0.06, 0.06 + math.sin(a) * 0.07),
              group='body', bone='chest')
    acc_glasses(m, hy + 0.03, 0.15, frame='#b08a3a', round_=True, group='acc_glasses')
    # apron
    m.add(rbox(0.3, 0.42, 0.02, 0.01), '#fff7ec', t=(0, 0.9 * H, 0.19), group='acc_apron', bone='hips')
    m.add(box(0.3, 0.06, 0.022), '#ff8fb1', t=(0, 0.72 * H, 0.19), group='acc_apron', bone='hips')
    # soup ladle
    m.add(cylinder(0.01, 0.01, 0.32, 8), '#c9c9cf', mat='metal', t=(-0.24, 0.76 * H, 0.06), r=(20, 0, 0), group='acc_ladle', bone='hand_R')
    m.add(sphere(0.045, 12, 6, math.pi / 2, math.pi), '#c9c9cf', mat='metal', t=(-0.24, 0.62 * H, 0.11), group='acc_ladle', bone='hand_R')
    save(m, 'grandma.glb')


# =====================================================================  GOOSE
def build_goose():
    m = Model('goose', tint_groups=())
    for b, p, pos_ in [('body', None, (0, 0.38, 0)), ('neck1', 'body', (0, 0.48, 0.17)), ('neck2', 'neck1', (0, 0.63, 0.22)),
                       ('head', 'neck2', (0, 0.79, 0.24)), ('jaw', 'head', (0, 0.795, 0.3)),
                       ('wing_L', 'body', (0.15, 0.47, 0.08)), ('wing_R', 'body', (-0.15, 0.47, 0.08)),
                       ('leg_L', 'body', (0.07, 0.27, 0.0)), ('leg_R', 'body', (-0.07, 0.27, 0.0))]:
        m.bone(b, p, pos_)
    W, O, D = '#f5f3ee', '#ff8a1f', '#16161a'
    m.add(sphere(0.2, 18, 12), W, t=(0, 0.38, -0.02), s=(0.95, 0.82, 1.45), group='body', bone='body')
    m.add(cone(0.11, 0.2, 10), W, t=(0, 0.45, -0.33), r=(-115, 0, 0), s=(1, 1, 0.6), group='body', bone='body')
    m.add(tube([(0, 0.45, 0.14), (0, 0.56, 0.2), (0, 0.64, 0.22)], 0.048, 10), W, group='body', bone='neck1')
    m.add(tube([(0, 0.62, 0.22), (0, 0.72, 0.23), (0, 0.8, 0.24)], 0.044, 10), W, group='body', bone='neck2')
    m.add(sphere(0.07, 14, 10), W, t=(0, 0.81, 0.25), s=(0.9, 0.95, 1.15), group='body', bone='head')
    m.add(sphere(0.022, 8, 6), O, t=(0, 0.845, 0.31), group='body', bone='head')  # knob
    m.add(cone(0.032, 0.11, 10), O, t=(0, 0.808, 0.355), r=(90, 0, 0), s=(1, 0.65, 1), group='body', bone='head')
    m.add(cone(0.026, 0.09, 10), O, t=(0, 0.788, 0.345), r=(90, 0, 0), s=(1, 0.45, 1), group='body', bone='jaw')
    for sx in (1, -1):
        m.add(sphere(0.014, 8, 6), D, mat='gloss', t=(sx * 0.052, 0.83, 0.28), group='body', bone='head')
        m.add(box(0.045, 0.01, 0.012), D, t=(sx * 0.05, 0.853, 0.282), r=(0, sx * 20, sx * -25), group='body', bone='head')   # angry brows
        side = 'L' if sx > 0 else 'R'
        wing = sphere(0.12, 14, 8)
        m.add(wing, '#e2ded6', t=(sx * 0.27, 0.47, 0.08), s=(1.45, 0.3, 0.75), group='body', bone='wing_' + side)
        m.add(cone(0.05, 0.12, 6), '#c9c4ba', t=(sx * 0.43, 0.47, 0.06), r=(0, 0, sx * -90), s=(1, 1, 0.4), group='body', bone='wing_' + side)
        m.add(cylinder(0.016, 0.014, 0.24, 8), O, t=(sx * 0.07, 0.15, 0), group='body', bone='leg_' + side)
        m.add(cone(0.06, 0.12, 3), O, t=(sx * 0.07, 0.012, 0.05), r=(90, 0, 0), s=(1, 1, 0.15), group='body', bone='leg_' + side, flat=True)
    m.marker('socket_beak', (0, 0.8, 0.41), bone='head')
    fold = lambda l=0: {'wing_L': (0, 80 - l, 0), 'wing_R': (0, -80 + l, 0)}
    m.clip('Idle', 3.0, osc(3.0, 12, lambda p: {**fold(), 'neck1': (6 * S(p), 0, 0), 'neck2': (-4 * S(p), 15 * S(p, 1, 0.2), 0),
                                                   'head': (0, 20 * S(p, 2), 8 * S(p)), 'body': (2 * S(p), 0, 0)}))
    m.clip('Walk', 0.5, osc(0.5, 10, lambda p: {**fold(), 'body': (0, 4 * S(p), 9 * S(p)), 'leg_L': (35 * S(p), 0, -9 * S(p)), 'leg_R': (-35 * S(p), 0, -9 * S(p)),
                                                  'neck1': (12 + 10 * S(p, 2), 0, 0), 'neck2': (-6 * S(p, 2), 0, 0), 'body@pos': (0, 0.015 * C(p, 2), 0)}))
    m.clip('Honk', 0.7, posed([(0, fold()),
                                (0.15, {**fold(), 'neck1': (35, 0, 0), 'neck2': (-25, 0, 0), 'head': (-30, 0, 0), 'jaw': (35, 0, 0), 'body': (-6, 0, 0)}),
                                (0.45, {**fold(), 'neck1': (38, 0, 3), 'neck2': (-28, 0, -3), 'head': (-28, 0, 0), 'jaw': (40, 0, 0), 'body': (-6, 0, 0)}),
                                (0.7, fold())]), loop=False)
    m.clip('Charge', 0.36, osc(0.36, 12, lambda p: {
        'wing_L': (0, 15, 20 + 40 * S(p, 2)), 'wing_R': (0, -15, -20 - 40 * S(p, 2)),
        'neck1': (62, 0, 0), 'neck2': (12, 0, 0), 'head': (-55, 0, 0), 'jaw': (35 + 8 * S(p, 2), 0, 0),
        'body': (14, 0, 7 * S(p)), 'leg_L': (45 * S(p), 0, 0), 'leg_R': (-45 * S(p), 0, 0), 'body@pos': (0, 0.025 * C(p, 2), 0)}))
    m.clip('Flap', 0.5, osc(0.5, 12, lambda p: {
        'wing_L': (0, 5, 10 + 60 * S(p, 2)), 'wing_R': (0, -5, -10 - 60 * S(p, 2)), 'neck1': (-5, 0, 0), 'head': (-10, 0, 0),
        'jaw': (20, 0, 0), 'body@pos': (0, 0.12 * pos(S(p)), 0), 'leg_L': (20, 0, 0), 'leg_R': (20, 0, 0)}))
    m.clip('Netted', 0.6, osc(0.6, 12, lambda p: {**fold(10), 'body': (0, 0, 14 * S(p, 2)), 'neck1': (20 * S(p), 25 * S(p, 2), 0),
                                                    'jaw': (30 * pos(S(p, 3)), 0, 0), 'leg_L': (30 * S(p, 3), 0, 0), 'leg_R': (-30 * S(p, 3), 0, 0)}))
    m.clip('Stunned', 2.0, osc(2.0, 12, lambda p: {**fold(), 'body': (0, 0, 88), 'body@pos': (0, -0.22, 0), 'neck1': (0, 0, -30),
                                                     'head': (0, 30 * S(p), 0), 'leg_L': (20 * S(p, 2), 0, 0), 'leg_R': (-20 * S(p, 2), 0, 0)}))
    save(m, 'goose.glb')


# =====================================================================  CAT
def build_cat():
    m = Model('cat')
    for b, p, pp in [('body', None, (0, 0.22, 0)), ('head', 'body', (0, 0.3, 0.17)), ('tail1', 'body', (0, 0.26, -0.18)),
                     ('tail2', 'tail1', (0, 0.4, -0.25)), ('leg_FL', 'body', (0.06, 0.18, 0.12)), ('leg_FR', 'body', (-0.06, 0.18, 0.12)),
                     ('leg_BL', 'body', (0.06, 0.18, -0.12)), ('leg_BR', 'body', (-0.06, 0.18, -0.12))]:
        m.bone(b, p, pp)
    O, Dk, Wt = '#f29a3a', '#c86a1a', '#fff4e6'
    m.add(capsule(0.085, 0.22, 14), O, t=(0, 0.23, 0), r=(90, 0, 0), s=(1, 1, 0.92), group='body', bone='body')
    for i in range(3):
        m.add(sphere(0.06, 10, 6), Dk, t=(0, 0.305, -0.1 + i * 0.08), s=(1.25, 0.28, 0.35), group='body', bone='body')
    m.add(sphere(0.06, 10, 6), Wt, t=(0, 0.19, 0.11), s=(1, 1, 0.8), group='body', bone='body')
    m.add(sphere(0.085, 16, 10), O, t=(0, 0.33, 0.22), s=(1.1, 0.95, 0.95), group='body', bone='head')
    m.add(sphere(0.04, 10, 6), Wt, t=(0, 0.305, 0.295), s=(1.2, 0.8, 0.7), group='body', bone='head')
    m.add(sphere(0.012, 6, 4), '#ff7a9a', t=(0, 0.322, 0.31), group='body', bone='head')
    for sx in (1, -1):
        m.add(cone(0.035, 0.07, 4), O, t=(sx * 0.055, 0.405, 0.21), r=(0, 45, sx * -15), flat=True, group='body', bone='head')
        m.add(sphere(0.017, 8, 6), '#b9e85a', mat='gloss', t=(sx * 0.035, 0.345, 0.296), s=(1, 1.2, 0.5), group='body', bone='head')
        m.add(box(0.005, 0.02, 0.004), '#111111', t=(sx * 0.035, 0.345, 0.302), group='body', bone='head')
        for k in (-1, 1):
            m.add(box(0.07, 0.003, 0.003), '#ffffff', t=(sx * 0.06, 0.31 + k * 0.008, 0.29), r=(0, 0, sx * k * 8), group='body', bone='head')
    m.add(tube([(0, 0.26, -0.17), (0, 0.3, -0.23), (0, 0.4, -0.26)], 0.022, 8), O, group='body', bone='tail1')
    m.add(tube([(0, 0.4, -0.26), (0, 0.5, -0.26), (0, 0.55, -0.21)], 0.022, 8, radii=[0.022, 0.02, 0.016]), Dk, group='body', bone='tail2')
    for nm, x, z in (('FL', 0.06, 0.12), ('FR', -0.06, 0.12), ('BL', 0.06, -0.12), ('BR', -0.06, -0.12)):
        m.add(capsule(0.028, 0.13, 8), O, t=(x, 0.1, z), group='body', bone='leg_' + nm)
        m.add(sphere(0.032, 8, 6), Wt, t=(x, 0.022, z + 0.01), s=(1, 0.7, 1.2), group='body', bone='leg_' + nm)
    m.clip('Idle', 3.0, osc(3.0, 12, lambda p: {'tail1': (10 * S(p), 25 * S(p), 0), 'tail2': (0, 30 * S(p, 1, 0.2), 0), 'head': (0, 25 * S(p, 0.999 if False else 1, 0.5), 0)}))
    m.clip('Walk', 0.6, osc(0.6, 12, lambda p: {'leg_FL': (30 * S(p), 0, 0), 'leg_BR': (30 * S(p), 0, 0), 'leg_FR': (-30 * S(p), 0, 0), 'leg_BL': (-30 * S(p), 0, 0),
                                                 'tail1': (-20, 15 * S(p), 0), 'tail2': (0, 15 * S(p, 1, 0.3), 0), 'body@pos': (0, 0.008 * C(p, 2), 0), 'head': (4 * S(p, 2), 0, 0)}))
    m.clip('Swat', 0.6, posed([(0, {}), (0.15, {'leg_FR': (-70, 0, 20), 'body': (-8, 0, 0), 'head': (-10, 0, 0)}),
                                (0.3, {'leg_FR': (-40, 0, -25), 'body': (-6, 0, 0)}), (0.6, {})]), loop=False)
    m.clip('Startled', 0.5, posed([(0, {}), (0.15, {'body@pos': (0, 0.25, 0), 'body': (0, 0, 0), 'tail1': (-60, 0, 0), 'tail2': (-30, 0, 0),
                                                    'leg_FL': (-30, 0, 20), 'leg_FR': (-30, 0, -20), 'leg_BL': (30, 0, 20), 'leg_BR': (30, 0, -20)}),
                                   (0.35, {'body@pos': (0, 0.1, 0), 'tail1': (-70, 0, 0), 'tail2': (-30, 0, 0)}), (0.5, {'tail1': (-60, 0, 0)})]), loop=False)
    m.marker('socket_mouth', (0, 0.3, 0.31), bone='head')
    save(m, 'cat.glb')


# =====================================================================  BALLOON ANIMALS
def balloon(m, a, b, r, bone, colr='#ff3b5c'):
    m.add(tube([a, b], r, 14, caps=False), colr, mat='gloss', group='balloon', bone=bone)
    for p in (a, b):
        m.add(sphere(r, 14, 8), colr, mat='gloss', t=p, group='balloon', bone=bone)


def build_balloon_dog():
    m = Model('balloon_dog', tint_groups=('balloon',))
    for b, p, pp in [('root', None, (0, 0.0, 0)), ('body', 'root', (0, 0.32, 0)), ('head', 'body', (0, 0.5, 0.2)), ('tail', 'body', (0, 0.36, -0.2))]:
        m.bone(b, p, pp)
    R = 0.055
    balloon(m, (0, 0.34, -0.18), (0, 0.36, 0.16), R + 0.01, 'body')
    for sx in (1, -1):
        balloon(m, (sx * 0.07, 0.3, 0.16), (sx * 0.08, 0.05, 0.18), R, 'body')
        balloon(m, (sx * 0.07, 0.3, -0.17), (sx * 0.08, 0.05, -0.2), R, 'body')
    balloon(m, (0, 0.38, 0.18), (0, 0.52, 0.22), R, 'head')
    balloon(m, (0, 0.54, 0.22), (0, 0.5, 0.42), R, 'head')
    for sx in (1, -1):
        balloon(m, (sx * 0.02, 0.56, 0.22), (sx * 0.1, 0.66, 0.16), R * 0.9, 'head')
        m.add(sphere(0.016, 8, 6), '#111111', mat='gloss', t=(sx * 0.04, 0.585, 0.33), group='face', bone='head')
        m.add(box(0.05, 0.012, 0.012), '#111111', t=(sx * 0.04, 0.615, 0.33), r=(0, 0, sx * -28), group='face', bone='head')
    balloon(m, (0, 0.38, -0.2), (0, 0.55, -0.28), R * 0.85, 'tail')
    m.add(cone(0.02, 0.04, 8), '#ffffff', mat='gloss', t=(0, 0.58, -0.29), group='face', bone='tail')
    m.clip('Idle', 1.6, osc(1.6, 16, lambda p: {'body@pos': (0, 0.02 * S(p), 0), 'head': (6 * S(p), 10 * S(p, 0.999 if False else 1, 0.3), 0),
                                                  'tail': (0, 25 * S(p, 2), 0), 'root@scale': (1 + 0.02 * S(p, 2), 1 - 0.02 * S(p, 2), 1 + 0.02 * S(p, 2))}))
    m.clip('Hop', 0.5, osc(0.5, 12, lambda p: {'root@pos': (0, 0.3 * pos(S(p)), 0), 'body': (-15 * S(p), 0, 0), 'tail': (0, 40 * S(p, 2), 0),
                                                 'root@scale': (1 + 0.12 * pos(-S(p)), 1 - 0.15 * pos(-S(p)), 1 + 0.12 * pos(-S(p)))}))
    m.clip('Bite', 0.5, posed([(0, {}), (0.15, {'head': (-30, 0, 0), 'body': (-5, 0, 0)}), (0.25, {'head': (35, 0, 0), 'body': (12, 0, 0), 'root@pos': (0, 0, 0.1)}), (0.5, {})]), loop=False)
    m.clip('Pop', 0.25, posed([(0, {'root@scale': (1, 1, 1)}), (0.15, {'root@scale': (1.35, 1.35, 1.35)}), (0.25, {'root@scale': (0.01, 0.01, 0.01)})]), loop=False)
    save(m, 'balloon_dog.glb')


def build_balloon_giraffe():
    m = Model('balloon_giraffe', tint_groups=('balloon',))
    for b, p, pp in [('root', None, (0, 0, 0)), ('body', 'root', (0, 1.6, 0)), ('neck', 'body', (0, 1.75, 0.5)), ('head', 'neck', (0, 3.6, 0.75)),
                     ('leg_FL', 'body', (0.28, 1.5, 0.5)), ('leg_FR', 'body', (-0.28, 1.5, 0.5)), ('leg_BL', 'body', (0.28, 1.5, -0.5)), ('leg_BR', 'body', (-0.28, 1.5, -0.5))]:
        m.bone(b, p, pp)
    R = 0.2; colr = '#ffb000'
    balloon(m, (0, 1.65, -0.55), (0, 1.7, 0.55), R + 0.05, 'body', colr)
    for nm, x, z in (('FL', 0.28, 0.5), ('FR', -0.28, 0.5), ('BL', 0.28, -0.5), ('BR', -0.28, -0.5)):
        balloon(m, (x, 1.5, z), (x * 1.15, 0.2, z * 1.05), R, 'leg_' + nm, colr)
    balloon(m, (0, 1.85, 0.55), (0, 3.55, 0.78), R, 'neck', colr)
    balloon(m, (0, 3.65, 0.7), (0, 3.6, 1.35), R + 0.02, 'head', colr)
    for sx in (1, -1):
        balloon(m, (sx * 0.08, 3.8, 0.75), (sx * 0.15, 4.15, 0.68), R * 0.6, 'head', colr)
        m.add(sphere(0.06, 10, 8), '#111111', mat='gloss', t=(sx * 0.13, 3.75, 1.05), group='face', bone='head')
        m.add(box(0.2, 0.04, 0.04), '#111111', t=(sx * 0.13, 3.86, 1.05), r=(0, 0, sx * -25), group='face', bone='head')
    for i, (x, y, z) in enumerate(((0.18, 1.85, 0.0), (-0.15, 1.9, -0.3), (0.0, 1.95, 0.3), (0.12, 2.6, 0.7), (-0.12, 3.1, 0.75))):
        m.add(sphere(0.09, 10, 6), '#8a4b14', mat='gloss', t=(x, y, z), s=(1, 0.6, 1), group='spots', bone='body' if y < 2.2 else 'neck')
    m.marker('weakpoint_head', (0, 3.62, 1.0), bone='head')
    m.clip('Idle', 2.4, osc(2.4, 16, lambda p: {'neck': (8 * S(p), 6 * S(p, 1, 0.25), 0), 'head': (-6 * S(p), 15 * S(p, 1, 0.5), 0), 'body': (0, 0, 2 * S(p)),
                                                  'root@scale': (1 + 0.015 * S(p, 2), 1 - 0.015 * S(p, 2), 1)}))
    m.clip('Walk', 1.2, osc(1.2, 12, lambda p: {'leg_FL': (22 * S(p), 0, 0), 'leg_BR': (22 * S(p), 0, 0), 'leg_FR': (-22 * S(p), 0, 0), 'leg_BL': (-22 * S(p), 0, 0),
                                                  'neck': (6 * S(p, 2), 0, 0), 'body@pos': (0, 0.05 * C(p, 2), 0)}))
    m.clip('Stomp', 1.2, posed([(0, {}), (0.4, {'body': (-22, 0, 0), 'leg_FL': (-40, 0, 0), 'leg_FR': (-40, 0, 0), 'neck': (-10, 0, 0), 'body@pos': (0, 0.3, 0)}),
                                 (0.55, {'body': (8, 0, 0), 'leg_FL': (10, 0, 0), 'leg_FR': (10, 0, 0), 'neck': (25, 0, 0), 'head': (20, 0, 0),
                                         'root@scale': (1.08, 0.9, 1.08)}), (1.2, {})]), loop=False)
    m.clip('Hurt', 0.5, posed([(0, {}), (0.1, {'root@scale': (1.15, 0.8, 1.15), 'neck': (-20, 0, 10)}), (0.3, {'root@scale': (0.92, 1.1, 0.92)}), (0.5, {})]), loop=False)
    m.clip('Pop', 0.3, posed([(0, {'root@scale': (1, 1, 1)}), (0.18, {'root@scale': (1.4, 1.4, 1.4)}), (0.3, {'root@scale': (0.01, 0.01, 0.01)})]), loop=False)
    save(m, 'balloon_giraffe.glb')


# =====================================================================  ALARM CLOCK BOSS
def build_alarm_clock():
    m = Model('alarm_clock_boss')
    for b, p, pp in [('root', None, (0, 0, 0)), ('body', 'root', (0, 1.35, 0)), ('bell_L', 'body', (0.5, 2.3, -0.05)), ('bell_R', 'body', (-0.5, 2.3, -0.05)),
                     ('hammer', 'body', (0, 2.25, -0.05)), ('hand_hour', 'body', (0, 1.35, 0.33)), ('hand_minute', 'body', (0, 1.35, 0.34)),
                     ('leg_L', 'body', (0.42, 0.62, 0)), ('leg_R', 'body', (-0.42, 0.62, 0)),
                     ('arm_L', 'body', (0.85, 1.35, 0)), ('arm_R', 'body', (-0.85, 1.35, 0))]:
        m.bone(b, p, pp)
    RED, GOLD, BLK = '#e8322f', '#f2c14e', '#1b1b1f'
    m.add(cylinder(0.85, 0.85, 0.6, 32), RED, mat='satin', t=(0, 1.35, 0), r=(90, 0, 0), group='body', bone='body')
    m.add(torus(0.8, 0.06, 32, 10), GOLD, mat='metal', t=(0, 1.35, 0.3), r=(90, 0, 0), group='body', bone='body')
    m.add(cylinder(0.78, 0.78, 0.02, 32), '#fffaf0', mat='satin', t=(0, 1.35, 0.3), r=(90, 0, 0), group='face', bone='body')
    for i in range(12):
        a = math.radians(i * 30)
        L = 0.12 if i % 3 == 0 else 0.06
        m.add(box(0.035, L, 0.02), BLK, t=(math.sin(a) * 0.66, 1.35 + math.cos(a) * 0.66, 0.315), r=(0, 0, -i * 30), group='face', bone='body')
    # angry face
    for sx in (1, -1):
        m.add(sphere(0.13, 16, 10), '#ffffff', mat='gloss', t=(sx * 0.25, 1.6, 0.31), s=(1, 1.15, 0.35), group='face', bone='body')
        m.add(sphere(0.06, 12, 8), BLK, mat='gloss', t=(sx * 0.22, 1.57, 0.355), s=(1, 1, 0.4), group='face', bone='body')
        m.add(box(0.3, 0.06, 0.04), BLK, t=(sx * 0.25, 1.8, 0.33), r=(0, 0, sx * -20), group='face', bone='body')
    m.add(rbox(0.5, 0.14, 0.04, 0.03), '#5a0d12', t=(0, 1.0, 0.315), group='face', bone='body')
    for i in range(6):
        m.add(box(0.07, 0.05, 0.03), '#ffffff', t=(-0.2 + i * 0.08, 1.045, 0.33), group='face', bone='body')
    m.add(box(0.06, 0.32, 0.02), BLK, t=(0, 1.35 + 0.14, 0.33), group='face', bone='hand_hour')
    m.add(box(0.04, 0.5, 0.02), BLK, t=(0, 1.35 + 0.22, 0.345), group='face', bone='hand_minute')
    m.add(cylinder(0.05, 0.05, 0.04, 12), GOLD, mat='metal', t=(0, 1.35, 0.35), r=(90, 0, 0), group='face', bone='hand_minute')
    # bells + hammer + snooze button
    for sx, b in ((1, 'bell_L'), (-1, 'bell_R')):
        m.add(sphere(0.32, 20, 10, 0, math.pi / 2), GOLD, mat='metal', t=(sx * 0.5, 2.2, -0.05), r=(0, 0, sx * -35), group='body', bone=b)
        m.add(cylinder(0.04, 0.04, 0.3, 10), GOLD, mat='metal', t=(sx * 0.4, 2.05, -0.05), r=(0, 0, sx * -35), group='body', bone=b)
        m.add(sphere(0.06, 10, 6), GOLD, mat='metal', t=(sx * 0.68, 2.47, -0.05), group='body', bone=b)
    m.add(cylinder(0.03, 0.03, 0.4, 8), '#9a9aa2', mat='metal', t=(0, 2.4, -0.05), group='body', bone='hammer')
    m.add(sphere(0.08, 12, 8), '#9a9aa2', mat='metal', t=(0, 2.6, -0.05), group='body', bone='hammer')
    m.add(cylinder(0.2, 0.22, 0.12, 20), '#ff8a00', mat='glow', t=(0, 2.22, -0.25), group='snooze', bone='body')
    m.add(cylinder(0.26, 0.26, 0.06, 20), '#333338', mat='metal', t=(0, 2.16, -0.25), group='body', bone='body')
    m.marker('weakpoint_snooze', (0, 2.3, -0.25), bone='body')
    # legs + arms
    for sx, s in ((1, 'L'), (-1, 'R')):
        m.add(cylinder(0.05, 0.05, 0.55, 10), '#9a9aa2', mat='metal', t=(sx * 0.42, 0.36, 0), group='body', bone='leg_' + s)
        m.add(sphere(0.16, 14, 8), BLK, mat='satin', t=(sx * 0.42, 0.08, 0.06), s=(1, 0.55, 1.3), group='body', bone='leg_' + s)
        m.add(tube([(sx * 0.85, 1.35, 0), (sx * 1.1, 1.2, 0.05), (sx * 1.2, 0.95, 0.1)], 0.045, 8), '#9a9aa2', mat='metal', group='body', bone='arm_' + s)
        m.add(sphere(0.12, 12, 8), '#ffffff', mat='satin', t=(sx * 1.22, 0.88, 0.1), group='body', bone='arm_' + s)
    # idle: hands tick slowly; minute hand full spin
    def tick(p, speed=1):
        return {'hand_minute': (0, 0, -360 * p * speed), 'hand_hour': (0, 0, -30 * p * speed)}
    m.clip('Idle', 2.0, osc(2.0, 24, lambda p: {**tick(p), 'body@pos': (0, 0.05 * S(p, 2), 0), 'body': (0, 0, 3 * S(p)),
                                                  'arm_L': (0, 0, 10 * S(p)), 'arm_R': (0, 0, -10 * S(p))}))
    m.clip('Ring', 0.4, osc(0.4, 16, lambda p: {**tick(p, 4), 'body': (0, 0, 7 * S(p, 4)), 'hammer': (0, 0, 40 * S(p, 4)), 'bell_L': (0, 0, 4 * S(p, 4)),
                                                  'bell_R': (0, 0, -4 * S(p, 4)), 'arm_L': (0, 0, 60 + 20 * S(p, 2)), 'arm_R': (0, 0, -60 - 20 * S(p, 2)),
                                                  'body@pos': (0.03 * S(p, 8), 0.06 * pos(S(p, 4)), 0)}))
    m.clip('Hop', 0.9, posed([(0, {}), (0.2, {'body@pos': (0, -0.25, 0), 'leg_L': (0, 0, 20), 'leg_R': (0, 0, -20), 'body@scale': (1.08, 0.9, 1.08)}),
                               (0.5, {'body@pos': (0, 1.3, 0), 'arm_L': (0, 0, 80), 'arm_R': (0, 0, -80), 'body@scale': (0.95, 1.08, 0.95)}),
                               (0.8, {'body@pos': (0, -0.15, 0), 'body@scale': (1.1, 0.88, 1.1)}), (0.9, {})]), loop=False)
    m.clip('Charge', 0.4, osc(0.4, 12, lambda p: {**tick(p, 3), 'body': (18, 0, 6 * S(p)), 'leg_L': (40 * S(p), 0, 0), 'leg_R': (-40 * S(p), 0, 0),
                                                    'arm_L': (-40 * S(p), 0, 30), 'arm_R': (40 * S(p), 0, -30), 'body@pos': (0, 0.06 * C(p, 2), 0)}))
    m.clip('Stunned', 1.5, osc(1.5, 18, lambda p: {**tick(p, 6), 'body': (6 * S(p), 0, 12 * S(p, 1, 0.25)), 'arm_L': (0, 0, 5), 'arm_R': (0, 0, -5),
                                                     'body@pos': (0, -0.15, 0), 'hammer': (0, 0, 60)}))
    m.clip('Defeated', 1.6, posed([(0, {}), (0.3, {'body': (-10, 0, 10), 'hand_minute': (0, 0, -720), 'body@pos': (0, 0.2, 0)}),
                                    (0.9, {'body': (-88, 0, 15), 'hand_minute': (0, 0, -1440), 'body@pos': (0, -0.6, -0.4), 'arm_L': (0, 0, 120), 'arm_R': (0, 0, -120)}),
                                    (1.1, {'body': (-82, 0, 10), 'body@pos': (0, -0.5, -0.4), 'hammer': (0, 0, 70)}),
                                    (1.6, {'body': (-90, 0, 12), 'body@pos': (0, -0.6, -0.42), 'hammer': (0, 0, 80), 'arm_L': (0, 0, 100), 'arm_R': (0, 0, -100)})]), loop=False)
    save(m, 'alarm_clock_boss.glb')


if __name__ == '__main__':
    build_office_worker(); build_groom(); build_bride(); build_grandma()
    build_goose(); build_cat(); build_balloon_dog(); build_balloon_giraffe(); build_alarm_clock()
    path = os.path.join(OUT, '..', '_manifest_characters.json')
    with open(path, 'w') as f: json.dump(MANIFEST, f, indent=1)
