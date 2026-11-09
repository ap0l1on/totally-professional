"""Static props, pickups & weapons -> public/assets/models/{props,weapons}/*.glb
Conventions: metres, base at y=0, front faces +Z, centred on x/z (unless noted)."""
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from gltf_builder import Model, Geo, box, rbox, sphere, cylinder, cone, capsule, lathe, torus, tube, v_norm

ROOT = os.path.join(os.path.dirname(__file__), '..', 'public', 'assets', 'models')
MAN = {'props': {}, 'weapons': {}}
REG = []

def prop(cat, level):
    def deco(fn):
        REG.append((cat, level, fn)); return fn
    return deco

def emit(m, cat, level, note=None):
    os.makedirs(os.path.join(ROOT, cat), exist_ok=True)
    info = m.save(os.path.join(ROOT, cat, m.name + '.glb'))
    info['level'] = level
    if note: info['note'] = note
    MAN[cat][m.name] = info
    print('%-8s %-20s tris=%5d size=%s' % (cat, m.name, info['triangles'], info['size_m']))

WOOD, WOOD_D, METAL, DARK, WHITE = '#c99a6b', '#8a5a3b', '#9aa0aa', '#2b2d33', '#f4f2ec'

def legs4(m, w, d, h, r=0.025, c=METAL, inset=0.06, mat='metal', square=True, group='main'):
    for sx in (1, -1):
        for sz in (1, -1):
            g = box(r * 2, h, r * 2) if square else cylinder(r, r, h, 10)
            m.add(g, c, mat=mat, t=(sx * (w / 2 - inset), h / 2, sz * (d / 2 - inset)), group=group)

def rock_geo(r=0.5, seed=1, seg=9, rings=6, jag=0.22):
    rnd = random.Random(seed); g = sphere(r, seg, rings)
    cache = {}
    for i, p in enumerate(g.p):
        key = tuple(round(x, 4) for x in p)
        if key not in cache: cache[key] = 1 + rnd.uniform(-jag, jag)
        k = cache[key]; g.p[i] = (p[0] * k, p[1] * k * 0.75, p[2] * k)
    return g.flat()

# ====================================================================== OFFICE (L1)
@prop('props', 'office')
def desk_setup():
    m = Model('desk_setup')
    m.add(rbox(1.4, 0.045, 0.72, 0.012), '#d8b48a', mat='satin', t=(0, 0.735, 0))
    for sx in (1, -1):
        m.add(box(0.04, 0.71, 0.64), '#7d8590', mat='metal', t=(sx * 0.66, 0.355, 0))
    m.add(box(1.28, 0.4, 0.02), '#7d8590', mat='metal', t=(0, 0.45, -0.32))
    # monitor (screen is its own node so code can swap emissive/texture)
    m.add(rbox(0.6, 0.38, 0.04, 0.012), DARK, mat='satin', t=(0, 1.1, -0.18))
    m.add(box(0.55, 0.32, 0.005), '#5fb0ff', mat='glow', t=(0, 1.1, -0.157), group='screen')
    m.add(box(0.05, 0.25, 0.04), DARK, t=(0, 0.88, -0.2))
    m.add(rbox(0.25, 0.015, 0.18, 0.006), DARK, t=(0, 0.765, -0.2))
    m.add(rbox(0.44, 0.022, 0.15, 0.008), '#3a3d45', t=(0, 0.768, 0.1))
    for i in range(4):
        m.add(box(0.4, 0.004, 0.025), '#d8dbe2', t=(0, 0.781, 0.05 + i * 0.033))
    m.add(capsule(0.025, 0.03, 10, 4), '#3a3d45', t=(0.32, 0.768, 0.12), r=(90, 0, 0), s=(1, 1, 0.5))
    for i in range(5):
        m.add(box(0.21, 0.006, 0.297), WHITE, t=(-0.45 + i * 0.004, 0.762 + i * 0.006, 0.0), r=(0, i * 4, 0))
    m.add(box(0.07, 0.003, 0.07), '#ffe66b', t=(0.31, 1.25, -0.155), r=(90, 0, 8))
    m.add(lathe([(0.0001, 0), (0.035, 0), (0.038, 0.1), (0.0001, 0.1)], 12), '#e85d5d', t=(0.55, 0.757, -0.2))
    for i, c in enumerate(('#2a5bd7', '#e8322f', '#222222')):
        m.add(cylinder(0.005, 0.005, 0.14, 6), c, t=(0.545 + i * 0.01, 0.85, -0.2), r=(0, 0, -8 + i * 8))
    return m

@prop('props', 'office')
def office_chair():
    m = Model('office_chair')
    for i in range(5):
        a = i * 72
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        m.add(box(0.05, 0.035, 0.3), DARK, t=(sa * 0.15, 0.08, ca * 0.15), r=(0, a, 0))
        m.add(sphere(0.03, 8, 6), '#111111', t=(sa * 0.29, 0.03, ca * 0.29))
    m.add(cylinder(0.025, 0.025, 0.32, 10), '#b8bcc4', mat='metal', t=(0, 0.26, 0))
    m.add(rbox(0.5, 0.08, 0.48, 0.03), '#30343c', t=(0, 0.46, 0))
    m.add(rbox(0.46, 0.58, 0.07, 0.03), '#30343c', t=(0, 0.83, -0.24), r=(-8, 0, 0))
    m.add(box(0.05, 0.3, 0.04), DARK, t=(0, 0.55, -0.24))
    for sx in (1, -1):
        m.add(box(0.04, 0.2, 0.04), DARK, t=(sx * 0.26, 0.58, -0.02))
        m.add(rbox(0.06, 0.03, 0.26, 0.012), DARK, t=(sx * 0.26, 0.69, 0.0))
    return m

@prop('props', 'office')
def water_cooler():
    m = Model('water_cooler')
    m.add(rbox(0.32, 0.95, 0.32, 0.03), WHITE, mat='satin', t=(0, 0.475, 0))
    m.add(lathe([(0.0001, 0.95), (0.05, 0.95), (0.05, 1.0), (0.15, 1.06), (0.15, 1.38), (0.12, 1.43), (0.0001, 1.44)], 18), '#7cc4ff', mat='glass')
    m.add(cylinder(0.13, 0.13, 0.36, 16), '#3f8fe0', mat='gloss', t=(0, 1.2, 0))
    m.add(box(0.03, 0.04, 0.05), '#3c7cff', t=(-0.05, 0.75, 0.17))
    m.add(box(0.03, 0.04, 0.05), '#ff4c4c', t=(0.05, 0.75, 0.17))
    m.add(box(0.2, 0.02, 0.1), '#888888', t=(0, 0.6, 0.17))
    return m

@prop('props', 'common')
def potted_plant():
    m = Model('potted_plant')
    m.add(lathe([(0.0001, 0), (0.14, 0), (0.19, 0.36), (0.21, 0.36), (0.21, 0.4), (0.0001, 0.4)], 14), '#c8683f')
    m.add(cylinder(0.18, 0.18, 0.01, 14), '#4a3222', t=(0, 0.39, 0))
    rnd = random.Random(4)
    for i in range(9):
        a = i * 40 + rnd.uniform(-10, 10)
        m.add(sphere(0.12, 6, 4), ['#3e9a4a', '#4fb85a', '#2f7d3c'][i % 3], t=(math.sin(math.radians(a)) * 0.12, 0.62 + rnd.uniform(0, 0.25), math.cos(math.radians(a)) * 0.12),
              r=(rnd.uniform(-30, 30), a, 20), s=(0.6, 1.5, 0.25), flat=True)
    return m

@prop('props', 'office')
def printer():
    m = Model('printer')
    m.add(box(0.7, 0.7, 0.55), '#5c616b', t=(0, 0.35, 0))
    m.add(rbox(0.6, 0.32, 0.5, 0.03), '#e3e4e8', mat='satin', t=(0, 0.86, 0))
    m.add(box(0.42, 0.04, 0.3), '#c8cad0', t=(0, 1.04, -0.05))
    m.add(box(0.36, 0.01, 0.25), WHITE, t=(0, 0.9, 0.2), r=(-12, 0, 0), group='paper_out')
    m.add(box(0.12, 0.06, 0.01), '#78ff8a', mat='glow', t=(0.18, 0.95, 0.252), group='status_led')
    for i in range(3):
        m.add(cylinder(0.012, 0.012, 0.01, 8), ['#33cc55', '#ffaa00', '#ff3333'][i], t=(0.06 + i * 0.035, 0.95, 0.252), r=(90, 0, 0))
    m.add(box(0.5, 0.12, 0.02), '#4a4f58', t=(0, 0.5, 0.28))
    m.add(box(0.5, 0.12, 0.02), '#4a4f58', t=(0, 0.25, 0.28))
    return m

@prop('props', 'office')
def filing_cabinet():
    m = Model('filing_cabinet')
    m.add(box(0.46, 1.3, 0.6), '#8c96a3', mat='metal', t=(0, 0.65, 0))
    for i in range(4):
        y = 0.17 + i * 0.31
        m.add(rbox(0.42, 0.28, 0.02, 0.008), '#a3adba', mat='metal', t=(0, y, 0.305))
        m.add(rbox(0.14, 0.025, 0.04, 0.01), '#5d6470', mat='metal', t=(0, y + 0.06, 0.32))
        m.add(box(0.08, 0.04, 0.005), WHITE, t=(0, y + 0.1, 0.317))
    return m

