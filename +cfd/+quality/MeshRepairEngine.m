function result = MeshRepairEngine(mesh_state, cfg, geometry_state, options)
%MESHREPAIRENGINE Execute mesh quality repair loop with tracking.
% Includes:
% - smoothing
% - remeshing
% - local refinement
% - boundary layer adjustment
% - geometry simplification fallback
% - retry loop + max attempts + improvement tracking

if nargin < 4 || isempty(options)
    options = struct();
end

cfg = cfd.config.validateConfig(cfg);
if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:quality:InvalidMeshState', 'mesh_state must be scalar struct.');
end
if ~isstruct(geometry_state) || ~isscalar(geometry_state)
    error('cfd:quality:InvalidGeometryState', 'geometry_state must be scalar struct.');
end

options = iNormalizeOptions(options);
thresholds = options.thresholds;

history = repmat(struct('attempt',0,'action','','gate',struct(),'improvement',struct(),'status',''), 0, 1);
current = mesh_state;

currentGate = cfd.quality.MeshQualityGate(current, thresholds);
history(end+1) = struct('attempt',0,'action','initial','gate',currentGate, ...
    'improvement',struct('total_score',0), 'status',iStatus(currentGate.pass)); %#ok<AGROW>

for attempt = 1:options.max_attempts
    if currentGate.pass
        break;
    end

    prevGate = currentGate;
    action = iPickRepairAction(attempt, options);

    switch action
        case 'smoothing'
            current = cfd.mesh.smoothMesh(current, options.smoothing_iterations);
        case 'local_refinement'
            badIds = unique([prevGate.quality.degenerate_elements; prevGate.quality.inverted_elements]);
            if isempty(badIds)
                badIds = iWorstElements(prevGate.quality.skewness_equiangular, options.max_local_refine_elements);
            end
            current = cfd.mesh.localRefineMesh(current, badIds, options.use_parallel);
        case 'boundary_layer_adjustment'
            cfgAdj = cfg;
            cfgAdj.meshing.boundary_layer.growth_rate = max(1.05, cfg.meshing.boundary_layer.growth_rate*0.9);
            cfgAdj.meshing.boundary_layer.num_layers = max(2, round(cfg.meshing.boundary_layer.num_layers*0.9));
            current = cfd.mesh.generateBoundaryLayerMesh(current, cfgAdj);
            current = cfd.mesh.smoothMesh(current, max(2, floor(options.smoothing_iterations/2)));
        case 'remeshing'
            remeshOpts = struct('use_parallel', options.use_parallel);
            current = cfd.mesh.automaticRemesh(current, cfg, geometry_state, remeshOpts);
        case 'geometry_simplification_fallback'
            if ~isfield(geometry_state, 'poly') || isempty(geometry_state.poly)
                error('cfd:quality:NoGeometryForFallback', 'geometry_state.poly required for simplification fallback.');
            end
            g2 = geometry_state;
            g2 = cfd.geom.simplifyGeometry(g2, options.geometry_simplify_tolerance);
            current = cfd.mesh.generateSurfaceMesh(current, cfg, g2);
            current = cfd.mesh.generateVolumeMesh(current, cfg, g2, struct('use_parallel', options.use_parallel));
            current = cfd.mesh.smoothMesh(current, options.smoothing_iterations);
        otherwise
            error('cfd:quality:UnknownRepairAction', 'Unknown repair action: %s', action);
    end

    currentGate = cfd.quality.MeshQualityGate(current, thresholds);
    imp = cfd.quality.trackQualityImprovement(prevGate, currentGate);
    history(end+1) = struct('attempt',attempt,'action',action,'gate',currentGate, ...
        'improvement',imp,'status',iStatus(currentGate.pass)); %#ok<AGROW>

    if imp.total_score < thresholds.min_attempt_improvement && ~currentGate.pass
        % Force stronger repair on next step by escalating attempt index.
        continue;
    end
end

result = struct();
result.mesh_state = current;
result.final_gate = currentGate;
result.history = history;
result.pass = currentGate.pass;
result.attempts_used = numel(history)-1;
end

function options = iNormalizeOptions(options)
def = struct();
def.max_attempts = 6;
def.smoothing_iterations = 8;
def.max_local_refine_elements = 100;
def.geometry_simplify_tolerance = 5e-4;
def.use_parallel = false;
def.thresholds = cfd.quality.defaultQualityThresholds();

options = cfd.config.mergeConfig(def, options);
if ~(isnumeric(options.max_attempts) && isscalar(options.max_attempts) && options.max_attempts >= 1)
    error('cfd:quality:InvalidMaxAttempts', 'max_attempts must be >= 1');
end
if ~(isnumeric(options.smoothing_iterations) && isscalar(options.smoothing_iterations) && options.smoothing_iterations >= 1)
    error('cfd:quality:InvalidSmoothingIterations', 'smoothing_iterations must be >= 1');
end
if ~(isnumeric(options.max_local_refine_elements) && isscalar(options.max_local_refine_elements) && options.max_local_refine_elements >= 1)
    error('cfd:quality:InvalidMaxLocalRefine', 'max_local_refine_elements must be >= 1');
end
if ~(isnumeric(options.geometry_simplify_tolerance) && isscalar(options.geometry_simplify_tolerance) && options.geometry_simplify_tolerance > 0)
    error('cfd:quality:InvalidSimplifyTolerance', 'geometry_simplify_tolerance must be > 0');
end
end

function action = iPickRepairAction(attempt, options)
seq = {'smoothing','local_refinement','boundary_layer_adjustment','remeshing','smoothing','geometry_simplification_fallback'};
idx = min(attempt, numel(seq));
action = seq{idx};
if strcmp(action,'local_refinement') && options.max_local_refine_elements < 1
    action = 'smoothing';
end
end

function ids = iWorstElements(skewness, maxCount)
[~, idx] = sort(skewness, 'descend');
ids = idx(1:min(maxCount, numel(idx)));
end

function s = iStatus(pass)
if pass
    s = 'pass';
else
    s = 'fail';
end
end
