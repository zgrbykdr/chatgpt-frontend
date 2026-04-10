function mesh_state = createMeshState(cfg, geometry_state)
%CREATEMESHSTATE Initialize mesh state container.

if nargin < 1
    cfg = cfd.config.defaultConfig();
end
cfg = cfd.config.validateConfig(cfg);
if nargin < 2
    geometry_state = struct();
end
if ~isstruct(geometry_state)
    error('cfd:mesh:InvalidGeometryState', 'geometry_state must be struct.');
end

mesh_state = struct();
mesh_state.status = 'initialized';
mesh_state.error = '';
mesh_state.created_utc = char(datetime('now','TimeZone','UTC','Format','yyyy-MM-dd''T''HH:mm:ss''Z'''));
mesh_state.workflow = 'watertight';
mesh_state.retry_count = 0;
mesh_state.remesh_count = 0;

mesh_state.nodes = zeros(0,2);
mesh_state.elements = zeros(0,3);
mesh_state.boundary_edges = zeros(0,2);
mesh_state.interior_edges = zeros(0,2);
mesh_state.boundary_layer = struct('nodes', zeros(0,2), 'elements', zeros(0,3), 'num_layers', 0);
mesh_state.size_field = struct('global_size', cfg.meshing.global_size, 'point_size', zeros(0,1));
mesh_state.quality = struct('skewness', zeros(0,1), 'orthogonal_quality', zeros(0,1), ...
    'aspect_ratio', zeros(0,1), 'max_skewness', NaN, 'min_orthogonal_quality', NaN, 'max_aspect_ratio', NaN, 'bad_element_ids', []);
mesh_state.fv = struct('face_nodes', zeros(0,2), 'cell_faces', {{}}, 'cell_centers', zeros(0,2), 'cell_areas', zeros(0,1));
mesh_state.logs = {};
mesh_state.geometry_snapshot = geometry_state;
mesh_state.config_snapshot = cfg.meshing;
end
