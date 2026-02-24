# Project File Format
Top-level keys:
- `name`, `width`, `height`, `initial_temperature`
- `materials[]`: id, curves (`conductivity`, `heat_capacity`), `density`, optional `phase_change`
- `rectangles[]`: rectangle geometry, material assignment, priority, volumetric heat source
- `boundaries[]`: side, type, schedule (+h or resistance)
- `mesh`: nx/ny and optional nonuniform coordinates
- `solver`: steady/transient options
- `probes[]`
