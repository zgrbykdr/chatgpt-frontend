function mesh_state = repairBadElements(mesh_state, cfg, geometry_state, options)
%REPAIRBADELEMENTS Repair bad elements via smoothing, local refine, remesh.

if nargin < 4
    options = struct('quality_repair_iterations', 2, 'use_parallel', false, 'auto_remesh', true);
end
cfg = cfd.config.validateConfig(cfg);
if isempty(mesh_state.elements)
    return;
end

if ~isfield(mesh_state.quality, 'bad_element_ids') || isempty(mesh_state.quality.bad_element_ids)
    mesh_state = cfd.mesh.detectBadElements(mesh_state, cfg.mesh_quality);
end

for it = 1:options.quality_repair_iterations
    bad = mesh_state.quality.bad_element_ids;
    if isempty(bad)
        break;
    end
    mesh_state = cfd.mesh.localRefineMesh(mesh_state, bad, options.use_parallel);
    mesh_state = cfd.mesh.smoothMesh(mesh_state, 3);
    mesh_state = cfd.mesh.computeMeshMetrics(mesh_state);
    mesh_state = cfd.mesh.detectBadElements(mesh_state, cfg.mesh_quality);
end

if ~isempty(mesh_state.quality.bad_element_ids) && options.auto_remesh
    mesh_state = cfd.mesh.automaticRemesh(mesh_state, cfg, geometry_state, options);
    mesh_state = cfd.mesh.computeMeshMetrics(mesh_state);
    mesh_state = cfd.mesh.detectBadElements(mesh_state, cfg.mesh_quality);
end

mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', 'Bad element repair complete.');
end
