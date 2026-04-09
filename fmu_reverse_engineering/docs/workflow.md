# Workflow

## Stage graph

1. Inspect FMU
2. Build variable catalog + dependency graph
3. Infer ranges and valid region priors
4. Plan experiments (screening + DOE + adaptive)
5. Execute simulation batches
6. Clean/label/engineer data
7. Influence and sensitivity analysis
8. Progressive model search
9. Regime discovery (if needed)
10. LUT/dynamic fallback (if needed)
11. Evaluate and rank candidates
12. Select and export final models
13. Generate reports

## Modes

- **Automatic**: everything inferred.
- **Semi-automatic**: apply user overrides and priorities.
- **Manual**: user provides experiment/model constraints.