@prop('props', 'office')
def cubicle_wall():
    m = Model('cubicle_wall')
    m.add(box(1.6, 1.3, 0.06), '#7a8aa3', t=(0, 0.67, 0))
    m.add(rbox(1.64, 0.04, 0.08, 0.015), '#b9bfc8', mat='metal', t=(0, 1.34, 0))
    for sx in (1, -1):
        m.add(box(0.04, 1.34, 0.08), '#b9bfc8', mat='metal', t=(sx * 0.8, 0.67, 0))
        m.add(box(0.06, 0.02, 0.4), '#b9bfc8', mat='metal', t=(sx * 0.7, 0.01, 0))
    m.add(box(0.15, 0.15, 0.003), '#ffe66b', t=(0.4, 1.1, 0.032), r=(0, 0, 5))
    m.add(box(0.15, 0.15, 0.003), '#ff9ac1', t=(0.58, 1.05, 0.032), r=(0, 0, -7))
    m.add(box(0.21, 0.297, 0.003), WHITE, t=(-0.45, 1.0, 0.032), r=(0, 0, 2))
    m.notes['note'] = 'Panel is 1.6m wide; tile along X to build cubicles. Both faces identical.'
    return m

@prop('props', 'office')
def coffee_mug():
    m = Model('coffee_mug')
    m.add(lathe([(0.0001, 0), (0.042, 0), (0.044, 0.1), (0.036, 0.1), (0.034, 0.012), (0.0001, 0.012)], 18), WHITE, mat='gloss')
    m.add(torus(0.028, 0.008, 12, 6), WHITE, mat='gloss', t=(0.05, 0.05, 0), r=(90, 0, 0))
    m.add(cylinder(0.035, 0.035, 0.004, 14), '#5b3820', t=(0, 0.088, 0))
    m.add(cylinder(0.0442, 0.0442, 0.03, 18, caps=False), '#ffd23f', t=(0, 0.05, 0))
    return m

@prop('props', 'office')
def ceiling_light():
    m = Model('ceiling_light')
    m.add(box(1.2, 0.06, 0.6), '#d9dbe0', mat='metal', t=(0, 0.03, 0))
    m.add(box(1.12, 0.01, 0.52), '#fffbe8', mat='glow', t=(0, -0.002, 0), group='light')
    m.notes['note'] = 'Origin at top; hang from ceiling (light faces -Y).'
    return m

