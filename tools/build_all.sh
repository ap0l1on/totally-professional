#!/bin/sh
# Regenerates every asset from source (pure Python 3 + Pillow; no other deps).
set -e
cd "$(dirname "$0")/.."
python3 tools/build_characters.py
python3 tools/build_props.py
python3 tools/build_textures.py
python3 tools/build_audio.py
python3 tools/build_ui.py
python3 tools/build_manifest.py
echo "Renders (ui/renders/*.png) need a browser: python3 tools/dev_server.py, then open http://localhost:8765/tools/render_shots.html"
