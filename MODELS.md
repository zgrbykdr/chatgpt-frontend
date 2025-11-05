# Mathematical Models

HeatPumpSim implements two primary component modeling granularities—Moving-Boundary (MB) and one-dimensional Finite Volume Method (FVM)—to resolve the dynamic behaviour of vapor compression cycles. The focus is on deterministic, energy-consistent formulations suitable for real-time simulation and rapid prototyping.

## Common Notation

| Symbol | Description |
| ------ | ----------- |
| $\dot m$ | Mass flow rate |
| $p$ | Pressure |
| $h$ | Specific enthalpy |
| $T$ | Temperature |
| $q''$ | Heat flux |
| $A$ | Heat transfer area |
| $L$ | Component length |
| $x$ | Vapor quality |
| $\alpha$ | Void fraction |
| $\rho$ | Density |
| $c_p$ | Specific heat at constant pressure |

Thermophysical properties are provided by CoolProp (or deterministic polynomial fallback) via the `FluidState` wrapper. All computations use SI units (Pa, K, kg/s, J/kg).

## Moving-Boundary Heat Exchanger

A moving-boundary (MB) evaporator or condenser is partitioned into three regions: subcooled, two-phase, and superheated/condensed. Region lengths $L_i$ satisfy

$$L = L_{\text{sc}} + L_{\text{tp}} + L_{\text{sh}}$$

with normalized fractions $f_i = L_i / L$. Energy balance per time step is enforced through

$$\mathcal{R}_E = \dot m (h_{\text{out}} - h_{\text{in}}) - \dot Q = 0$$

where $\dot Q = UA \Delta T_{\text{lm}}$ approximated with a linearized capacity relation. A soft relaxation updates the internal heat duty to minimize residuals. Region redistribution maintains $\sum f_i = 1$ while preventing negative fractions.

Two-phase properties leverage quality-based lookups:

$$h_{\text{sat}} = h(p, x), \quad T_{\text{sat}} = T(p, x)$$

with wall temperature $T_w$ driving the log-mean temperature difference. Drift-flux and Lockhart–Martinelli correlations are abstracted for future refinement; current implementation ensures smooth void fractions in $[0,1]$.

## Finite Volume Heat Exchanger

FVM discretizes the HX into $N$ control volumes on a staggered grid. For each cell $i$:

$$\rho_i c_{p,i} V_i \frac{dT_i}{dt} = \dot m c_{p,i} (T_{i-1} - T_i) + h_i A_i (T_{w,i} - T_i)$$

where $V_i$ is the control volume, and $h_i$ is a user-selectable heat-transfer coefficient (HTC). Semi-implicit time stepping updates cell temperatures:

$$T_i^{n+1} = T_i^n + \frac{\Delta t}{\rho_i c_{p,i} V_i} \left[ \dot m c_{p,i}(T_{i-1}^n - T_i^n) + h_i A_i (T_{w,i} - T_i^n) \right]$$

Exit enthalpy is derived from cell $N$, and the energy residual is computed against inlet enthalpy.

## Compressor Model

The compressor assumes an isentropic core with efficiency $\eta_{is}$:

1. Compute inlet state $(p_s, T_s)$ to obtain $h_s$ and $s_s$.
2. Isentropic discharge enthalpy $h_{2s} = h(p_d, s_s)$.
3. Actual work per unit mass:

$$w = \frac{h_{2s} - h_s}{\eta_{is}}$$

4. Outlet enthalpy $h_2 = h_s + w$ and temperature $T_2 = T(p_d, h_2)$.
5. Shaft power $\dot W = \dot m \, w$ and running coefficient of performance $\text{COP} = \frac{h_2 - h_s}{w}$.

Energy residual tracks $\dot m (h_2 - h_s) - \dot W$.

## Pump Model

The circulation pump uses Bernoulli head relationships:

$$\Delta p = \rho g H\left(\frac{n}{n_0}\right)^2$$

Power requirement is

$$\dot W = \frac{\dot m \Delta p}{\rho}$$

with outlet enthalpy incremented accordingly. The pump enforces non-negative mass flow and pressure rise.

## Expansion Valve

Mass flow through the valve follows a Cv formulation:

$$\dot m = C_v \phi(o) \frac{p_u - p_d}{\rho_u}$$

where $\phi(o)$ is a smoothed clamp of the opening fraction $o \in [0,1]$. Enthalpy is conserved (isenthalpic throttling). The model provides mass-flow feedback for control loops.

## PID Controller

A discrete PID controller with anti-windup integrator caps the control signal to $[u_{\min}, u_{\max}]$:

$$u_k = \text{clip}\left( K_p e_k + K_i \sum_{j=0}^k e_j \Delta t + K_d \frac{e_k - e_{k-1}}{\Delta t} \right)$$

## System Assembly

Projects are described by a JSON graph DSL validated via JSON Schema. Components are instantiated based on type and modeling granularity; all share a base `ComponentModel` interface with `initialize`, `step`, and `output` routines. The `SimulationManager` processes components sequentially, aggregates validation metrics, and publishes snapshots through WebSocket.

## Numerical Integration

The engine currently advances components with a deterministic fixed time step ($\Delta t = 1$ s by default) to maintain reproducibility. Residual-based relaxation ensures convergence without solving full nonlinear systems, allowing future upgrades to BDF2/Newton solvers.

## Thermophysical Properties

`FluidState` proxies CoolProp's `PropsSI` function:

- $h = \text{PropsSI}(\text{'H'}, T, p, \text{fluid})$
- $T = \text{PropsSI}(\text{'T'}, p, h, \text{fluid})$
- $\rho = \text{PropsSI}(\text{'D'}, T, p, \text{fluid})$

When CoolProp is unavailable, polynomial approximations supply deterministic values to keep unit tests portable. Saturation temperatures use $T(p, x=0.5)$ to approximate two-phase boundaries.

## Energy Balance & Validation

Every component reports an `energyResidual`. The `SimulationManager` aggregates these residuals and flags warnings if the total exceeds design thresholds. EN 14511 scenario tests assert that

$$|\dot Q_{\text{cond}} - \dot Q_{\text{evap}} - \dot W_{\text{comp}}| \le 0.5 |\dot Q_{\text{cond}}|$$

ensuring consistent thermal bookkeeping.
