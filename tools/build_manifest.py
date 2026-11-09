"""Merge per-category manifests into public/assets/manifest.json (single source of truth for the game)."""
import json, os, glob
A = os.path.join(os.path.dirname(__file__), '..', 'public', 'assets')
def load(p):
    with open(os.path.join(A, p)) as f: return json.load(f)
out = {
    'conventions': {
        'units': 'metres', 'up': '+Y', 'forward': 'models face +Z (rotate PI to face -Z)', 'origin': 'base centre at y=0 unless noted',
        'weapons': 'origin = right-hand grip, barrel points -Z, marker "muzzle" = projectile spawn, marker "grip_L" = support hand',
        'materials': 'vertex-coloured MeshStandardMaterial; materials named tint_<group> are single-colour and can be recoloured '
                     '(clone material, set vertexColors=false, color.set(hex))',
        'accessories': 'meshes/groups named acc_* are optional accessories: toggle visibility of the WHOLE subtree (multi-material accessories '
                       'load as a Group "acc_x" with child meshes)',
        'skinned': 'characters are rigidly skinned; clone with SkeletonUtils.clone(); animations included in each .glb',
    },
    'models': {'characters': load('models/_manifest_characters.json'), 'props': load('models/_manifest_props.json'),
               'weapons': load('models/_manifest_weapons.json')},
    'textures': load('textures/_manifest_textures.json'),
    'audio': load('audio/_manifest_audio.json'),
    'ui': load('ui/_manifest_ui.json'),
    'renders': {os.path.basename(p)[:-4]: 'assets/ui/renders/' + os.path.basename(p) for p in sorted(glob.glob(os.path.join(A, 'ui', 'renders', '*.png')))},
}
with open(os.path.join(A, 'manifest.json'), 'w') as f: json.dump(out, f, indent=1)
print('manifest.json written')
