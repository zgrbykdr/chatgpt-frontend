function output = runMeshQualitySystem(mesh_state, cfg, geometry_state, options)
%RUNMESHQUALITYSYSTEM Analyze, gate, repair, and re-gate mesh quality.

if nargin < 4
    options = struct();
end

initGate = cfd.quality.MeshQualityGate(mesh_state, cfd.quality.defaultQualityThresholds());
repair = cfd.quality.MeshRepairEngine(mesh_state, cfg, geometry_state, options);
finalGate = repair.final_gate;

output = struct();
output.initial_gate = initGate;
output.repair = repair;
output.final_gate = finalGate;
output.pass = finalGate.pass;
output.initial_report = initGate.report;
output.final_report = finalGate.report;
end
