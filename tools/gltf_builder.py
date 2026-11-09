"""
Tiny dependency-free glTF 2.0 (.glb) builder for stylized low-poly assets.

- Primitives: box, rbox (rounded box), sphere, cylinder/cone, capsule, lathe, torus, tube
- Vertex-coloured materials (1 draw call per material per node)
- Static props (one node per group) or skinned characters (rigid skinning, 1 bone per part)
- Node TRS animations (quaternion slerp + translation)
- Marker empties (sockets / muzzles / weak points)

Conventions: metres, +Y up, models FACE +Z, feet / base at y = 0.
"""
import json, math, struct

# ----------------------------------------------------------------- colour utils
def _s2l(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def col(h):
    h = h.lstrip('#')
    return tuple(_s2l(int(h[i:i + 2], 16)) for i in (0, 2, 4))

# ----------------------------------------------------------------- math
def v_add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def v_sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def v_mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def v_dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def v_cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def v_len(a): return math.sqrt(v_dot(a, a))
def v_norm(a):
    l = v_len(a)
    return (0.0, 1.0, 0.0) if l < 1e-12 else (a[0] / l, a[1] / l, a[2] / l)

def quat_from_euler(rx, ry, rz):
    """Degrees, three.js 'XYZ' order."""
    x, y, z = math.radians(rx) / 2, math.radians(ry) / 2, math.radians(rz) / 2
    c1, c2, c3 = math.cos(x), math.cos(y), math.cos(z)
    s1, s2, s3 = math.sin(x), math.sin(y), math.sin(z)
    return (s1 * c2 * c3 + c1 * s2 * s3,
            c1 * s2 * c3 - s1 * c2 * s3,
            c1 * c2 * s3 + s1 * s2 * c3,
            c1 * c2 * c3 - s1 * s2 * s3)

def mat3_from_quat(q):
    x, y, z, w = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]

def m3v(m, v):
    return (m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
            m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
            m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2])

# ----------------------------------------------------------------- geometry
class Geo:
    """Indexed triangle soup with intended (outward) vertex normals."""
    def __init__(self):
        self.p, self.n, self.t = [], [], []

    def vert(self, p, n):
        self.p.append(tuple(p)); self.n.append(v_norm(n))
        return len(self.p) - 1

    def tri(self, a, b, c): self.t.append((a, b, c))
    def quad(self, a, b, c, d): self.t.append((a, b, c)); self.t.append((a, c, d))

    def merge(self, g):
        o = len(self.p)
        self.p += g.p; self.n += g.n
        self.t += [(a + o, b + o, c + o) for a, b, c in g.t]
        return self

    def transformed(self, t=(0, 0, 0), r=(0, 0, 0), s=(1, 1, 1)):
        q = quat_from_euler(*r); R = mat3_from_quat(q)
        g = Geo()
        for p, n in zip(self.p, self.n):
            ps = (p[0] * s[0], p[1] * s[1], p[2] * s[2])
            ns = (n[0] / s[0], n[1] / s[1], n[2] / s[2])
            g.p.append(v_add(m3v(R, ps), t)); g.n.append(v_norm(m3v(R, ns)))
        neg = (s[0] * s[1] * s[2]) < 0
        g.t = [(a, c, b) if neg else (a, b, c) for a, b, c in self.t]
        return g

    def flat(self):
        g = Geo()
        for a, b, c in self.t:
            pa, pb, pc = self.p[a], self.p[b], self.p[c]
            fn = v_norm(v_cross(v_sub(pb, pa), v_sub(pc, pa)))
            ref = v_add(v_add(self.n[a], self.n[b]), self.n[c])
            if v_dot(fn, ref) < 0: fn = v_mul(fn, -1)
            i = g.vert(pa, fn); j = g.vert(pb, fn); k = g.vert(pc, fn)
            g.tri(i, j, k)
        return g

    def fix_winding(self):
        out = []
        for a, b, c in self.t:
            pa, pb, pc = self.p[a], self.p[b], self.p[c]
            fn = v_cross(v_sub(pb, pa), v_sub(pc, pa))
            ref = v_add(v_add(self.n[a], self.n[b]), self.n[c])
            out.append((a, c, b) if v_dot(fn, ref) < 0 else (a, b, c))
        self.t = out
        return self


