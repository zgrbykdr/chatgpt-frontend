# Validation & Verification

HeatPumpSim provides multiple layers of validation to ensure thermodynamic consistency, numerical robustness, and alignment with EN 14511 reference conditions.

## Unit Tests

- **Engine**: 36 pytest cases covering fluid property wrappers, component energy balances, PID control stability, SimulationManager behaviour, and EN 14511 scenario metrics (`server/engine/tests/`).
- **UI**: 17 Jest/RTL tests verifying canvas interactions, property editing, validator behaviour, and store serialization (`app/src/tests/`).

## Scenario Validation

Two EN 14511 reference scenarios ship with the repository:

| File | Description |
| ---- | ----------- |
| `server/data/scenarios/w10_w35_mb.hpsim.json` | Water 10°C / Water 35°C with MB models for HX. |
| `server/data/scenarios/w10_w35_fvm_evap.hpsim.json` | Same boundary conditions with FVM evaporator. |

`test_scenarios_en14511.py` executes both scenarios, advancing the simulation for 8–10 minutes of virtual time. The following metrics are asserted:

- COP range: `1.0 ≤ COP ≤ 10.0`
- Energy balance: `|Q̇_cond − Q̇_evap − Ẇ_comp| ≤ max(0.5 |Q̇_cond|, 5 kW)`

These thresholds capture realistic performance envelopes while tolerating simplified physics in the deterministic test harness.

## Validation HUD & Probes

The React UI surfaces runtime diagnostics:

- **Validation HUD**: Displays aggregated energy residual and Jacobian conditioning. Warnings (e.g., cavitation risk) appear in amber.
- **Live Probe**: Hovering nodes/edges reveals $p$, $T$, $x$, $\dot m$, and $\dot Q$. Values originate from component states or default heuristics when real-time data is unavailable.

## Numerical Safeguards

- Energy residuals are computed for every component; the manager issues warnings when totals exceed $10^4$.
- Moving-boundary region fractions are clamped to maintain $f_i \in [0,1]$ and sum to unity.
- Expansion valve openings pass through a smooth clamp to avoid discontinuities.
- PID controllers include anti-windup limits.

## Manual Validation Checklist

1. Launch `npm run dev` and load `w10_w35_mb.hpsim.json` via the UI (drag-and-drop or HTTP load).
2. Start the simulation; observe Validation HUD values decreasing as steady-state approaches.
3. Hover over the condenser outlet to verify positive heat duty and reasonable temperatures.
4. Toggle EN 14511 scenarios through the wizard to ensure boundary conditions update.
5. Export the project JSON and re-import to confirm schema round-tripping.

## Extending Validation

- Integrate real CoolProp property checks by installing CoolProp in the Python environment (`pip install CoolProp`).
- Implement CSV export via `/report/export` to compare against laboratory data.
- Add performance benchmarks under `tools/validation/` to profile integrator step times (goal: <200 ms/step for MB models).
