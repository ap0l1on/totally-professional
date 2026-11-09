# totally-professional

**TOTALLY PROFESSIONAL**: a funny first-person mission game for the web (three.js), with *missions nobody asked for*.

**Play:** https://ap0l1on.github.io/totally-professional/ (live once the game code is built and deployed)

This repo currently holds **all game assets** plus the prompt that tells OpenCode how to build the game.

- `OPENCODE_PROMPT.md`: the full spec to paste into OpenCode (gameplay, levels, tech, git + deploy workflow).
- `public/assets/`: models (.glb, animated), textures, audio (.wav), UI (SVG icons, logo, pre-rendered PNGs).
- `public/assets/manifest.json`: machine-readable list of every asset (sizes, node names, animations, usage).
- `tools/`: the pure-Python generators that produced every asset (`sh tools/build_all.sh` rebuilds them).

## Deployment
Pushing to `main` deploys to GitHub Pages through `.github/workflows/deploy.yml` (OpenCode creates it).
Pages must be set to **Settings → Pages → Source: GitHub Actions**, or run this once:
```bash
gh api -X POST repos/ap0l1on/totally-professional/pages -f build_type=workflow
```

## Preview the assets
```bash
python3 tools/dev_server.py
```
Then open http://localhost:8765/tools/preview.html (3D model/animation viewer, add `?cat=props&lineup=1&level=office`),
http://localhost:8765/tools/ui_sheet.html (logo + icons), or http://localhost:8765/tools/render_shots.html (re-renders `ui/renders/*.png`).
