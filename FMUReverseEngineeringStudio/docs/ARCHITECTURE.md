# Architecture

Layers:
1. Presentation/UI (`app/`)
2. Application orchestration (`src/+appcore`, `src/+project`)
3. Domain engines (`src/+ranges`, `src/+experiments`, `src/+analysis`, `src/+models`, `src/+validation`)
4. Infrastructure adapters (`src/+fmu`, `src/+simulation`, `src/+exporter`, `src/+logging`, `src/+config`)

Fallback chain:
`equation.simple -> equation.rich -> equation.sparse -> piecewise -> dynamic -> statistical -> lut`
