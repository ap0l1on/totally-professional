"""Logo + HUD / clue icons as SVG -> public/assets/ui/{logo.svg, icons/*.svg}"""
import json, os
OUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'assets', 'ui')
os.makedirs(os.path.join(OUT, 'icons'), exist_ok=True)
INK = '#1b1b1f'
MAN = {}

def icon(name, body, use):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
           '<g stroke="%s" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">%s</g></svg>' % (INK, body))
    with open(os.path.join(OUT, 'icons', name + '.svg'), 'w') as f: f.write(svg)
    MAN[name] = dict(file='assets/ui/icons/%s.svg' % name, use=use)

ICONS = {
    'crosshair': ('<circle cx="32" cy="32" r="14" fill="none" stroke="#fff"/><path d="M32 6v14M32 44v14M6 32h14M44 32h14" stroke="#fff"/><circle cx="32" cy="32" r="2.5" fill="#ff3b5c" stroke="none"/>', 'Default crosshair (white, draw with a dark drop-shadow)'),
    'heart': ('<path d="M32 54 10 32C3 25 6 12 17 11c7 0 11 5 15 10 4-5 8-10 15-10 11 1 14 14 7 21Z" fill="#ff4f6d"/>', 'Health'),
    'lock': ('<rect x="14" y="28" width="36" height="28" rx="5" fill="#ffd43b"/><path d="M22 28v-8a10 10 0 0 1 20 0v8" fill="none"/><circle cx="32" cy="41" r="3" fill="' + INK + '"/>', 'Locked level'),
    'star': ('<path d="m32 6 7.6 16.2 17.4 2-12.9 12 3.4 17.3L32 45l-15.5 8.5 3.4-17.3-12.9-12 17.4-2Z" fill="#ffd43b"/>', 'Rating star (earned)'),
    'star_empty': ('<path d="m32 6 7.6 16.2 17.4 2-12.9 12 3.4 17.3L32 45l-15.5 8.5 3.4-17.3-12.9-12 17.4-2Z" fill="#3a3d4a"/>', 'Rating star (not earned)'),
    'check': ('<circle cx="32" cy="32" r="26" fill="#40c057"/><path d="m20 33 8 8 16-17" fill="none" stroke="#fff" stroke-width="6"/>', 'Level completed'),
    'clue_mustache': ('<path d="M32 28c-6-8-20-6-24 4 6 4 14 6 20 2 2-1 3-3 4-6 1 3 2 5 4 6 6 4 14 2 20-2-4-10-18-12-24-4Z" fill="#4a2e1c"/>', 'Clue: real (straight) mustache'),
    'clue_stain': ('<path d="M26 8h12l4 8-6 40h-8l-6-40Z" fill="#c0262d"/><path d="M28 28c3-3 9-2 10 2s-3 8-7 7-6-5-3-9Z" fill="#6b4426" stroke="none"/>', 'Clue: coffee stain on tie'),
    'clue_watch_right': ('<rect x="24" y="4" width="16" height="56" rx="4" fill="#2b2b2b"/><circle cx="32" cy="32" r="13" fill="#e8c35a"/><path d="M32 25v7l5 3" fill="none"/><text x="50" y="62" font-family="Arial Black,Arial" font-size="16" fill="#fff" stroke="none">R</text>', 'Clue: watch on RIGHT wrist'),
    'clue_pen': ('<path d="m44 8 12 12-30 30-14 2 2-14Z" fill="#2a5bd7"/><path d="m14 38 12 12" fill="none"/><path d="M14 52l-2 0 0-2" fill="#e6d3a8"/>', 'Clue: pen behind ear'),
    'clue_mug': ('<path d="M12 18h32v28a10 10 0 0 1-10 10H22a10 10 0 0 1-10-10Z" fill="#fff"/><path d="M44 24h6a7 7 0 0 1 0 14h-6" fill="none"/><path d="M12 30h32" stroke="#ffd23f" stroke-width="6"/>', "Clue: carries the WORLD'S OKAYEST BOSS mug"),
    'clue_hum': ('<path d="M24 46V14l26-6v32" fill="none"/><circle cx="18" cy="46" r="7" fill="' + INK + '"/><circle cx="44" cy="40" r="7" fill="' + INK + '"/>', 'Clue: he hums (listen!)'),
    'clue_unknown': ('<rect x="8" y="8" width="48" height="48" rx="10" fill="#3a3d4a"/><text x="32" y="45" text-anchor="middle" font-family="Arial Black,Arial" font-size="34" fill="#fff" stroke="none">?</text>', 'Clue not unlocked yet'),
    'soup': ('<path d="M6 30h52a26 22 0 0 1-52 0Z" fill="#f4f2ec"/><path d="M10 30h44" stroke="#e8963a" stroke-width="6"/><path d="M22 20c0-6 6-6 6-12M34 20c0-6 6-6 6-12" fill="none" stroke="#9aa0aa"/>', 'L4 soup meter (3 bowls = food coma = fail)'),
    'ring': ('<circle cx="32" cy="40" r="16" fill="none" stroke="#f2c14e" stroke-width="7"/><path d="m24 18 8-12 8 12-8 6Z" fill="#d9f6ff"/>', 'L2 objective: the ring / groom'),
    'timer': ('<circle cx="32" cy="36" r="22" fill="#fff"/><path d="M32 22v14l9 6M26 6h12M32 6v8" fill="none"/>', 'Timer'),
    'cake': ('<rect x="10" y="30" width="44" height="24" rx="4" fill="#ffe3ef"/><path d="M10 38c6 4 10-4 15 0s10-4 15 0 10-4 14 0" fill="none" stroke="#ff8cc6"/><path d="M22 30v-10M32 30v-10M42 30v-10" /><path d="M22 14c-2 2 2 4 0 6M32 14c-2 2 2 4 0 6M42 14c-2 2 2 4 0 6" stroke="#ffb02e" fill="none"/>', 'L5 cake health'),
    'snooze': ('<rect x="8" y="22" width="48" height="26" rx="8" fill="#ff8a00"/><text x="32" y="42" text-anchor="middle" font-family="Arial Black,Arial" font-size="16" fill="#fff" stroke="none">Zzz</text>', 'L6 weak point indicator'),
    'ammo_dart': ('<rect x="27" y="14" width="10" height="38" rx="3" fill="#3bc9db"/><path d="M24 14a8 6 0 0 1 16 0Z" fill="#ff3b5c"/>', 'Dart ammo'),
    'ammo_net': ('<circle cx="32" cy="32" r="22" fill="#e9e3d0"/><path d="M14 22h36M10 32h44M14 42h36M22 12v40M32 10v44M42 12v40" stroke-width="2.5" fill="none"/>', 'Net ammo'),
    'ammo_water': ('<path d="M32 6C22 22 14 30 14 40a18 18 0 0 0 36 0c0-10-8-18-18-34Z" fill="#339af0"/>', 'Water tank'),
    'ammo_pillow': ('<path d="M8 18q24-8 48 0 4 14 0 28-24 8-48 0-4-14 0-28Z" fill="#fff"/>', 'Pillow ammo'),
    'router': ('<rect x="8" y="34" width="48" height="18" rx="5" fill="#1f2228"/><path d="M16 34 12 10M48 34l4-24" /><circle cx="22" cy="43" r="2.5" fill="#36ff6b" stroke="none"/><circle cx="32" cy="43" r="2.5" fill="#36ff6b" stroke="none"/><circle cx="42" cy="43" r="2.5" fill="#ff8a1f" stroke="none"/>', 'L4 objective'),
    'eye': ('<path d="M4 32q28-26 56 0-28 26-56 0Z" fill="#fff"/><circle cx="32" cy="32" r="10" fill="' + INK + '"/>', 'Stealth: being watched'),
    'exclaim': ('<path d="M32 6 60 56H4Z" fill="#ffd43b"/><path d="M32 24v14" stroke-width="6"/><circle cx="32" cy="47" r="3" fill="' + INK + '"/>', 'Spotted / alert'),
    'pause': ('<rect x="14" y="10" width="12" height="44" rx="3" fill="#fff"/><rect x="38" y="10" width="12" height="44" rx="3" fill="#fff"/>', 'Pause'),
    'sound_on': ('<path d="M8 24h12l14-12v40L20 40H8Z" fill="#fff"/><path d="M42 22q8 10 0 20M48 16q14 16 0 32" fill="none" stroke="#fff"/>', 'Sound on'),
    'sound_off': ('<path d="M8 24h12l14-12v40L20 40H8Z" fill="#fff"/><path d="m42 24 16 16M58 24 42 40" stroke="#ff4f6d"/>', 'Sound off'),
}

