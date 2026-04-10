function mesh_state = MeshManager(cfg, geometry_state, options)
%MESHMANAGER Facade for meshing pipeline.

if nargin < 1
    cfg = cfd.config.defaultConfig();
end
if nargin < 2
    error('cfd:mesh:MissingGeometryState', 'geometry_state is required.');
end
if nargin < 3
    options = struct();
end

mesh_state = cfd.mesh.processMeshPipeline(cfg, geometry_state, options);
end
