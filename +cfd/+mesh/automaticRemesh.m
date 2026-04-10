function mesh_state = automaticRemesh(mesh_state, cfg, geometry_state, options)
%AUTOMATICREMESH Rebuild mesh with adjusted size controls.

if nargin < 4
    options = struct();
end
cfg = cfd.config.validateConfig(cfg);
if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end

cfg2 = cfg;
cfg2.meshing.global_size = cfg.meshing.global_size * 0.9;
cfg2.meshing.growth_rate = min(max(cfg.meshing.growth_rate, 1.05), 1.5);

mesh_state.remesh_count = mesh_state.remesh_count + 1;
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'WARN', sprintf('Automatic remeshing pass %d', mesh_state.remesh_count));

mesh_state = cfd.mesh.generateSurfaceMesh(mesh_state, cfg2, geometry_state);
mesh_state = cfd.mesh.generateVolumeMesh(mesh_state, cfg2, geometry_state, options);
mesh_state = cfd.mesh.smoothMesh(mesh_state, 4);
end