LOGO = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" width="900" height="360">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe066"/><stop offset="1" stop-color="#ff922b"/></linearGradient>
    <filter id="s" x="-10%" y="-10%" width="120%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="0" flood-color="#1b1b1f"/></filter>
  </defs>
  <g transform="rotate(-4 450 180)" filter="url(#s)">
    <text x="450" y="150" text-anchor="middle" font-family="Impact, 'Arial Black', sans-serif" font-size="128" fill="url(#g)" stroke="#1b1b1f" stroke-width="10" paint-order="stroke" letter-spacing="4">TOTALLY</text>
    <text x="450" y="262" text-anchor="middle" font-family="Impact, 'Arial Black', sans-serif" font-size="112" fill="#fff" stroke="#1b1b1f" stroke-width="10" paint-order="stroke" letter-spacing="2">PROFESSIONAL</text>
  </g>
  <!-- agent shades -->
  <g transform="translate(700 40) rotate(12)">
    <path d="M0 20h150" stroke="#1b1b1f" stroke-width="10" stroke-linecap="round"/>
    <path d="M8 18h56q4 40-30 38Q8 54 8 18Z M86 18h56q0 36-26 38-34 2-30-38Z" fill="#1b1b1f"/>
    <path d="M20 26l10 0M98 26l10 0" stroke="#fff" stroke-width="5" stroke-linecap="round"/>
  </g>
  <g transform="translate(450 320) rotate(-4)">
    <rect x="-230" y="-30" width="460" height="52" rx="26" fill="#ff4f6d" stroke="#1b1b1f" stroke-width="6"/>
    <text x="0" y="8" text-anchor="middle" font-family="'Arial Black', Arial, sans-serif" font-size="26" fill="#fff">MISSIONS NOBODY ASKED FOR</text>
  </g>
</svg>'''

FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#ff922b"/><path d="M6 26h52" stroke="#1b1b1f" stroke-width="5"/><path d="M8 25h20q2 18-10 17Q8 41 8 25ZM36 25h20q0 16-10 17-12 1-10-17Z" fill="#1b1b1f"/></svg>'

if __name__ == '__main__':
    for k, (b, u) in ICONS.items(): icon(k, b, u)
    with open(os.path.join(OUT, 'logo.svg'), 'w') as f: f.write(LOGO)
    with open(os.path.join(OUT, 'favicon.svg'), 'w') as f: f.write(FAVICON)
    MAN['logo'] = dict(file='assets/ui/logo.svg', use='Title logo (main menu). Game title: TOTALLY PROFESSIONAL')
    MAN['favicon'] = dict(file='assets/ui/favicon.svg', use='Browser tab icon')
    with open(os.path.join(OUT, '_manifest_ui.json'), 'w') as f: json.dump(MAN, f, indent=1)
    print(len(MAN), 'ui files')
