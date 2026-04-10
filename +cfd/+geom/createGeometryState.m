function geometry_state = createGeometryState(cfg)
%CREATEGEOMETRYSTATE Initialize geometry processing state.

if nargin < 1
    cfg = cfd.config.defaultConfig();
end
cfg = cfd.config.validateConfig(cfg);

geometry_state = struct();
geometry_state.status = 'initialized';
geometry_state.error = '';
geometry_state.recovery_attempted = false;
geometry_state.created_utc = char(datetime('now', 'TimeZone', 'UTC', 'Format', 'yyyy-MM-dd''T''HH:mm:ss''Z'''));

geometry_state.raw = struct('points', zeros(0,2), 'segments', zeros(0,2), 'source', '');
geometry_state.poly = polyshape.empty(0,1);
geometry_state.fluid_region = polyshape.empty(0,1);
geometry_state.enclosure = polyshape.empty(0,1);
geometry_state.boundary_labels = struct('inlet', {{}}, 'outlet', {{}}, 'wall', {{}}, 'symmetry', {{}});
geometry_state.named_selections = struct();
geometry_state.rename_history = struct('from', {}, 'to', {}, 'timestamp_utc', {});
geometry_state.topology = struct('shared_vertex_tolerance', 1.0e-6, 'is_shared', false);
geometry_state.quality = struct('is_watertight', false, 'leaks', struct('count',0,'indices',[]), 'short_edges_fixed', 0);
geometry_state.metrics = struct('area', NaN, 'perimeter', NaN, 'bounding_box', [NaN NaN NaN NaN]);
geometry_state.flow_description = struct('inlet_speed', NaN, 'reference_length', NaN, 'reynolds_number', NaN);
geometry_state.pde_model = [];
geometry_state.debug = struct('figures', [], 'snapshots', {{}});
geometry_state.logs = {};
geometry_state.config_snapshot = cfg.geometry;
end
