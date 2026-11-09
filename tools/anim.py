"""Helpers for authoring keyframed clips as poses."""
import math


def posed(frames, pos_bone='hips'):
    """frames: [(t, {bone: (rx,ry,rz), '<bone>@pos': (dx,dy,dz), '<bone>@scale': (sx,sy,sz)})]
    Missing rotation bones default to 0. Returns tracks dict for Model.clip."""
    bones, posb, scb = set(), set(), set()
    for _, pose in frames:
        for k in pose:
            if k.endswith('@pos'): posb.add(k[:-4])
            elif k.endswith('@scale'): scb.add(k[:-6])
            else: bones.add(k)
    tracks = {}
    for b in bones:
        tracks.setdefault(b, {})['rot'] = [(t, pose.get(b, (0, 0, 0))) for t, pose in frames]
    for b in posb:
        tracks.setdefault(b, {})['pos'] = [(t, pose.get(b + '@pos', (0, 0, 0))) for t, pose in frames]
    for b in scb:
        tracks.setdefault(b, {})['scale'] = [(t, pose.get(b + '@scale', (1, 1, 1))) for t, pose in frames]
    return tracks


def osc(dur, n, fn):
    """Sample fn(phase 0..1) -> pose dict n times for a seamless loop."""
    frames = []
    for i in range(n + 1):
        p = i / n
        pose = fn(p % 1.0 if i < n else 0.0)
        frames.append((round(dur * p, 5), pose))
    return posed(frames)


S = lambda p, k=1, ph=0: math.sin(2 * math.pi * (k * p + ph))
C = lambda p, k=1, ph=0: math.cos(2 * math.pi * (k * p + ph))
pos = lambda x: max(0.0, x)