def box(w, h, d):
    g = Geo(); hx, hy, hz = w / 2, h / 2, d / 2
    faces = [((1, 0, 0), (0, 0, -1), (0, 1, 0)), ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
             ((0, 1, 0), (1, 0, 0), (0, 0, -1)), ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
             ((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (-1, 0, 0), (0, 1, 0))]
    for n, u, v in faces:
        c = (n[0] * hx, n[1] * hy, n[2] * hz)
        uu = (u[0] * hx, u[1] * hy, u[2] * hz); vv = (v[0] * hx, v[1] * hy, v[2] * hz)
        ids = [g.vert(v_add(v_add(c, v_mul(uu, su)), v_mul(vv, sv)), n) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        g.quad(*ids)
    return g.fix_winding()


def rbox(w, h, d, r=0.03, seg=None):
    """Rounded box with smooth bevels."""
    if seg is None: seg = 1 if r < 0.02 else 2
    H = (w / 2, h / 2, d / 2)
    r = min(r, *[x * 0.999 for x in H])
    def axis_vals(Hk):
        inner = Hk - r
        lo = [-inner - r * math.tan(math.radians(45 * k / seg)) for k in range(seg, 0, -1)]
        hi = [inner + r * math.tan(math.radians(45 * k / seg)) for k in range(1, seg + 1)]
        return lo + [-inner, inner] + hi
    vals = [axis_vals(Hk) for Hk in H]
    g = Geo()
    def emit(v):
        inner = tuple(max(-(H[k] - r), min(H[k] - r, v[k])) for k in range(3))
        nrm = v_norm(v_sub(v, inner))
        return g.vert(v_add(inner, v_mul(nrm, r)), nrm)
    for ax in range(3):
        a1, a2 = [k for k in range(3) if k != ax]
        for sgn in (-1, 1):
            grid = []
            for x in vals[a1]:
                row = []
                for y in vals[a2]:
                    v = [0, 0, 0]; v[ax] = sgn * H[ax]; v[a1] = x; v[a2] = y
                    row.append(emit(tuple(v)))
                grid.append(row)
            for i in range(len(grid) - 1):
                for j in range(len(grid[0]) - 1):
                    g.quad(grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1])
    return g.fix_winding()


def sphere(r=0.5, seg=16, rings=10, phi0=0.0, phi1=math.pi):
    g = Geo(); rows = []
    for i in range(rings + 1):
        phi = phi0 + (phi1 - phi0) * i / rings
        row = []
        for j in range(seg + 1):
            th = 2 * math.pi * j / seg
            n = (math.sin(phi) * math.cos(th), math.cos(phi), math.sin(phi) * math.sin(th))
            row.append(g.vert(v_mul(n, r), n))
        rows.append(row)
    for i in range(rings):
        for j in range(seg):
            g.quad(rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j])
    return g.fix_winding()


