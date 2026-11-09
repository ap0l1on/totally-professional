"""Tileable textures + text decals (PIL) -> public/assets/textures/*.png"""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

OUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'assets', 'textures')
os.makedirs(OUT, exist_ok=True)
MAN = {}
rnd = random.Random(7)
FONT_DIR = '/System/Library/Fonts/Supplemental/'
def font(name, size):
    try: return ImageFont.truetype(FONT_DIR + name, size)
    except Exception: return ImageFont.load_default()

def save(img, name, use, tile=True, repeat_m=None):
    p = os.path.join(OUT, name + '.png'); img.save(p, optimize=True)
    MAN[name] = dict(file='assets/textures/%s.png' % name, size=list(img.size), tileable=tile, use=use, **({'metres_per_tile': repeat_m} if repeat_m else {}))
    print('%-28s %s' % (name, img.size))

def hexrgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def tile_blur(img, r):
    w, h = img.size; big = Image.new(img.mode, (w * 3, h * 3))
    for i in range(3):
        for j in range(3): big.paste(img, (i * w, j * h))
    return big.filter(ImageFilter.GaussianBlur(r)).crop((w, h, 2 * w, 2 * h))

def noise_l(size, sigma=64, blur=0):
    n = Image.effect_noise((size, size), sigma)
    return tile_blur(n, blur) if blur else n

def colorize(l, dark, light):
    return Image.merge('RGB', [l.point(lambda v, a=a, b=b: int(a + (b - a) * v / 255)) for a, b in zip(hexrgb(dark), hexrgb(light))])

def speckle(size, base_dark, base_light, blur_big=12, fine=0.35):
    a = noise_l(size, 80, blur_big); b = noise_l(size, 90)
    l = ImageChops.blend(a, b, fine)
    l = l.point(lambda v: max(0, min(255, int((v - 128) * 2.2 + 128))))
    return colorize(l, base_dark, base_light)

S = 512

