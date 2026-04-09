# FMU Reverse Engineering Studio

FMU Reverse Engineering Studio is a production-oriented MATLAB/Simulink desktop application for reverse engineering complex FMUs into interpretable equations, dynamic surrogate models, ML regressors, and lookup table fallbacks.

## Key capabilities
- FMU import, metadata extraction, variable cataloging
- Automatic/semi-automatic/manual workflow modes
- Range inference with safe probing and user override support
- Experiment planning and simulation campaign execution
- Behavior diagnostics (nonlinearity, delay, saturation, regime hints)
- Multi-family model fitting and fallback orchestration
- Validation, scoring, and ranked model selection
- Export to MATLAB code, Simulink artifacts, reports, and manifests

## Entry points
- Main app: `app/FMUReverseEngineeringStudioApp.m`
- Automated workflow script: `scripts/run_full_workflow.m`
- Demo script: `examples/demo_quickstart.m`

## Toolboxes
- Simulink
- System Identification Toolbox
- Curve Fitting Toolbox
- Statistics and Machine Learning Toolbox
- Simulink Design Optimization
- Global Optimization Toolbox
- Symbolic Math Toolbox
- Parallel Computing Toolbox

## Notes
FMU interaction details can differ by MATLAB release and FMU standard variant. The `+fmu/FMUInspector` and `+simulation/FMUSimulator` adapters isolate these environment-specific details with practical fallback behavior.