def lathe(profile, seg=16, smooth_profile=False, arc=2 * math.pi):
    """profile: list of (radius, y) ordered bottom -> top (outer surface)."""
    g = Geo()
    m = len(profile)
    seg_n = []
    for i in range(m - 1):
        (r0, y0), (r1, y1) = profile[i], profile[i + 1]
        seg_n.append(v_norm((y1 - y0, -(r1 - r0), 0)))  # (radial, y)
    def ring(r, y, nr, ny):
        ids = []
        for j in range(seg + 1):
            th = arc * j / seg
            c, s = math.cos(th), math.sin(th)
            ids.append(g.vert((r * c, y, r * s), (nr * c, ny, nr * s)))
        return ids
    if smooth_profile:
        rings = []
        for i in range(m):
            ns = [seg_n[k] for k in (i - 1, i) if 0 <= k < m - 1]
            n = v_norm((sum(x[0] for x in ns), sum(x[1] for x in ns), 0))
            rings.append(ring(profile[i][0], profile[i][1], n[0], n[1]))
        for i in range(m - 1):
            for j in range(seg):
                g.quad(rings[i][j], rings[i + 1][j], rings[i + 1][j + 1], rings[i][j + 1])
    else:
        for i in range(m - 1):
            n = seg_n[i]
            a = ring(profile[i][0], profile[i][1], n[0], n[1])
            b = ring(profile[i + 1][0], profile[i + 1][1], n[0], n[1])
            for j in range(seg):
                g.quad(a[j], b[j], b[j + 1], a[j + 1])
    return g.fix_winding()


def cylinder(rt=0.5, rb=0.5, h=1.0, seg=16, caps=True, flat=False):
    prof = []
    if caps and rb > 0: prof.append((0, -h / 2))
    prof += [(rb, -h / 2), (rt, h / 2)]
    if caps and rt > 0: prof.append((0, h / 2))
    g = lathe(prof, seg)
    return g.flat() if flat else g


def cone(r=0.5, h=1.0, seg=16, flat=False):
    return cylinder(0.0001, r, h, seg, True, flat)


def capsule(r=0.25, h=0.5, seg=14, rings=6):
    """Total height h + 2r, centred."""
    prof = []
    for i in range(rings + 1):
        a = -math.pi / 2 + (math.pi / 2) * i / rings
        prof.append((r * math.cos(a), -h / 2 + r * math.sin(a)))
    for i in range(rings + 1):
        a = (math.pi / 2) * i / rings
        prof.append((r * math.cos(a), h / 2 + r * math.sin(a)))
    prof[0] = (0.0001, prof[0][1]); prof[-1] = (0.0001, prof[-1][1])
    return lathe(prof, seg, smooth_profile=True)


def torus(R=0.5, r=0.1, seg=24, tseg=10):
    g = Geo(); rows = []
    for i in range(seg + 1):
        u = 2 * math.pi * i / seg
        row = []
        for j in range(tseg + 1):
            v = 2 * math.pi * j / tseg
            cx, cz = R * math.cos(u), R * math.sin(u)
            n = (math.cos(v) * math.cos(u), math.sin(v), math.cos(v) * math.sin(u))
            row.append(g.vert((cx + r * n[0], r * n[1], cz + r * n[2]), n))
        rows.append(row)
    for i in range(seg):
        for j in range(tseg):
            g.quad(rows[i][j], rows[i + 1][j], rows[i + 1][j + 1], rows[i][j + 1])
    return g.fix_winding()


def tube(points, r=0.05, seg=8, caps=True, radii=None):
    """Sweep a circle along a polyline."""
    g = Geo(); n = len(points); rings = []
    up = (0, 1, 0)
    for i, p in enumerate(points):
        if i == 0: t = v_sub(points[1], p)
        elif i == n - 1: t = v_sub(p, points[i - 1])
        else: t = v_sub(points[i + 1], points[i - 1])
        t = v_norm(t)
        ref = up if abs(v_dot(t, up)) < 0.95 else (1, 0, 0)
        b1 = v_norm(v_cross(t, ref)); b2 = v_cross(t, b1)
        rr = radii[i] if radii else r
        ring = []
        for j in range(seg + 1):
            a = 2 * math.pi * j / seg
            d = v_add(v_mul(b1, math.cos(a)), v_mul(b2, math.sin(a)))
            ring.append(g.vert(v_add(p, v_mul(d, rr)), d))
        rings.append((ring, t))
    for i in range(n - 1):
        a, b = rings[i][0], rings[i + 1][0]
        for j in range(seg):
            g.quad(a[j], b[j], b[j + 1], a[j + 1])
    if caps:
        for idx, sgn in ((0, -1), (n - 1, 1)):
            ring, t = rings[idx]; nn = v_mul(t, sgn)
            c = g.vert(points[idx], nn)
            ids = [g.vert(g.p[k], nn) for k in ring]
            for j in range(seg): g.tri(c, ids[j], ids[j + 1])
    return g.fix_winding()