@prop('props', 'office')
def whiteboard():
    m = Model('whiteboard')
    m.add(rbox(1.8, 1.0, 0.04, 0.015), '#c3c7cf', mat='metal', t=(0, 1.5, 0))
    m.add(box(1.72, 0.92, 0.01), '#fdfdfd', mat='gloss', t=(0, 1.5, 0.02))
    pts = [(-0.7, 1.15), (-0.4, 1.3), (-0.15, 1.22), (0.15, 1.55), (0.45, 1.48), (0.7, 1.85)]
    for (a, b) in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        m.add(box(math.hypot(dx, dy), 0.02, 0.004), '#2a8f4a', t=((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.027), r=(0, 0, math.degrees(math.atan2(dy, dx))))
    m.add(box(0.012, 0.75, 0.004), '#222222', t=(-0.75, 1.5, 0.027))
    m.add(box(1.55, 0.012, 0.004), '#222222', t=(0, 1.12, 0.027))
    m.add(box(0.6, 0.04, 0.08), '#a5aab3', mat='metal', t=(0, 0.98, 0.05))
    for i, c in enumerate(('#e8322f', '#2a5bd7', '#2a8f4a')):
        m.add(cylinder(0.01, 0.01, 0.12, 6), c, t=(-0.15 + i * 0.1, 1.01, 0.05), r=(0, 0, 90))
    for sx in (1, -1):
        m.add(box(0.04, 1.0, 0.04), '#a5aab3', mat='metal', t=(sx * 0.85, 0.5, -0.02))
        m.add(box(0.05, 0.03, 0.5), '#a5aab3', mat='metal', t=(sx * 0.85, 0.015, -0.02))
    return m

@prop('props', 'office')
def vending_machine():
    m = Model('vending_machine')
    m.add(rbox(0.95, 1.85, 0.8, 0.03), '#d8282f', mat='satin', t=(0, 0.925, 0))
    m.add(box(0.62, 1.3, 0.02), '#bfe3ff', mat='glass', t=(-0.1, 1.12, 0.405))
    cols = ['#ffcc00', '#2bb3ff', '#ff5aa0', '#7ddc4a', '#ff8a1f', '#a26bff']
    for row in range(5):
        m.add(box(0.6, 0.015, 0.6), '#9aa0aa', mat='metal', t=(-0.1, 0.55 + row * 0.25, 0.05))
        for k in range(5):
            m.add(box(0.08, 0.14, 0.05), cols[(row * 5 + k) % 6], mat='gloss', t=(-0.34 + k * 0.12, 0.64 + row * 0.25, 0.3))
    m.add(box(0.18, 0.5, 0.02), '#222222', t=(0.36, 1.3, 0.405))
    m.add(box(0.12, 0.06, 0.01), '#59ff8a', mat='glow', t=(0.36, 1.48, 0.416), group='display')
    for i in range(9):
        m.add(box(0.03, 0.03, 0.01), '#dddddd', t=(0.32 + (i % 3) * 0.04, 1.35 - (i // 3) * 0.045, 0.416))
    m.add(box(0.6, 0.15, 0.02), '#1a1a1a', t=(-0.1, 0.25, 0.405))
    m.add(box(0.95, 0.12, 0.1), '#fff1f1', mat='glow', t=(0, 1.78, 0.37), group='sign')
    return m

@prop('props', 'common')
def door():
    m = Model('door')
    W, Hh = 0.95, 2.1
    m.add(box(0.08, Hh + 0.08, 0.16), '#e8e3d8', t=(-(W / 2 + 0.04), (Hh + 0.08) / 2, 0))
    m.add(box(0.08, Hh + 0.08, 0.16), '#e8e3d8', t=((W / 2 + 0.04), (Hh + 0.08) / 2, 0))
    m.add(box(W + 0.16, 0.08, 0.16), '#e8e3d8', t=(0, Hh + 0.04, 0))
    m.add(box(W, Hh, 0.045), '#a8774f', mat='satin', t=(0, Hh / 2, 0), group='door')
    for y in (0.55, 1.45):
        m.add(box(W - 0.25, 0.6, 0.012), '#9a6a45', t=(0, y, 0.026), group='door')
        m.add(box(W - 0.25, 0.6, 0.012), '#9a6a45', t=(0, y, -0.026), group='door')
    for sz in (1, -1):
        m.add(sphere(0.035, 10, 6), '#d9b84a', mat='metal', t=(W / 2 - 0.1, 1.0, sz * 0.06), group='door')
    m.pivot('door', (-W / 2, 0, 0))
    m.notes['note'] = 'Node "door" pivots at its hinge (left edge). Rotate door.rotation.y to open.'
    return m

# ====================================================================== ROOFTOPS (L2)
@prop('props', 'rooftops')
def ac_unit():
    m = Model('ac_unit')
    m.add(rbox(1.3, 0.9, 1.0, 0.03), '#c5cad1', mat='metal', t=(0, 0.45, 0))
    for i in range(9):
        m.add(box(0.012, 0.6, 0.012), '#8b929c', t=(-0.5 + i * 0.125, 0.45, 0.505))
    m.add(cylinder(0.4, 0.4, 0.04, 24, caps=False), '#6f7782', mat='metal', t=(0, 0.92, 0))
    m.add(torus(0.4, 0.02, 24, 6), '#6f7782', mat='metal', t=(0, 0.94, 0))
    for i in range(4):
        m.add(box(0.36, 0.008, 0.1), '#3a3f47', t=(0, 0.92, 0), r=(18, i * 45, 0), group='fan')
    m.add(cylinder(0.06, 0.06, 0.04, 12), '#3a3f47', t=(0, 0.92, 0), group='fan')
    m.pivot('fan', (0, 0.92, 0))
    for sx in (1, -1):
        m.add(box(0.06, 0.06, 1.0), '#5d646e', mat='metal', t=(sx * 0.55, 0.03, 0))
    m.notes['note'] = 'Spin node "fan" around Y. Good parkour step (0.9m tall).'
    return m

@prop('props', 'rooftops')
def chimney():
    m = Model('chimney')
    m.add(box(0.7, 1.4, 0.7), '#a4513a', t=(0, 0.7, 0))
    for i in range(7):
        m.add(box(0.705, 0.02, 0.705), '#c9b8a6', t=(0, 0.1 + i * 0.2, 0))
    m.add(box(0.85, 0.12, 0.85), '#5f5f66', t=(0, 1.46, 0))
    m.add(box(0.5, 0.02, 0.5), '#1a1a1a', t=(0, 1.525, 0))
    return m

@prop('props', 'rooftops')
def water_tower():
    m = Model('water_tower')
    for sx in (1, -1):
        for sz in (1, -1):
            m.add(box(0.12, 3.0, 0.12), '#5b4636', t=(sx * 0.9, 1.5, sz * 0.9))
    for y in (0.9, 2.0):
        for r in (0, 90):
            m.add(box(1.9, 0.08, 0.08), '#5b4636', t=(0, y, 0), r=(0, r, 45))
    m.add(cylinder(1.25, 1.25, 2.2, 24, flat=True), '#9c6a43', t=(0, 4.1, 0))
    for y in (3.2, 3.9, 4.6):
        m.add(torus(1.26, 0.04, 24, 6), '#3a3a3f', mat='metal', t=(0, y, 0))
    m.add(cone(1.4, 1.0, 24, flat=True), '#6b4a33', t=(0, 5.7, 0))
    m.add(cylinder(1.35, 1.35, 0.1, 24), '#3a3a3f', t=(0, 3.0, 0))
    return m

@prop('props', 'rooftops')
def antenna():
    m = Model('antenna')
    m.add(cylinder(0.03, 0.04, 3.0, 8), '#a0a6ae', mat='metal', t=(0, 1.5, 0))
    for i, y in enumerate((1.6, 2.1, 2.6)):
        m.add(cylinder(0.012, 0.012, 1.0 - i * 0.2, 6), '#a0a6ae', mat='metal', t=(0, y, 0), r=(0, 0, 90))
    m.add(sphere(0.06, 10, 6), '#ff2a2a', mat='glow', t=(0, 3.03, 0), group='beacon')
    m.add(cylinder(0.25, 0.25, 0.05, 12), '#5d646e', t=(0, 0.025, 0))
    return m

@prop('props', 'rooftops')
def skylight():
    m = Model('skylight')
    m.add(box(1.4, 0.3, 1.4), '#8b929c', mat='metal', t=(0, 0.15, 0))
    m.add(cone(0.97, 0.55, 4, flat=True), '#cfe9ff', mat='glass', t=(0, 0.575, 0), r=(0, 45, 0))
    return m

@prop('props', 'rooftops')
def vent_pipe():
    m = Model('vent_pipe')
    m.add(cylinder(0.12, 0.12, 0.8, 14), '#a0a6ae', mat='metal', t=(0, 0.4, 0))
    m.add(lathe([(0.0001, 0.82), (0.25, 0.82), (0.25, 0.86), (0.0001, 1.0)], 14), '#a0a6ae', mat='metal')
    return m

@prop('props', 'rooftops')
def satellite_dish():
    m = Model('satellite_dish')
    m.add(cylinder(0.03, 0.03, 0.8, 8), '#9aa0aa', mat='metal', t=(0, 0.4, 0))
    m.add(lathe([(0.0001, 0), (0.25, 0.05), (0.42, 0.16), (0.4, 0.17), (0.24, 0.07), (0.0001, 0.02)], 20), '#e9ebee', mat='satin', t=(0, 0.85, 0.05), r=(60, 0, 0))
    m.add(cylinder(0.01, 0.01, 0.4, 6), '#666666', t=(0, 0.95, 0.25), r=(60, 0, 0))
    m.add(box(0.06, 0.06, 0.08), '#444444', t=(0, 1.0, 0.42))
    return m

@prop('props', 'rooftops')
def rooftop_door():
    m = Model('rooftop_door')
    m.add(box(1.6, 2.5, 1.8), '#b7aa98', t=(0, 1.25, 0))
    m.add(box(1.8, 0.12, 2.0), '#5f5f66', t=(0, 2.56, 0))
    m.add(box(0.9, 2.0, 0.05), '#6a7f5a', mat='satin', t=(0, 1.0, 0.91))
    m.add(sphere(0.04, 8, 6), '#d9b84a', mat='metal', t=(0.3, 1.0, 0.95))
    m.add(box(0.25, 0.12, 0.05), '#fffbe0', mat='glow', t=(0, 2.25, 0.92), group='light')
    return m

@prop('props', 'rooftops')
def plank():
    m = Model('plank')
    m.add(box(0.5, 0.06, 3.0), '#b08559', t=(0, 0.03, 0), flat=True)
    for z in (-1.2, 0, 1.2):
        m.add(box(0.52, 0.065, 0.05), '#8a6440', t=(0, 0.031, z))
    m.notes['note'] = '3m long along Z: bridge between rooftops (wobbles when stepped on, if you want).'
    return m

@prop('props', 'common')
def crate():
    m = Model('crate')
    m.add(box(0.8, 0.8, 0.8), '#c49a63', t=(0, 0.4, 0))
    for ax in range(3):
        for a in (1, -1):
            for b in (1, -1):
                s = [0.82, 0.82, 0.82]; s[ax] = 0.84
                t = [0, 0.4, 0]; o = [k for k in range(3) if k != ax]
                t[o[0]] += a * 0.36; t[o[1]] += b * 0.36
                dims = [0.08, 0.08, 0.08]; dims[ax] = 0.84
                m.add(box(*dims), '#8a6440', t=tuple(t))
    for f in ((0, 0.4, 0.41, 0), (0, 0.4, -0.41, 0)):
        m.add(box(1.0, 0.07, 0.02), '#8a6440', t=f[:3], r=(0, 0, 45))
    return m

@prop('props', 'rooftops')
def clothesline():
    m = Model('clothesline')
    for sx in (1, -1):
        m.add(cylinder(0.03, 0.03, 2.0, 8), '#9aa0aa', mat='metal', t=(sx * 2.0, 1.0, 0))
    m.add(tube([(-2.0, 1.9, 0), (-1, 1.78, 0), (0, 1.74, 0), (1, 1.78, 0), (2.0, 1.9, 0)], 0.008, 5), '#eeeeee')
    rnd = random.Random(2)
    items = [('#ff6b6b', 0.5, 0.6), ('#4dabf7', 0.35, 0.5), ('#ffd43b', 0.6, 0.4), ('#ffffff', 0.4, 0.55), ('#b197fc', 0.3, 0.3)]
    for i, (c, w, h) in enumerate(items):
        x = -1.5 + i * 0.75
        m.add(box(w, h, 0.02), c, t=(x, 1.76 - h / 2, 0), r=(0, rnd.uniform(-8, 8), rnd.uniform(-4, 4)), group='clothes')
    m.add(box(0.5, 0.18, 0.02), '#ff8cc6', t=(-1.5 + 4 * 0.75, 1.62, 0.0), group='clothes')  # undies, obviously
    return m

@prop('props', 'rooftops')
def billboard():
    m = Model('billboard')
    for sx in (1, -1):
        m.add(box(0.15, 3.0, 0.15), '#4a4f58', mat='metal', t=(sx * 1.8, 1.5, -0.1))
    m.add(box(4.4, 2.2, 0.1), '#2b2d33', t=(0, 3.9, 0))
    m.add(box(4.2, 2.0, 0.02), '#ffffff', t=(0, 3.9, 0.06), group='face')
    m.add(box(4.4, 0.08, 0.6), '#4a4f58', mat='metal', t=(0, 2.78, 0.3))
    for i in range(3):
        m.add(cone(0.12, 0.2, 10), '#30343c', t=(-1.4 + i * 1.4, 2.9, 0.4), r=(-120, 0, 0))
    m.notes['note'] = 'Node "face" is a 4.2x2.0 front panel: put a texture on it (see ui/textures/billboard_*.png).'
    return m

@prop('props', 'rooftops')
def wedding_arch():
    m = Model('wedding_arch')
    for sx in (1, -1):
        m.add(cylinder(0.06, 0.06, 1.8, 10), WHITE, t=(sx * 1.0, 0.9, 0))
    m.add(tube([(math.cos(math.pi * i / 16), 1.8 + math.sin(math.pi * i / 16), 0) for i in range(17)], 0.06, 8), WHITE)
    for sx in (1, -1):
        m.add(box(0.3, 0.06, 0.4), WHITE, t=(sx * 1.0, 0.03, 0))
    rnd = random.Random(7); cols = ['#ff7aa2', '#ffffff', '#ffb3c8', '#ff4f7f', '#fff0a0']
    for i in range(26):
        a = math.pi * i / 25
        m.add(sphere(0.07, 8, 6), cols[i % 5], t=(math.cos(a) * 1.0, 1.8 + math.sin(a) * 1.0, rnd.uniform(-0.05, 0.05)))
        if i % 2: m.add(sphere(0.06, 6, 4), '#4f8f3c', t=(math.cos(a) * 1.07, 1.8 + math.sin(a) * 1.07, 0.04), s=(1, 0.5, 1), flat=True)
    m.notes['note'] = 'Arch spans x=-1..1, top at y=2.86. The groom must be delivered here.'
    return m

@prop('props', 'rooftops')
def wedding_chair():
    m = Model('wedding_chair')
    legs4(m, 0.42, 0.42, 0.45, 0.015, WHITE, 0.03, 'satin', square=False)
    m.add(rbox(0.44, 0.04, 0.42, 0.015), WHITE, mat='satin', t=(0, 0.46, 0))
    for sx in (1, -1):
        m.add(cylinder(0.015, 0.015, 0.45, 8), WHITE, mat='satin', t=(sx * 0.19, 0.7, -0.19))
    for y in (0.75, 0.85):
        m.add(box(0.4, 0.04, 0.02), WHITE, mat='satin', t=(0, y, -0.19))
    m.add(torus(0.07, 0.02, 12, 6), '#ffd1dc', t=(0, 0.92, -0.19), r=(90, 0, 0))
    return m

@prop('props', 'rooftops')
def wedding_ring():
    m = Model('wedding_ring')
    m.add(torus(0.1, 0.022, 28, 10).transformed(r=(90, 0, 0)), '#f2c14e', mat='metal', t=(0, 0.12, 0))
    m.add(cone(0.045, 0.05, 8, flat=True), '#d9f6ff', mat='gloss', t=(0, 0.25, 0))
    m.add(cone(0.045, 0.03, 8, flat=True), '#d9f6ff', mat='gloss', t=(0, 0.29, 0), r=(180, 0, 0))
    m.notes['note'] = 'Oversized (~0.3m) on purpose: it is a held/pickup item. Spin it + bob it.'
    return m

@prop('props', 'rooftops')
def building_trim():
    m = Model('building_trim')
    m.add(box(4.0, 0.3, 0.3), '#d6cfc4', t=(0, 0.15, 0))
    m.add(box(4.0, 0.1, 0.4), '#bdb4a7', t=(0, 0.35, 0.02))
    m.notes['note'] = '4m roof-edge parapet segment. Tile around building roofs (buildings themselves = textured boxes in code).'
    return m

# ====================================================================== PARK (L3)
@prop('props', 'park')
def tree_round():
    m = Model('tree_round')
    m.add(cylinder(0.14, 0.2, 1.8, 8, flat=True), '#7a5233', t=(0, 0.9, 0))
    for (x, y, z, r, c) in ((0, 2.4, 0, 1.0, '#4fa04a'), (0.6, 2.0, 0.2, 0.7, '#5bb556'), (-0.5, 2.1, -0.3, 0.75, '#3f8a3e'), (0.1, 3.0, 0.1, 0.65, '#69c463')):
        m.add(sphere(r, 9, 6), c, t=(x, y, z), flat=True)
    return m

@prop('props', 'park')
def tree_pine():
    m = Model('tree_pine')
    m.add(cylinder(0.12, 0.16, 1.0, 8, flat=True), '#6a4630', t=(0, 0.5, 0))
    for i, (r, h, y) in enumerate(((1.1, 1.4, 1.4), (0.85, 1.2, 2.2), (0.6, 1.0, 2.9))):
        m.add(cone(r, h, 9, flat=True), ['#2f7d4a', '#3a8f56', '#47a362'][i], t=(0, y, 0))
    return m

@prop('props', 'park')
def bush():
    m = Model('bush')
    for (x, y, z, r) in ((0, 0.35, 0, 0.45), (0.4, 0.28, 0.1, 0.35), (-0.38, 0.3, -0.05, 0.38), (0.1, 0.3, 0.35, 0.3)):
        m.add(sphere(r, 8, 6), '#4a9a48', t=(x, y, z), flat=True)
    for i in range(5):
        a = i * 1.3
        m.add(sphere(0.05, 6, 4), '#ff5a7a', t=(math.cos(a) * 0.4, 0.45 + (i % 2) * 0.15, math.sin(a) * 0.35))
    return m

@prop('props', 'park')
def bench():
    m = Model('bench')
    for sx in (1, -1):
        m.add(box(0.06, 0.45, 0.5), '#2f3338', mat='metal', t=(sx * 0.75, 0.225, 0))
        m.add(box(0.06, 0.5, 0.06), '#2f3338', mat='metal', t=(sx * 0.75, 0.7, -0.22), r=(-12, 0, 0))
    for i in range(4):
        m.add(rbox(1.7, 0.035, 0.1, 0.01), '#b8763f', t=(0, 0.46, -0.17 + i * 0.115))
    for i in range(3):
        m.add(rbox(1.7, 0.1, 0.035, 0.01), '#b8763f', t=(0, 0.6 + i * 0.13, -0.23 - i * 0.02), r=(-12, 0, 0))
    return m

@prop('props', 'park')
def lamp_post():
    m = Model('lamp_post')
    m.add(cylinder(0.12, 0.15, 0.3, 10), '#2f3338', mat='metal', t=(0, 0.15, 0))
    m.add(cylinder(0.05, 0.06, 3.0, 10), '#2f3338', mat='metal', t=(0, 1.8, 0))
    m.add(lathe([(0.0001, 3.24), (0.13, 3.24), (0.13, 3.3), (0.0001, 3.3)], 6), '#2f3338', mat='metal')
    m.add(lathe([(0.24, 3.58), (0.24, 3.62), (0.12, 3.7), (0.0001, 3.82)], 6), '#2f3338', mat='metal')
    m.add(cylinder(0.14, 0.17, 0.3, 6), '#fff2b0', mat='glow', t=(0, 3.45, 0), group='bulb')
    return m

@prop('props', 'park')
def picnic_table():
    m = Model('picnic_table')
    for i in range(5):
        m.add(box(1.8, 0.05, 0.14), '#b8763f', t=(0, 0.74, -0.3 + i * 0.15))
    for sz in (1, -1):
        for i in range(2):
            m.add(box(1.8, 0.05, 0.14), '#a8692f', t=(0, 0.44, sz * (0.62 + i * 0.15)))
    for sx in (1, -1):
        for a in (1, -1):
            m.add(box(0.08, 1.1, 0.08), '#8a5a2b', t=(sx * 0.7, 0.4, a * 0.27), r=(a * 38, 0, 0))
        m.add(box(0.08, 0.08, 1.6), '#8a5a2b', t=(sx * 0.7, 0.4, 0))
    m.add(box(0.6, 0.004, 0.6), '#e64545', t=(0.3, 0.768, 0))
    return m

@prop('props', 'park')
def trash_can():
    m = Model('trash_can')
    m.add(lathe([(0.0001, 0), (0.25, 0), (0.29, 0.9), (0.0001, 0.9)], 14), '#2f7d4a', mat='metal')
    for y in (0.2, 0.5, 0.8):
        m.add(torus(0.28, 0.015, 14, 4), '#245f39', mat='metal', t=(0, y, 0))
    m.add(lathe([(0.0001, 0.9), (0.31, 0.9), (0.3, 0.96), (0.15, 1.02), (0.0001, 1.04)], 14), '#245f39', mat='metal', group='lid')
    return m

@prop('props', 'park')
def fence_segment():
    m = Model('fence_segment')
    for i in range(8):
        x = -0.875 + i * 0.25
        m.add(box(0.1, 0.9, 0.03), '#f1ece2', t=(x, 0.45, 0))
        m.add(cone(0.071, 0.1, 4, flat=True), '#f1ece2', t=(x, 0.95, 0), r=(0, 45, 0), s=(1, 1, 0.3))
    for y in (0.25, 0.7):
        m.add(box(2.0, 0.08, 0.03), '#e3dccd', t=(0, y, -0.03))
    m.notes['note'] = '2m segment along X.'
    return m

@prop('props', 'common')
def rock():
    m = Model('rock')
    m.add(rock_geo(0.6, 3), '#9a9c9f', t=(0, 0.3, 0))
    m.add(rock_geo(0.3, 5), '#8a8c90', t=(0.55, 0.15, 0.2))
    return m

@prop('props', 'park')
def sticky_note():
    m = Model('sticky_note')
    m.add(box(0.1, 0.002, 0.1), '#ffe14d', t=(0, 0.001, 0))
    for i in range(3):
        m.add(box(0.07 - i * 0.015, 0.0025, 0.006), '#e8322f', t=(0, 0.0022, -0.025 + i * 0.022))
    m.notes['note'] = 'The "launch codes" (it just says password123). Real size; scale x3 for the beak.'
    return m

@prop('props', 'common')
def signpost():
    m = Model('signpost')
    m.add(box(0.1, 1.6, 0.1), '#7a5233', t=(0, 0.8, 0))
    m.add(rbox(1.2, 0.6, 0.06, 0.02), '#7a5233', t=(0, 1.5, 0.04))
    m.add(box(1.1, 0.5, 0.01), '#f6efe1', t=(0, 1.5, 0.075), group='face')
    m.notes['note'] = 'Node "face" (1.1x0.5) takes a texture e.g. ui/textures/sign_dont_feed_geese.png'
    return m

@prop('props', 'park')
def bread_loaf():
    m = Model('bread_loaf')
    m.add(rbox(0.3, 0.14, 0.14, 0.06), '#d9973f', mat='satin', t=(0, 0.07, 0))
    for i in range(3):
        m.add(box(0.02, 0.005, 0.1), '#a8642a', t=(-0.08 + i * 0.08, 0.142, 0), r=(0, 30, 0))
    m.notes['note'] = 'Goose bait / throwable lure.'
    return m

# ====================================================================== GRANDMA HOUSE (L4)
@prop('props', 'grandma')
def sofa():
    m = Model('sofa')
    C, D = '#b0708f', '#93587a'
    m.add(rbox(2.0, 0.3, 0.9, 0.05), D, t=(0, 0.3, 0))
    m.add(rbox(2.0, 0.6, 0.25, 0.08), C, t=(0, 0.7, -0.33))
    for sx in (1, -1):
        m.add(rbox(0.25, 0.55, 0.9, 0.08), C, t=(sx * 0.9, 0.5, 0))
        m.add(rbox(0.8, 0.16, 0.65, 0.06), C, t=(sx * 0.4, 0.52, 0.08))
        m.add(cone(0.04, 0.12, 6), '#4a3222', t=(sx * 0.9, 0.06, 0.35), r=(180, 0, 0))
        m.add(cone(0.04, 0.12, 6), '#4a3222', t=(sx * 0.9, 0.06, -0.35), r=(180, 0, 0))
    m.add(box(0.5, 0.004, 0.5), '#fff8ec', t=(0, 1.0, -0.3), r=(-80, 0, 45))   # doily
    m.add(rbox(0.4, 0.35, 0.12, 0.05), '#f2c94c', t=(0.55, 0.75, -0.12), r=(-15, 0, 10))
    return m

@prop('props', 'grandma')
def armchair():
    m = Model('armchair')
    C = '#6f8f6a'
    m.add(rbox(0.9, 0.3, 0.85, 0.05), '#5e7a5a', t=(0, 0.3, 0))
    m.add(rbox(0.9, 0.75, 0.22, 0.08), C, t=(0, 0.75, -0.32))
    for sx in (1, -1):
        m.add(rbox(0.2, 0.55, 0.85, 0.08), C, t=(sx * 0.38, 0.5, 0))
    m.add(rbox(0.55, 0.15, 0.62, 0.06), C, t=(0, 0.52, 0.08))
    m.add(box(0.3, 0.004, 0.3), '#fff8ec', t=(0, 1.13, -0.3), r=(-80, 0, 45))
    return m

@prop('props', 'grandma')
def crt_tv():
    m = Model('crt_tv')
    m.add(box(0.9, 0.45, 0.5), '#6b4a2f', t=(0, 0.225, 0))
    m.add(box(0.8, 0.3, 0.02), '#5a3d26', t=(0, 0.22, 0.25))
    m.add(rbox(0.75, 0.6, 0.55, 0.06), '#7a5a3a', mat='satin', t=(0, 0.76, -0.02))
    m.add(rbox(0.6, 0.45, 0.04, 0.03), '#222222', t=(-0.06, 0.78, 0.25))
    m.add(box(0.52, 0.38, 0.01), '#9ad7a0', mat='glow', t=(-0.06, 0.78, 0.272), group='screen')
    for i in range(2):
        m.add(cylinder(0.025, 0.025, 0.03, 10), '#cccccc', mat='metal', t=(0.3, 0.88 - i * 0.1, 0.26), r=(90, 0, 0))
    for sx in (1, -1):
        m.add(cylinder(0.006, 0.006, 0.55, 6), '#c0c0c0', mat='metal', t=(sx * 0.12, 1.28, -0.05), r=(0, 0, -sx * 30))
    m.add(sphere(0.05, 10, 6, 0, math.pi / 2), '#333333', t=(0, 1.06, -0.05))
    return m

@prop('props', 'grandma')
def router():
    m = Model('router')
    m.add(rbox(0.28, 0.05, 0.18, 0.02), '#1f2228', mat='satin', t=(0, 0.025, 0))
    for sx in (1, -1):
        m.add(cylinder(0.008, 0.01, 0.2, 8), '#1f2228', t=(sx * 0.11, 0.15, -0.08), r=(0, 0, -sx * 10))
    for i, (g, c) in enumerate((('led_power', '#36ff6b'), ('led_wifi', '#36ff6b'), ('led_internet', '#ff8a1f'))):
        m.add(box(0.016, 0.008, 0.005), c, mat='glow', t=(-0.05 + i * 0.05, 0.03, 0.092), group=g)
    m.add(tube([(0.05, 0.02, -0.09), (0.08, 0.02, -0.25), (0.1, 0.01, -0.4)], 0.006, 5), '#111111')
    m.notes['note'] = 'Blink led_* nodes (swap emissive). Mission: unplug, wait 10s, plug back in. Comes with power_plug + wall_outlet.'
    return m

@prop('props', 'grandma')
def wall_outlet():
    m = Model('wall_outlet')
    m.add(rbox(0.08, 0.12, 0.012, 0.005), '#f2efe6', t=(0, 0.3, 0.006))
    for y in (0.27, 0.33):
        for sx in (1, -1):
            m.add(box(0.006, 0.015, 0.004), '#222222', t=(sx * 0.012, y, 0.013))
    m.notes['note'] = 'Mount on wall (face +Z). Socket centre at y=0.3.'
    return m

@prop('props', 'grandma')
def power_plug():
    m = Model('power_plug')
    m.add(rbox(0.04, 0.05, 0.035, 0.008), '#111111', t=(0, 0, 0.02))
    for sx in (1, -1):
        m.add(box(0.005, 0.012, 0.02), '#d9b84a', mat='metal', t=(sx * 0.012, 0, -0.008))
    m.add(tube([(0, 0, 0.04), (0, -0.02, 0.1), (0, -0.1, 0.15)], 0.005, 5), '#111111')
    m.notes['note'] = 'Prongs face -Z, origin at prong base. Interactable.'
    return m

@prop('props', 'grandma')
def bookshelf():
    m = Model('bookshelf')
    m.add(box(1.0, 1.9, 0.04), '#7a5233', t=(0, 0.95, -0.15))
    for sx in (1, -1):
        m.add(box(0.04, 1.9, 0.34), '#8a6440', t=(sx * 0.48, 0.95, 0))
    rnd = random.Random(11); cols = ['#c0392b', '#2e86de', '#27ae60', '#f39c12', '#8e44ad', '#16a085', '#d35400', '#ecf0f1']
    for k in range(5):
        y = 0.02 + k * 0.45
        m.add(box(0.96, 0.03, 0.32), '#8a6440', t=(0, y, 0))
        if k == 4: break
        x = -0.42
        while x < 0.4:
            w = rnd.uniform(0.035, 0.07); h = rnd.uniform(0.25, 0.36)
            m.add(box(w, h, 0.24), rnd.choice(cols), t=(x + w / 2, y + 0.015 + h / 2, 0.02), r=(0, 0, rnd.choice([0, 0, 0, 0, 8])))
            x += w + 0.004
    return m

@prop('props', 'common')
def floor_lamp():
    m = Model('floor_lamp')
    m.add(cylinder(0.18, 0.2, 0.04, 16), '#c9a24a', mat='metal', t=(0, 0.02, 0))
    m.add(cylinder(0.015, 0.015, 1.45, 8), '#c9a24a', mat='metal', t=(0, 0.75, 0))
    m.add(sphere(0.06, 10, 8), '#fff3c4', mat='glow', t=(0, 1.45, 0), group='bulb')
    m.add(lathe([(0.25, 1.35), (0.14, 1.7), (0.13, 1.7), (0.24, 1.35)], 16), '#f7e7c6', mat='satin')
    return m

@prop('props', 'grandma')
def soup_bowl():
    m = Model('soup_bowl')
    m.add(lathe([(0.0001, 0), (0.06, 0), (0.11, 0.07), (0.1, 0.075), (0.0001, 0.02)], 18), '#f4f2ec', mat='gloss')
    m.add(torus(0.1, 0.006, 20, 4), '#5a8ed8', t=(0, 0.06, 0))
    m.add(cylinder(0.095, 0.095, 0.004, 18), '#e8963a', mat='satin', t=(0, 0.06, 0), group='soup')
    for i in range(4):
        m.add(box(0.015, 0.008, 0.015), ['#ff6a3d', '#64c26a', '#f2d16b', '#ff6a3d'][i], t=(-0.04 + i * 0.025, 0.064, (i % 2) * 0.03 - 0.015))
    m.add(cylinder(0.006, 0.006, 0.17, 6), '#c9c9cf', mat='metal', t=(0.05, 0.1, 0), r=(0, 0, -55))
    m.add(sphere(0.022, 8, 4, math.pi / 2, math.pi), '#c9c9cf', mat='metal', t=(-0.015, 0.065, 0), s=(1, 0.5, 1.3))
    return m

@prop('props', 'common')
def side_table():
    m = Model('side_table')
    m.add(cylinder(0.3, 0.3, 0.04, 20), '#8a5a3b', mat='satin', t=(0, 0.6, 0))
    m.add(cylinder(0.035, 0.05, 0.56, 10), '#8a5a3b', t=(0, 0.3, 0))
    m.add(cylinder(0.2, 0.22, 0.04, 16), '#8a5a3b', t=(0, 0.02, 0))
    m.add(cylinder(0.25, 0.25, 0.003, 20), '#fff8ec', t=(0, 0.622, 0))
    return m

@prop('props', 'grandma')
def rug():
    m = Model('rug')
    for i, (r, c) in enumerate(((1.4, '#8d3b4a'), (1.15, '#d9a441'), (0.9, '#3d5a80'), (0.55, '#d9a441'), (0.3, '#8d3b4a'))):
        m.add(cylinder(r, r, 0.01, 32), c, t=(0, 0.005 + i * 0.001, 0), s=(1, 1, 0.7))
    return m

@prop('props', 'grandma')
def kitchen_counter():
    m = Model('kitchen_counter')
    m.add(box(2.0, 0.86, 0.6), '#e6dcc8', t=(0, 0.43, 0))
    m.add(rbox(2.04, 0.05, 0.64, 0.01), '#b2a48c', mat='satin', t=(0, 0.885, 0.01))
    for i in range(4):
        x = -0.75 + i * 0.5
        m.add(box(0.46, 0.7, 0.02), '#cfc2a8', t=(x, 0.42, 0.305))
        m.add(rbox(0.12, 0.02, 0.03, 0.008), '#b08a4a', mat='metal', t=(x, 0.7, 0.325))
    m.add(box(0.5, 0.04, 0.36), '#9aa0aa', mat='metal', t=(0.5, 0.9, 0.0))
    m.add(tube([(0.5, 0.91, -0.22), (0.5, 1.15, -0.22), (0.5, 1.18, -0.1)], 0.015, 8), '#c9c9cf', mat='metal')
    for i, c in enumerate(('#ff6b6b', '#ffd43b', '#69db7c')):
        m.add(lathe([(0.0001, 0), (0.06, 0), (0.07, 0.15), (0.03, 0.2), (0.0001, 0.2)], 10), c, mat='gloss', t=(-0.75 + i * 0.16, 0.91, -0.18))
    return m

@prop('props', 'grandma')
def stove():
    m = Model('stove')
    m.add(box(0.76, 0.9, 0.65), WHITE, mat='satin', t=(0, 0.45, 0))
    m.add(box(0.6, 0.35, 0.02), '#222222', mat='gloss', t=(0, 0.45, 0.33))
    m.add(box(0.6, 0.03, 0.03), '#c9c9cf', mat='metal', t=(0, 0.68, 0.35))
    for sx in (1, -1):
        for sz in (1, -1):
            m.add(torus(0.09, 0.012, 16, 4), '#333333', t=(sx * 0.18, 0.905, sz * 0.15))
    for i in range(4):
        m.add(cylinder(0.025, 0.025, 0.03, 10), '#333333', t=(-0.27 + i * 0.18, 0.8, 0.335), r=(90, 0, 0))
    # soup pot (grandma's infinite soup)
    m.add(lathe([(0.0001, 0.91), (0.17, 0.91), (0.18, 1.15), (0.17, 1.15), (0.16, 0.93), (0.0001, 0.93)], 18), '#9aa0aa', mat='metal', t=(-0.18, 0, 0.15))
    m.add(cylinder(0.165, 0.165, 0.005, 18), '#e8963a', t=(-0.18, 1.1, 0.15), group='soup')
    for sx in (1, -1):
        m.add(torus(0.035, 0.01, 10, 4), '#333333', t=(-0.18 + sx * 0.2, 1.1, 0.15), r=(90, 0, 0))
    m.add(box(0.15, 0.04, 0.04), '#ff4d2e', mat='glow', t=(0.18, 0.92, 0.15), r=(0, 0, 0), group='burner_glow')
    return m

@prop('props', 'grandma')
def fridge():
    m = Model('fridge')
    m.add(rbox(0.75, 1.8, 0.7, 0.05), '#f4f2ec', mat='satin', t=(0, 0.9, 0))
    m.add(rbox(0.74, 1.15, 0.05, 0.02), '#ecebe5', mat='satin', t=(0, 0.6, 0.37), group='door_low')
    m.add(rbox(0.74, 0.6, 0.05, 0.02), '#ecebe5', mat='satin', t=(0, 1.5, 0.37), group='door_top')
    for g, y in (('door_low', 0.9), ('door_top', 1.35)):
        m.add(box(0.03, 0.3, 0.04), '#c9c9cf', mat='metal', t=(0.3, y, 0.41), group=g)
    for i, c in enumerate(('#ff6b6b', '#4dabf7', '#ffd43b')):
        m.add(box(0.08, 0.06, 0.01), c, t=(-0.15 + i * 0.12, 1.55 - (i % 2) * 0.1, 0.4), group='door_top')
    m.add(box(0.2, 0.25, 0.004), WHITE, t=(-0.05, 0.95, 0.398), r=(0, 0, 3), group='door_low')
    m.pivot('door_low', (-0.37, 0, 0.37)); m.pivot('door_top', (-0.37, 0, 0.37))
    return m

@prop('props', 'grandma')
def framed_picture():
    m = Model('framed_picture')
    m.add(rbox(0.5, 0.6, 0.04, 0.012), '#b08a4a', mat='metal', t=(0, 0.3, 0.02))
    m.add(box(0.42, 0.52, 0.005), '#e9d9b5', t=(0, 0.3, 0.042), group='canvas')
    m.notes['note'] = 'Wall-mounted, back at z=0. Put a texture on node "canvas" (ui/textures/portrait_*.png).'
    return m

@prop('props', 'common')
def vase_flowers():
    m = Model('vase_flowers')
    m.add(lathe([(0.0001, 0), (0.06, 0), (0.1, 0.12), (0.05, 0.25), (0.06, 0.28), (0.0001, 0.27)], 16, smooth_profile=True), '#3d78c4', mat='gloss')
    rnd = random.Random(9)
    for i in range(6):
        a = i * 60; dx, dz = math.cos(math.radians(a)) * 0.07, math.sin(math.radians(a)) * 0.07
        m.add(tube([(0, 0.25, 0), (dx * 0.5, 0.4, dz * 0.5), (dx, 0.5 + rnd.uniform(0, 0.1), dz)], 0.006, 4), '#3c8c3c')
        m.add(sphere(0.04, 8, 6), ['#ff7aa2', '#ffd43b', '#ffffff'][i % 3], t=(dx, 0.52 + rnd.uniform(0, 0.1), dz))
    return m

@prop('props', 'grandma')
def yarn_ball():
    m = Model('yarn_ball')
    m.add(sphere(0.08, 12, 8), '#e64980', t=(0, 0.08, 0))
    for r in (0, 50, 100, 140):
        m.add(torus(0.081, 0.006, 20, 4), '#c2255c', t=(0, 0.08, 0), r=(r, r * 0.7, 0))
    m.add(tube([(0.07, 0.03, 0.03), (0.2, 0.0, 0.1), (0.35, 0.005, 0.0)], 0.005, 4), '#e64980')
    return m

# ====================================================================== PARTY (L5)
@prop('props', 'party')
def birthday_cake():
    m = Model('birthday_cake')
    m.add(cylinder(0.35, 0.35, 0.22, 28), '#ffe3ef', mat='satin', t=(0, 0.11, 0))
    m.add(cylinder(0.25, 0.25, 0.18, 28), '#fff3d6', mat='satin', t=(0, 0.31, 0))
    m.add(cylinder(0.4, 0.4, 0.02, 28), '#e9ecef', mat='gloss', t=(0, 0.01, 0))
    for i in range(18):
        a = i * 20
        m.add(sphere(0.035, 8, 6), '#ff8cc6', t=(math.cos(math.radians(a)) * 0.35, 0.22, math.sin(math.radians(a)) * 0.35))
    for i in range(14):
        a = i * 360 / 14
        m.add(sphere(0.028, 8, 6), '#9be7ff', t=(math.cos(math.radians(a)) * 0.25, 0.4, math.sin(math.radians(a)) * 0.25))
    rnd = random.Random(5)
    for i in range(30):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(0, 0.22)
        m.add(box(0.025, 0.008, 0.008), rnd.choice(['#ff5a5a', '#ffd43b', '#4dabf7', '#69db7c']), t=(math.cos(a) * r, 0.402, math.sin(a) * r), r=(0, rnd.uniform(0, 180), 0))
    for i in range(5):
        a = i * 72; x, z = math.cos(math.radians(a)) * 0.13, math.sin(math.radians(a)) * 0.13
        m.add(cylinder(0.012, 0.012, 0.12, 8), ['#ff5a5a', '#4dabf7', '#ffd43b', '#69db7c', '#b197fc'][i], t=(x, 0.46, z))
        m.add(cone(0.016, 0.05, 8), '#ffb02e', mat='glow', t=(x, 0.545, z), group='flames')
    m.notes['note'] = 'Flicker node "flames" (scale.y). The objective in L5: protect this cake.'
    return m

@prop('props', 'party')
def party_table():
    m = Model('party_table')
    m.add(cylinder(0.6, 0.6, 0.04, 24), WHITE, t=(0, 0.74, 0))
    m.add(lathe([(0.62, 0.45), (0.62, 0.76), (0.0001, 0.765)], 24), '#ff8cc6', mat='satin')
    m.add(cylinder(0.04, 0.04, 0.72, 8), '#9aa0aa', mat='metal', t=(0, 0.36, 0))
    m.add(cylinder(0.3, 0.3, 0.02, 16), '#9aa0aa', mat='metal', t=(0, 0.01, 0))
    for i in range(4):
        a = i * 90 + 30
        m.add(lathe([(0.0001, 0), (0.03, 0), (0.035, 0.09), (0.0001, 0.09)], 10), ['#ff5a5a', '#4dabf7', '#ffd43b', '#69db7c'][i], mat='gloss',
              t=(math.cos(math.radians(a)) * 0.4, 0.765, math.sin(math.radians(a)) * 0.4))
    return m

@prop('props', 'party')
def gift_box():
    m = Model('gift_box', tint_groups=('wrap',))
    m.add(box(0.4, 0.3, 0.4), '#4dabf7', t=(0, 0.15, 0), group='wrap')
    m.add(box(0.44, 0.08, 0.44), '#4dabf7', t=(0, 0.32, 0), group='wrap')
    m.add(box(0.07, 0.36, 0.41), '#ffd43b', mat='satin', t=(0, 0.18, 0))
    m.add(box(0.41, 0.36, 0.07), '#ffd43b', mat='satin', t=(0, 0.18, 0))
    for sx in (1, -1):
        m.add(torus(0.07, 0.02, 12, 6), '#ffd43b', mat='satin', t=(sx * 0.07, 0.4, 0), r=(90, 0, sx * 30), s=(1, 1, 0.6))
    return m

@prop('props', 'party')
def balloon_plain():
    m = Model('balloon_plain', tint_groups=('balloon',))
    m.add(sphere(0.18, 16, 12), '#ff5a5a', mat='gloss', t=(0, 1.55, 0), s=(1, 1.2, 1), group='balloon')
    m.add(cone(0.03, 0.04, 8), '#ff5a5a', mat='gloss', t=(0, 1.32, 0), group='balloon')
    m.add(tube([(0, 1.3, 0), (0.03, 1.0, 0.02), (-0.02, 0.6, 0), (0.0, 0.0, 0.0)], 0.003, 4, caps=False), '#dddddd')
    return m

@prop('props', 'party')
def party_hat():
    m = Model('party_hat', tint_groups=('hat',))
    m.add(cone(0.08, 0.22, 18), '#b197fc', mat='satin', t=(0, 0.11, 0), group='hat')
    for y in (0.04, 0.1, 0.16):
        m.add(torus(0.08 * (1 - y / 0.22), 0.006, 18, 4), '#ffd43b', t=(0, y, 0))
    m.add(sphere(0.025, 8, 6), '#ffd43b', t=(0, 0.225, 0))
    return m

@prop('props', 'party')
def cupcake():
    m = Model('cupcake')
    m.add(lathe([(0.0001, 0), (0.04, 0), (0.05, 0.05), (0.0001, 0.05)], 12, smooth_profile=False), '#4dabf7', t=(0, 0, 0))
    m.add(lathe([(0.055, 0.05), (0.05, 0.08), (0.035, 0.1), (0.01, 0.125), (0.0001, 0.13)], 12, smooth_profile=True), '#ffd6e8', mat='satin')
    m.add(sphere(0.014, 8, 6), '#e03131', mat='gloss', t=(0, 0.14, 0))
    return m

@prop('props', 'party')
def bouncy_castle():
    m = Model('bouncy_castle')
    m.add(rbox(4.0, 0.5, 4.0, 0.2), '#ff5a5a', mat='satin', t=(0, 0.25, 0))
    for sx in (1, -1):
        for sz in (1, -1):
            m.add(capsule(0.35, 1.8, 14), '#4dabf7', mat='satin', t=(sx * 1.8, 1.3, sz * 1.8))
            m.add(cone(0.4, 0.6, 14), '#ffd43b', mat='satin', t=(sx * 1.8, 2.75, sz * 1.8))
    for sx in (1, -1):
        m.add(rbox(0.3, 1.2, 3.2, 0.12), '#ffd43b', mat='satin', t=(sx * 1.8, 1.1, 0))
    m.add(rbox(3.2, 1.2, 0.3, 0.12), '#ffd43b', mat='satin', t=(0, 1.1, -1.8))
    m.add(rbox(1.2, 0.8, 0.3, 0.12), '#69db7c', mat='satin', t=(0, 1.75, -1.8))
    m.notes['note'] = '4x4m, open front (+Z). Players can jump in it for a super-bounce.'
    return m

# ====================================================================== BEDROOM (L6) - real-world scale; scale x8 in game ("you shrank")
@prop('props', 'bedroom')
def bed():
    m = Model('bed')
    m.add(box(1.6, 0.3, 2.1), '#8a5a3b', t=(0, 0.25, 0))
    m.add(rbox(1.55, 0.25, 2.0, 0.08), WHITE, mat='satin', t=(0, 0.52, 0))
    m.add(rbox(1.62, 0.12, 1.5, 0.06), '#4c6ef5', mat='satin', t=(0, 0.66, 0.3), r=(0, 0, 0))
    m.add(rbox(1.64, 0.4, 0.06, 0.03), '#4c6ef5', mat='satin', t=(0, 0.48, 1.05))
    for sx in (1, -1):
        m.add(rbox(0.06, 0.4, 1.5, 0.03), '#4c6ef5', mat='satin', t=(sx * 0.8, 0.48, 0.3))
    m.add(box(1.7, 1.1, 0.08), '#8a5a3b', t=(0, 0.55, -1.05))
    for sx in (1, -1):
        m.add(rbox(0.6, 0.15, 0.4, 0.07), '#f8f9fa', mat='satin', t=(sx * 0.38, 0.72, -0.75))
    return m

@prop('props', 'bedroom')
def nightstand():
    m = Model('nightstand')
    m.add(box(0.5, 0.55, 0.42), '#a87b52', t=(0, 0.3, 0))
    m.add(box(0.46, 0.2, 0.02), '#9a6d45', t=(0, 0.4, 0.215))
    m.add(sphere(0.02, 8, 6), '#d9b84a', mat='metal', t=(0, 0.4, 0.23))
    legs4(m, 0.5, 0.42, 0.04, 0.02, '#7a5233', 0.04, 'matte')
    return m

@prop('props', 'bedroom')
def slipper():
    m = Model('slipper')
    m.add(rbox(0.11, 0.03, 0.28, 0.014), '#e8d9c4', t=(0, 0.015, 0))
    m.add(sphere(0.07, 12, 8, 0, math.pi / 2), '#ff9cc0', t=(0, 0.03, 0.06), s=(0.8, 0.9, 1.3))
    for sx in (1, -1):
        m.add(sphere(0.02, 8, 6), '#ff9cc0', t=(sx * 0.03, 0.09, 0.1))
        m.add(sphere(0.008, 6, 4), '#111111', t=(sx * 0.025, 0.08, 0.135))
    return m

@prop('props', 'bedroom')
def book_stack():
    m = Model('book_stack')
    rnd = random.Random(3); y = 0
    for i in range(4):
        h = rnd.uniform(0.03, 0.05)
        m.add(rbox(0.22, h, 0.15, 0.004), ['#c0392b', '#2e86de', '#27ae60', '#f39c12'][i], t=(rnd.uniform(-0.015, 0.015), y + h / 2, 0), r=(0, rnd.uniform(-12, 12), 0))
        m.add(box(0.21, h * 0.8, 0.005), '#fffbea', t=(0, y + h / 2, 0.075))
        y += h
    return m

@prop('props', 'bedroom')
def phone():
    m = Model('phone')
    m.add(rbox(0.075, 0.009, 0.155, 0.004), '#1a1b1f', mat='gloss', t=(0, 0.0045, 0))
    m.add(box(0.068, 0.002, 0.145), '#6ab0ff', mat='glow', t=(0, 0.0095, 0), group='screen')
    m.notes['note'] = 'Lying flat, screen up. Glow it with notifications (they are the boss projectiles in L6).'
    return m

@prop('props', 'bedroom')
def pillow():
    m = Model('pillow')
    m.add(rbox(0.6, 0.14, 0.4, 0.07, 3), '#f8f9fa', mat='satin', t=(0, 0.07, 0))
    m.notes['note'] = 'Also the Pillow Cannon projectile (scale 0.35).'
    return m

@prop('props', 'bedroom')
def sock():
    m = Model('sock')
    m.add(tube([(0, 0.02, -0.12), (0, 0.02, 0.0), (0, 0.03, 0.06), (0, 0.06, 0.1), (0, 0.18, 0.1)], 0.035, 10), '#ffffff', mat='matte')
    m.add(torus(0.035, 0.008, 12, 4), '#e8322f', t=(0, 0.16, 0.1))
    return m

# ====================================================================== PICKUPS
@prop('props', 'pickup')
def coffee_cup():
    m = Model('coffee_cup')
    m.add(lathe([(0.0001, 0), (0.035, 0), (0.045, 0.13), (0.0001, 0.13)], 14), WHITE)
    m.add(cylinder(0.044, 0.044, 0.05, 14, caps=False), '#8a5a3b', t=(0, 0.06, 0), s=(1.01, 1, 1.01))
    m.add(lathe([(0.048, 0.125), (0.048, 0.145), (0.03, 0.155), (0.0001, 0.155)], 14), '#2b2d33')
    m.notes['note'] = 'Pickup: speed boost ("DOUBLE ESPRESSO"). Spin + bob.'
    return m

@prop('props', 'pickup')
def donut():
    m = Model('donut')
    m.add(torus(0.07, 0.035, 18, 10), '#d9973f', mat='satin', t=(0, 0.035, 0))
    m.add(torus(0.07, 0.036, 18, 10, ).transformed(s=(1, 0.6, 1)), '#ff8cc6', mat='gloss', t=(0, 0.047, 0))
    rnd = random.Random(1)
    for i in range(16):
        a = rnd.uniform(0, 6.28); r = 0.07 + rnd.uniform(-0.02, 0.02)
        m.add(box(0.012, 0.004, 0.004), rnd.choice(['#ff5a5a', '#ffd43b', '#4dabf7', '#ffffff']), t=(math.cos(a) * r, 0.071, math.sin(a) * r), r=(0, rnd.uniform(0, 180), 0))
    m.notes['note'] = 'Pickup: +1 health. Spin + bob.'
    return m

# ====================================================================== WEAPONS (first-person)
# Origin = right-hand grip. Barrel points -Z (camera forward). Marker "muzzle" = projectile spawn. "grip_L" = support-hand position.
@prop('weapons', 'L1')
def dart_pistol():
    m = Model('dart_pistol')
    T, O, Y = '#19b3a6', '#ff8a1f', '#ffd43b'
    m.add(rbox(0.06, 0.13, 0.08, 0.02), O, t=(0, -0.02, 0.01), r=(-15, 0, 0))
    m.add(rbox(0.07, 0.07, 0.3, 0.025), T, mat='satin', t=(0, 0.075, -0.08))
    m.add(cylinder(0.022, 0.022, 0.12, 14), Y, mat='satin', t=(0, 0.075, -0.27), r=(90, 0, 0))
    m.add(cylinder(0.014, 0.014, 0.01, 12), '#222222', t=(0, 0.075, -0.33), r=(90, 0, 0))
    m.add(rbox(0.04, 0.045, 0.06, 0.015), O, t=(0, 0.125, 0.04))
    m.add(box(0.008, 0.03, 0.04), '#333333', t=(0, 0.02, -0.03))
    m.add(torus(0.035, 0.008, 12, 4), O, t=(0, 0.02, -0.035), r=(0, 90, 0), s=(1, 1, 1))
    m.add(box(0.008, 0.02, 0.01), '#222222', t=(0, 0.12, -0.21))
    m.add(box(0.03, 0.02, 0.01), '#222222', t=(0, 0.125, 0.04))
    # dart sticking out (hide after firing until reload)
    m.add(cylinder(0.012, 0.012, 0.03, 10), '#ff3b5c', t=(0, 0.075, -0.345), r=(90, 0, 0), group='loaded_dart')
    m.marker('muzzle', (0, 0.075, -0.36)); m.marker('grip_L', (0, -0.02, -0.06))
    return m

@prop('weapons', 'L1')
def dart():
    m = Model('dart')
    m.add(cylinder(0.012, 0.012, 0.1, 10), '#3bc9db', t=(0, 0, 0.0), r=(90, 0, 0))
    m.add(lathe([(0.0001, 0), (0.02, 0.0), (0.012, 0.015), (0.0001, 0.015)], 12), '#ff3b5c', mat='gloss', t=(0, 0, -0.065), r=(-90, 0, 0))
    for i in range(3):
        m.add(box(0.002, 0.03, 0.03), '#ffd43b', t=(0, 0, 0.04), r=(0, 0, i * 60))
    m.notes['note'] = 'Tranquilliser foam dart: tip points -Z. Sticks to whatever it hits.'
    return m

@prop('weapons', 'L3')
def net_launcher():
    m = Model('net_launcher')
    G, D = '#5c940d', '#2b2d33'
    m.add(rbox(0.06, 0.14, 0.08, 0.02), D, t=(0, -0.03, 0.02), r=(-15, 0, 0))
    m.add(rbox(0.09, 0.09, 0.42, 0.03), G, mat='satin', t=(0, 0.07, -0.12))
    m.add(lathe([(0.04, 0), (0.09, 0.12), (0.085, 0.12), (0.035, 0.0)], 18), G, mat='satin', t=(0, 0.07, -0.33), r=(-90, 0, 0))
    m.add(cylinder(0.084, 0.084, 0.004, 18), '#e9e3d0', t=(0, 0.07, -0.445), r=(90, 0, 0), group='loaded_net')
    for i in range(4):
        a = i * 90 + 45
        m.add(sphere(0.016, 8, 6), '#ffd43b', mat='metal', t=(math.cos(math.radians(a)) * 0.075, 0.07 + math.sin(math.radians(a)) * 0.075, -0.44))
    m.add(rbox(0.05, 0.07, 0.12, 0.02), D, t=(0, -0.02, -0.18))
    m.add(box(0.12, 0.012, 0.012), '#ffd43b', t=(0, 0.125, -0.05))
    m.marker('muzzle', (0, 0.07, -0.46)); m.marker('grip_L', (0, -0.04, -0.18))
    return m

@prop('weapons', 'L3')
def net_projectile():
    m = Model('net_projectile')
    for i in range(7):
        a = i / 6 * math.pi
        pts = [(math.cos(a) * math.sin(t * math.pi / 2) * 0.6, math.sin(a) * math.sin(t * math.pi / 2) * 0.6, -math.cos(t * math.pi / 2) * 0.3) for t in (x / 6 for x in range(7))]
        pts2 = [(-p[0], -p[1], p[2]) for p in pts]
        m.add(tube(list(reversed(pts2))[:-1] + pts, 0.008, 4), '#e9e3d0')
    for k in range(1, 4):
        r = 0.6 * math.sin(k / 3 * math.pi / 2)
        m.add(torus(r, 0.008, 24, 4).transformed(r=(90, 0, 0)), '#e9e3d0', t=(0, 0, -math.cos(k / 3 * math.pi / 2) * 0.3))
    for i in range(4):
        a = i * 90 + 45
        m.add(sphere(0.04, 8, 6), '#ffd43b', mat='metal', t=(math.cos(math.radians(a)) * 0.6, math.sin(math.radians(a)) * 0.6, 0))
    m.notes['note'] = 'Opened net, flies along -Z. Scale from 0.1 to 1 over first 0.2s of flight. On hit, drape over target + play goose "Netted".'
    return m

@prop('weapons', 'L5')
def water_blaster():
    m = Model('water_blaster')
    P, B = '#7048e8', '#ffd43b'
    m.add(rbox(0.06, 0.14, 0.08, 0.02), B, t=(0, -0.03, 0.02), r=(-15, 0, 0))
    m.add(rbox(0.08, 0.08, 0.5, 0.03), P, mat='gloss', t=(0, 0.06, -0.12))
    m.add(cylinder(0.015, 0.02, 0.12, 12), B, mat='gloss', t=(0, 0.06, -0.42), r=(90, 0, 0))
    m.add(cylinder(0.07, 0.07, 0.24, 18), '#a5d8ff', mat='glass', t=(0, 0.17, -0.05), r=(90, 0, 0))
    m.add(cylinder(0.062, 0.062, 0.22, 16), '#339af0', mat='gloss', t=(0, 0.17, -0.05), r=(90, 0, 0), group='water_level')
    m.add(cylinder(0.03, 0.03, 0.04, 12), B, t=(0, 0.24, -0.05))
    m.add(rbox(0.07, 0.06, 0.14, 0.025), B, t=(0, 0.0, -0.26), group='pump')
    m.pivot('water_level', (0, 0.17, 0.06))
    m.marker('muzzle', (0, 0.06, -0.49)); m.marker('grip_L', (0, -0.01, -0.26))
    m.notes['note'] = 'Scale node "water_level" on Z (0..1) for ammo. Slide node "pump" +Z to pump.'
    return m

@prop('weapons', 'L6')
def pillow_cannon():
    m = Model('pillow_cannon')
    m.add(cylinder(0.12, 0.12, 0.7, 20), '#f783ac', mat='satin', t=(0, 0.1, -0.15), r=(90, 0, 0))
    m.add(torus(0.12, 0.025, 20, 8), '#fcc2d7', mat='satin', t=(0, 0.1, -0.5), r=(90, 0, 0))
    m.add(torus(0.12, 0.02, 20, 8), '#fcc2d7', mat='satin', t=(0, 0.1, 0.2), r=(90, 0, 0))
    for sx in (1, -1):
        m.add(sphere(0.03, 10, 6), '#fff0f6', t=(sx * 0.06, 0.22, -0.15))
    m.add(rbox(0.06, 0.14, 0.08, 0.02), '#a61e4d', t=(0, -0.06, 0.02), r=(-15, 0, 0))
    m.add(rbox(0.05, 0.12, 0.07, 0.02), '#a61e4d', t=(0, -0.04, -0.3))
    m.add(rbox(0.2, 0.1, 0.12, 0.05, 3), '#ffffff', mat='satin', t=(0, 0.1, -0.5), group='loaded_pillow')
    m.add(sphere(0.02, 8, 6), '#ffd43b', t=(0, 0.13, -0.42))
    m.add(rbox(0.04, 0.03, 0.05, 0.01), '#ffd43b', t=(0, 0.23, 0.05))
    m.marker('muzzle', (0, 0.1, -0.55)); m.marker('grip_L', (0, -0.04, -0.3))
    m.notes['note'] = 'Shoulder-mounted: hold lower/right. Projectile = props/pillow.glb scaled 0.35.'
    return m

@prop('weapons', 'all')
def fp_arms():
    m = Model('fp_arms')
    for side, sx in (('R', 1), ('L', -1)):
        g = 'arm_' + side; ox = 0.0 if side == 'R' else -0.25
        m.add(rbox(0.07, 0.085, 0.09, 0.03), '#3a3f47', t=(ox, 0, 0.015), group=g)            # glove palm
        for i in range(4):
            m.add(capsule(0.011, 0.035, 6, 3), '#3a3f47', t=(ox + sx * (-0.028 + i * 0.018), 0.0, -0.035), r=(90, 0, 0), group=g)
        m.add(capsule(0.012, 0.03, 6, 3), '#3a3f47', t=(ox - sx * 0.04, 0.02, -0.005), r=(60, 0, -sx * 40), group=g)
        m.add(cylinder(0.05, 0.045, 0.05, 12), '#2b2d33', t=(ox, 0, 0.08), r=(90, 0, 0), group=g)  # cuff
        m.add(tube([(ox, 0, 0.1), (ox + sx * 0.03, -0.06, 0.32), (ox + sx * 0.08, -0.16, 0.55)], 0.055, 12, radii=[0.05, 0.058, 0.065]), '#1c1f26', mat='satin', group=g)
        m.add(rbox(0.012, 0.05, 0.02, 0.004), '#e8c35a', mat='metal', t=(ox + sx * 0.035, 0.0, 0.115), group=g)  # cufflink, very professional
        m.pivot(g, (ox, 0, 0))
    m.notes['note'] = ('Black-suit gloved arms. Nodes "arm_R"/"arm_L" have origin at the palm; place arm_R at the weapon origin and arm_L '
                       'at the weapon "grip_L" marker (mirror pose is baked). Sleeves extend toward +Z (behind the camera).')
    return m


if __name__ == '__main__':
    for cat, level, fn in REG:
        emit(fn(), cat, level)
    for cat in MAN:
        with open(os.path.join(ROOT, '_manifest_%s.json' % cat), 'w') as f: json.dump(MAN[cat], f, indent=1)