def textures():
    save(speckle(S, '#46546b', '#6d7f99'), 'carpet_office', 'Office floor', repeat_m=2)
    save(speckle(S, '#d8d2c2', '#ebe6d9', 30, 0.15), 'wall_office', 'Office walls (beige)', repeat_m=3)
    # ceiling tiles
    img = speckle(S, '#d9d9d6', '#efefec', 20, 0.4); d = ImageDraw.Draw(img)
    for k in (0, S // 2): d.line([(k, 0), (k, S)], fill=(160, 160, 160), width=6); d.line([(0, k), (S, k)], fill=(160, 160, 160), width=6)
    save(img, 'ceiling_tiles', 'Office ceiling (2x2 tiles per texture)', repeat_m=1.2)
    # wood planks
    img = Image.new('RGB', (S, S)); d = ImageDraw.Draw(img); ph = S // 8
    grain = noise_l(S, 70, 0).resize((S // 16, S)).resize((S, S))
    for i in range(8):
        c = hexrgb(rnd.choice(['#a8774f', '#b5835a', '#9a6a45', '#b07c52']))
        d.rectangle([0, i * ph, S, (i + 1) * ph], fill=c)
    img = ImageChops.multiply(img, colorize(grain.rotate(90), '#c8c8c8', '#ffffff'))
    d = ImageDraw.Draw(img)
    for i in range(8):
        d.line([(0, i * ph), (S, i * ph)], fill=(70, 45, 30), width=3)
        x = rnd.randint(0, S); d.line([(x, i * ph), (x, (i + 1) * ph)], fill=(70, 45, 30), width=3)
    save(img, 'wood_floor', 'Grandma house floor / bedroom floor', repeat_m=2)
    # brick
    img = Image.new('RGB', (S, S), hexrgb('#cfc4b4')); d = ImageDraw.Draw(img); bh, bw = S // 16, S // 4
    for row in range(16):
        off = (bw // 2) if row % 2 else 0
        for col in range(-1, 5):
            x = col * bw + off; c = hexrgb(rnd.choice(['#a4513a', '#b35c42', '#94472f', '#a95a3c', '#8c4330']))
            d.rectangle([x + 3, row * bh + 3, x + bw - 3, row * bh + bh - 3], fill=c)
    img = ImageChops.multiply(img, colorize(noise_l(S, 60, 1), '#d0d0d0', '#ffffff'))
    save(img, 'brick', 'Chimneys, building walls', repeat_m=2)
    save(speckle(S, '#4a4d52', '#7b7f86', 6, 0.6), 'roof_gravel', 'Flat rooftops (L2)', repeat_m=3)
    save(speckle(S, '#8f9196', '#b4b6ba', 25, 0.3), 'concrete', 'Ledges, sidewalks', repeat_m=3)
    # grass
    img = speckle(S, '#4c8f3a', '#79c25a', 10, 0.5); d = ImageDraw.Draw(img)
    for _ in range(2500):
        x, y = rnd.randint(0, S), rnd.randint(0, S); c = rnd.choice([(96, 168, 70), (70, 130, 52), (120, 190, 85)])
        d.line([(x, y), (x + rnd.randint(-3, 3), y - rnd.randint(4, 10))], fill=c, width=1)
    save(img, 'grass', 'Park, party lawn', repeat_m=4)
    save(speckle(S, '#b08c62', '#d2b48a', 14, 0.4), 'dirt_path', 'Park paths', repeat_m=3)
    # pond water
    w = noise_l(S, 80, 18); w = w.point(lambda v: max(0, min(255, int((v - 128) * 3 + 128))))
    save(colorize(w, '#2b7bb9', '#6cc3e8'), 'water', 'Pond (scroll UVs slowly)', repeat_m=6)
    # floral wallpaper
    img = Image.new('RGB', (S, S), hexrgb('#f3e3d3')); d = ImageDraw.Draw(img)
    for x in range(0, S, 32): d.line([(x, 0), (x, S)], fill=hexrgb('#ead2bf'), width=10)
    for i in range(4):
        for j in range(4):
            cx, cy = i * 128 + (64 if j % 2 else 0) + 32, j * 128 + 40
            for k in range(5):
                a = k * 72; px, py = cx + 12 * math.cos(math.radians(a)), cy + 12 * math.sin(math.radians(a))
                for ox in (-S, 0, S):
                    d.ellipse([px - 9 + ox, py - 9, px + 9 + ox, py + 9], fill=hexrgb('#d98aa8'))
            d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=hexrgb('#f2c14e'))
            d.ellipse([cx + 18, cy + 14, cx + 34, cy + 22], fill=hexrgb('#8fb37a'))
    save(img, 'wallpaper_floral', 'Grandma house walls', repeat_m=2)
    # kitchen checker
    img = Image.new('RGB', (S, S)); d = ImageDraw.Draw(img); c = S // 8
    for i in range(8):
        for j in range(8): d.rectangle([i * c, j * c, (i + 1) * c, (j + 1) * c], fill=hexrgb('#f4f1ea' if (i + j) % 2 else '#4f7cac'))
    save(img, 'tile_checker', 'Grandma kitchen floor', repeat_m=2)
    save(speckle(S, '#cbb79c', '#e6d7c2', 3, 0.7), 'carpet_bedroom', 'L6 giant bedroom floor (scale up a lot: you are tiny)', repeat_m=1)
    # building facade with windows (some lit)
    img = Image.new('RGB', (S, S), hexrgb('#b9b2a7')); img = ImageChops.multiply(img, colorize(noise_l(S, 50, 2), '#d8d8d8', '#ffffff'))
    d = ImageDraw.Draw(img)
    for i in range(4):
        for j in range(4):
            x, y = i * 128 + 30, j * 128 + 24
            lit = rnd.random() < 0.3
            d.rectangle([x - 6, y - 6, x + 74, y + 86], fill=hexrgb('#8d877d'))
            d.rectangle([x, y, x + 68, y + 80], fill=hexrgb('#ffe9a8' if lit else '#4f6d8a'))
            d.line([(x + 34, y), (x + 34, y + 80)], fill=hexrgb('#ece6dc'), width=4)
            d.line([(x, y + 40), (x + 68, y + 40)], fill=hexrgb('#ece6dc'), width=4)
    save(img, 'building_facade', 'Rooftop-level building walls (4x4 windows per tile)', repeat_m=12)
    # party stripes / bouncy
    img = Image.new('RGB', (S, S)); d = ImageDraw.Draw(img)
    for i, c in enumerate(['#ff5a5a', '#ffd43b', '#4dabf7', '#69db7c'] * 2): d.rectangle([i * 64, 0, i * 64 + 64, S], fill=hexrgb(c))
    save(img, 'party_stripes', 'Party tent / backdrop', repeat_m=2)


def banner(name, w, h, bg, lines, use, fg='#ffffff', outline='#00000055', fonts=None, deco=None):
    img = Image.new('RGBA', (w, h), hexrgb(bg) + (255,)); d = ImageDraw.Draw(img)
    if deco: deco(d, w, h)
    y = h * 0.5 - sum(sz for _, sz, *_ in lines) * 0.55
    for item in lines:
        text, size = item[0], item[1]; fname = item[2] if len(item) > 2 else 'Arial Black.ttf'; col = item[3] if len(item) > 3 else fg
        fnt = font(fname, size); tw = d.textlength(text, font=fnt)
        while tw > w * 0.9 and size > 10:
            size = int(size * 0.94); fnt = font(fname, size); tw = d.textlength(text, font=fnt)
        x = (w - tw) / 2
        d.text((x + size * 0.06, y + size * 0.06), text, font=fnt, fill=(0, 0, 0, 90))
        d.text((x, y), text, font=fnt, fill=hexrgb(col))
        y += size * 1.15
    save(img.convert('RGB'), name, use, tile=False)

def decals():
    def bunting(d, w, h):
        cols = ['#ff5a5a', '#ffd43b', '#4dabf7', '#69db7c', '#b197fc']
        for i in range(0, w, 64):
            d.polygon([(i, 0), (i + 56, 0), (i + 28, 46)], fill=hexrgb(cols[(i // 64) % 5]))
            d.polygon([(i, h), (i + 56, h), (i + 28, h - 46)], fill=hexrgb(cols[(i // 64 + 2) % 5]))
    banner('banner_happy_gary_day', 1536, 384, '#2b2d6e', [('HAPPY GARY DAY!', 150, 'Arial Black.ttf', '#ffd43b'),
                                                          ('Be like Gary. Dress like Gary. Become Gary.', 56, 'Arial Bold.ttf')], 'L1 office banner (ratio 4:1)', deco=bunting)
    banner('poster_gary_employee', 512, 640, '#f4f1ea', [('EMPLOYEE', 64, 'Impact.ttf', '#2b2d6e'), ('OF THE MONTH', 52, 'Impact.ttf', '#2b2d6e'),
                                                         ('', 260), ('GARY', 90, 'Impact.ttf', '#c0262d'), ('(every month since 2009)', 30, 'Arial Bold.ttf', '#444444')],
           'L1 wall poster. Leave the blank middle for a render of Gary (ui/renders/portrait_gary.png) or draw a frame.')
    banner('sign_dont_feed_geese', 1100, 500, '#f6efe1', [('DO NOT FEED', 110, 'Impact.ttf', '#c0262d'), ('THE GEESE', 110, 'Impact.ttf', '#c0262d'),
                                                         ('They know what they did.', 46, 'Arial Bold.ttf', '#333333')], 'L3 park signpost face (signpost.glb node "face")',
           deco=lambda d, w, h: d.rectangle([12, 12, w - 12, h - 12], outline=hexrgb('#c0262d'), width=14))
    banner('sign_launch_codes', 600, 600, '#ffe14d', [('LAUNCH', 80, 'Chalkduster.ttf', '#c0262d'), ('CODES:', 80, 'Chalkduster.ttf', '#c0262d'),
                                                     ('password123', 70, 'Chalkduster.ttf', '#222222'), ('(do not lose)', 40, 'Chalkduster.ttf', '#555555')], 'L3 sticky note close-up / HUD item')
    banner('billboard_cold_feet', 1260, 600, '#4dabf7', [('COLD FEET?', 170, 'Impact.ttf', '#ffffff'), ('TRY SOCKS.', 120, 'Impact.ttf', '#ffd43b'),
                                                        ('SockCo - commitment for your toes', 40, 'Arial Bold.ttf', '#ffffff')], 'L2 billboard (billboard.glb node "face")')
    banner('billboard_megacorp', 1260, 600, '#2b2d6e', [('MEGACORP', 170, 'Impact.ttf', '#ffffff'), ("WE'RE ALL GARY NOW", 90, 'Impact.ttf', '#ffd43b')], 'L2 billboard alt')
    banner('banner_birthday', 1536, 384, '#ff8cc6', [('HAPPY 7th BIRTHDAY TIMMY!', 120, 'Arial Black.ttf', '#ffffff'), ('(the balloons are fine. probably.)', 48, 'Arial Bold.ttf', '#5a1640')],
           'L5 party banner', deco=bunting)
    banner('mug_okayest_boss', 512, 160, '#ffffff', [("WORLD'S OKAYEST", 54, 'Arial Black.ttf', '#222222'), ('BOSS', 64, 'Arial Black.ttf', '#c0262d')], "Gary's mug wrap")
    img = Image.new('RGB', (256, 340), 'white'); d = ImageDraw.Draw(img); d.rectangle([0, 0, 256, 120], fill=hexrgb('#c0262d'))
    for txt, fn, sz, y, c in (('HELLO', 'Arial Black.ttf', 52, 18, '#ffffff'), ('my name is', 'Arial Bold.ttf', 26, 80, '#ffffff'), ('GARY', 'Chalkduster.ttf', 70, 180, '#222222')):
        f = font(fn, sz); d.text(((256 - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=hexrgb(c))
    save(img, 'name_badge_gary', 'Lanyard badge', tile=False)
    banner('wifi_password_note', 600, 400, '#fffbe6', [('WIFI', 70, 'Noteworthy.ttc' if False else 'Chalkboard.ttc', '#2a5bd7'), ('Password: "grandson"', 52, 'Chalkboard.ttc', '#222222'),
                                                      ('(it is always "grandson")', 36, 'Chalkboard.ttc', '#666666')], 'L4 fridge note')
    banner('cross_stitch_home', 600, 450, '#f8f1e3', [('BLESS THIS', 70, 'Chalkduster.ttf', '#8d3b4a'), ('ROUTER', 90, 'Chalkduster.ttf', '#3d5a80')],
           "L4 framed cross-stitch (framed_picture.glb node 'canvas')", deco=lambda d, w, h: [d.rectangle([20 + k * 14, 20 + k * 14, w - 20 - k * 14, h - 20 - k * 14], outline=hexrgb(c), width=6) for k, c in enumerate(['#8d3b4a', '#d9a441'])])
    banner('clock_face_text', 512, 128, '#ffffff', [('5:00 AM', 100, 'Impact.ttf', '#e8322f')], 'L6 digital readout / HUD')


if __name__ == '__main__':
    textures(); decals()
    with open(os.path.join(OUT, '_manifest_textures.json'), 'w') as f: json.dump(MAN, f, indent=1)