# ----------------------------------------------------------------- materials
MAT_TYPES = {
    'matte': dict(roughnessFactor=0.85, metallicFactor=0.0),
    'satin': dict(roughnessFactor=0.55, metallicFactor=0.0),
    'gloss': dict(roughnessFactor=0.22, metallicFactor=0.0),
    'metal': dict(roughnessFactor=0.35, metallicFactor=0.85),
    'glass': dict(roughnessFactor=0.08, metallicFactor=0.0),
    'glow':  dict(roughnessFactor=0.6, metallicFactor=0.0),
}


# ----------------------------------------------------------------- model
class Model:
    def __init__(self, name, tint_groups=()):
        self.name = name
        self.parts = []          # (geo_world, color_lin, mat, group, bone, glowhex)
        self.markers = []        # (name, pos, euler, parentbone)
        self.bones = {}          # name -> (parent, world_pos)
        self.bone_order = []
        self.clips = []          # dicts
        self.tint_groups = set(tint_groups)
        self.notes = {}
        self.pivots = {}

    def pivot(self, group, p):
        """Give a static group its own origin (e.g. a door hinge) so code can rotate it."""
        self.pivots[group] = tuple(p)

    # -- authoring
    def add(self, geo, color='#cccccc', mat='matte', t=(0, 0, 0), r=(0, 0, 0), s=(1, 1, 1),
            group='main', bone=None, flat=False):
        g = geo.transformed(t, r, s)
        if flat: g = g.flat()
        glow = color if mat == 'glow' else None
        self.parts.append((g, col(color), mat, group, bone, glow))
        return self

    def marker(self, name, t=(0, 0, 0), r=(0, 0, 0), bone=None):
        self.markers.append((name, t, r, bone))

    def bone(self, name, parent, pos):
        self.bones[name] = (parent, pos); self.bone_order.append(name)

    def clip(self, name, duration, tracks, loop=True):
        """tracks: {bone: {'rot': [(t, (rx,ry,rz))...], 'pos': [(t, (dx,dy,dz))...]}}  pos = offset from rest."""
        self.clips.append(dict(name=name, duration=duration, tracks=tracks, loop=loop))

    # -- export
    def bbox(self):
        xs = [p for g, *_ in self.parts for p in g.p]
        mn = [min(p[k] for p in xs) for k in range(3)]
        mx = [max(p[k] for p in xs) for k in range(3)]
        return mn, mx

    def save(self, path):
        skinned = bool(self.bones)
        bin_ = bytearray(); bviews = []; accs = []

        def push(data, fmt, count, ctype, atype, target=None, minmax=None):
            while len(bin_) % 4: bin_.append(0)
            off = len(bin_)
            bin_.extend(struct.pack('<' + fmt * 1, *data) if False else struct.pack('<%d%s' % (len(data), fmt), *data))
            bv = dict(buffer=0, byteOffset=off, byteLength=len(bin_) - off)
            if target: bv['target'] = target
            bviews.append(bv)
            a = dict(bufferView=len(bviews) - 1, componentType=ctype, count=count, type=atype)
            if minmax: a['min'], a['max'] = minmax
            accs.append(a)
            return len(accs) - 1

        materials, mat_index = [], {}
        def get_mat(group, mtype, glow):
            key = (group if group in self.tint_groups else '', mtype, glow)
            if key in mat_index: return mat_index[key]
            pbr = dict(MAT_TYPES[mtype]); pbr['baseColorFactor'] = [1, 1, 1, 1]
            m = dict(name=(('tint_' + group) if key[0] else mtype) + (('_' + glow.lstrip('#')) if glow else ''),
                     pbrMetallicRoughness=pbr)
            if glow:
                m['emissiveFactor'] = list(col(glow))
                m['extensions'] = {'KHR_materials_emissive_strength': {'emissiveStrength': 2.0}}
            if mtype == 'glass':
                pbr['baseColorFactor'] = [1, 1, 1, 0.35]; m['alphaMode'] = 'BLEND'
            materials.append(m); mat_index[key] = len(materials) - 1
            return mat_index[key]

        nodes = [dict(name=self.name, children=[])]
        bone_node = {}
        if skinned:
            for b in self.bone_order:
                parent, pos = self.bones[b]
                ppos = self.bones[parent][1] if parent else (0, 0, 0)
                nodes.append(dict(name=b, translation=list(v_sub(pos, ppos)), children=[]))
                bone_node[b] = len(nodes) - 1
            for b in self.bone_order:
                parent = self.bones[b][0]
                if parent: nodes[bone_node[parent]]['children'].append(bone_node[b])
                else: nodes[0]['children'].append(bone_node[b])
            joints = [bone_node[b] for b in self.bone_order]
            ibm = []
            for b in self.bone_order:
                x, y, z = self.bones[b][1]
                ibm += [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -x, -y, -z, 1]
            ibm_acc = push(ibm, 'f', len(self.bone_order), 5126, 'MAT4')
            skins = [dict(joints=joints, inverseBindMatrices=ibm_acc, skeleton=joints[0])]

        # group parts -> meshes
        groups = {}
        for g, c, mtype, group, bone, glow in self.parts:
            groups.setdefault(group, {}).setdefault((mtype, glow), []).append((g, c, bone))
        meshes = []; tri_total = 0
        for group, bymat in groups.items():
            prims = []
            for (mtype, glow), plist in bymat.items():
                P, N, C, J, I = [], [], [], [], []
                piv = self.pivots.get(group, (0, 0, 0))
                for g, c, bone in plist:
                    o = len(P) // 3
                    for p in g.p: P += (p[0] - piv[0], p[1] - piv[1], p[2] - piv[2])
                    for n in g.n: N += n
                    C += list(c) * len(g.p)
                    if skinned:
                        bi = self.bone_order.index(bone or self.bone_order[0])
                        J += [bi, 0, 0, 0] * len(g.p)
                    for a, b, cc in g.t: I += [a + o, b + o, cc + o]
                vc = len(P) // 3
                mn = [min(P[k::3]) for k in range(3)]; mx = [max(P[k::3]) for k in range(3)]
                attrs = dict(POSITION=push(P, 'f', vc, 5126, 'VEC3', 34962, (mn, mx)),
                             NORMAL=push(N, 'f', vc, 5126, 'VEC3', 34962),
                             COLOR_0=push(C, 'f', vc, 5126, 'VEC3', 34962))
                if skinned:
                    attrs['JOINTS_0'] = push(J, 'B', vc, 5121, 'VEC4', 34962)
                    attrs['WEIGHTS_0'] = push([1.0, 0.0, 0.0, 0.0] * vc, 'f', vc, 5126, 'VEC4', 34962)
                big = vc > 65535
                idx = push(I, 'I' if big else 'H', len(I), 5125 if big else 5123, 'SCALAR', 34963)
                prims.append(dict(attributes=attrs, indices=idx, material=get_mat(group, mtype, glow)))
                tri_total += len(I) // 3
            meshes.append(dict(name=group, primitives=prims))
            nd = dict(name=group, mesh=len(meshes) - 1)
            if group in self.pivots: nd['translation'] = list(self.pivots[group])
            if skinned: nd['skin'] = 0
            nodes.append(nd); nodes[0]['children'].append(len(nodes) - 1)

        for name, t, r, bone in self.markers:
            nd = dict(name=name, translation=list(t))
            if any(r): nd['rotation'] = list(quat_from_euler(*r))
            if skinned and bone:
                bp = self.bones[bone][1]
                nd['translation'] = list(v_sub(t, bp))
                nodes.append(nd); nodes[bone_node[bone]]['children'].append(len(nodes) - 1)
            else:
                nodes.append(nd); nodes[0]['children'].append(len(nodes) - 1)

        animations = []
        node_lookup = {n['name']: i for i, n in enumerate(nodes)}
        for cl in self.clips:
            samplers, channels = [], []
            for bname, tr in cl['tracks'].items():
                ni = bone_node.get(bname, node_lookup.get(bname))
                if ni is None: raise KeyError(bname)
                rest = nodes[ni].get('translation', [0, 0, 0])
                for chan, keys in tr.items():
                    times = [k[0] for k in keys]
                    tin = push(times, 'f', len(times), 5126, 'SCALAR', None, ([min(times)], [max(times)]))
                    if chan == "rot":
                        out, prev = [], None
                        for _, e in keys:
                            q = quat_from_euler(*e)
                            if prev and sum(a * b for a, b in zip(q, prev)) < 0: q = tuple(-x for x in q)
                            out += q; prev = q
                        tout = push(out, 'f', len(keys), 5126, 'VEC4')
                        p = 'rotation'
                    elif chan == "scale":
                        out = []
                        for _, s in keys: out += s
                        tout = push(out, 'f', len(keys), 5126, 'VEC3'); p = 'scale'
                    else:
                        out = []
                        for _, d in keys: out += [rest[0] + d[0], rest[1] + d[1], rest[2] + d[2]]
                        tout = push(out, 'f', len(keys), 5126, 'VEC3'); p = 'translation'
                    samplers.append(dict(input=tin, output=tout, interpolation='LINEAR'))
                    channels.append(dict(sampler=len(samplers) - 1, target=dict(node=ni, path=p)))
            animations.append(dict(name=cl['name'], samplers=samplers, channels=channels))

        gl = dict(asset=dict(version='2.0', generator='funny-game gltf_builder.py'),
                  scene=0, scenes=[dict(nodes=[0])], nodes=nodes, meshes=meshes,
                  materials=materials, accessors=accs, bufferViews=bviews,
                  buffers=[dict(byteLength=0)])
        if any('extensions' in m for m in materials):
            gl['extensionsUsed'] = ['KHR_materials_emissive_strength']
        if skinned: gl['skins'] = skins
        if animations: gl['animations'] = animations
        for n in nodes:
            if 'children' in n and not n['children']: del n['children']
        while len(bin_) % 4: bin_.append(0)
        gl['buffers'][0]['byteLength'] = len(bin_)
        js = json.dumps(gl, separators=(',', ':')).encode()
        while len(js) % 4: js += b' '
        out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_))
        out += struct.pack('<II', len(js), 0x4E4F534A) + js
        out += struct.pack('<II', len(bin_), 0x004E4942) + bytes(bin_)
        with open(path, 'wb') as f: f.write(out)

        mn, mx = self.bbox()
        return dict(
            file=path.split('public/')[-1], triangles=tri_total,
            size_m=[round(mx[k] - mn[k], 3) for k in range(3)],
            bbox_min=[round(v, 3) for v in mn], bbox_max=[round(v, 3) for v in mx],
            meshes=list(groups.keys()),
            pivots={k: [round(x, 3) for x in v] for k, v in self.pivots.items()},
            tint_materials=['tint_' + g for g in groups if g in self.tint_groups],
            markers=[m[0] for m in self.markers],
            bones=self.bone_order if skinned else [],
            animations=[dict(name=c['name'], duration=c['duration'], loop=c['loop']) for c in self.clips],
            **self.notes)
