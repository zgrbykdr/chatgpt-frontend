# AetherForge Cartographer (Python)

Professional-grade RPG world map generation prototype with a dark dockable UI and simulation-centric rendering pipeline.

## Highlights

- 16K-ready generation controls (up to `16384 x 16384`) and infinite-canvas scene navigation.
- Zoom support up to 800% in the viewport.
- Non-destructive conceptual layer stack and simulation paneling.
- Tectonic heightmap synthesis, erosion simulation, river generation, and climate-informed biomes.
- 500+ terrain color presets (`512` currently generated) for stylized map workflows.
- Export targets for production workflows:
  - Cinematic map preview PNG
  - 16-bit heightmap PNG for Unreal/Unity terrain pipelines

## Run

```bash
python3 -m pip install -r requirements.txt
python3 rpg_map_studio.py
```

### Batch demo output (headless)

```bash
python3 rpg_map_studio.py --generate-demo
```

This writes:

- `output/demo_world.png`
- `output/demo_height_16bit.png`

## Notes

This implementation is designed as a robust starting point for a commercial toolchain architecture. It includes the generation backbone and a professional editor shell that can be extended with GPU shaders, real-time weather animation, procedural settlement growth logic, and game-engine export adapters.
