function cfg = validateConfig(cfg)
%VALIDATECONFIG Validate and normalize CFD configuration.

if nargin < 1 || ~isstruct(cfg) || ~isscalar(cfg)
    error('cfd:config:InvalidConfig', 'Configuration must be a scalar struct.');
end

cfg = cfd.config.mergeConfig(cfd.config.defaultConfig(), cfg);

cfg.geometry = iValidateGeometry(cfg.geometry);
cfg.meshing = iValidateMeshing(cfg.meshing);
cfg.mesh_quality = iValidateMeshQuality(cfg.mesh_quality);
cfg.solver = iValidateSolver(cfg.solver);
cfg.turbulence = iValidateTurbulence(cfg.turbulence);
cfg.boundaries = iValidateBoundaries(cfg.boundaries);
cfg.materials = iValidateMaterials(cfg.materials);

if isfield(cfg, 'version')
    cfg.version = iValidateTextScalar(cfg.version, 'version', false);
else
    cfg.version = '1.0.0';
end

if isfield(cfg, 'created_utc')
    cfg.created_utc = iValidateTextScalar(cfg.created_utc, 'created_utc', false);
else
    cfg.created_utc = char(datetime('now', 'TimeZone', 'UTC', 'Format', 'yyyy-MM-dd''T''HH:mm:ss''Z'''));
end
end

function g = iValidateGeometry(g)
iRequireStruct(g, 'geometry');

validModes = {'parametric', 'import'};
g.mode = iValidateEnum(g.mode, 'geometry.mode', validModes);

g.file_path = iValidateTextScalar(g.file_path, 'geometry.file_path', true);
if strcmp(g.mode, 'import') && isempty(g.file_path)
    error('cfd:config:GeometryPathRequired', ...
        'geometry.file_path must be provided when geometry.mode is "import".');
end

g.scale = iValidatePositiveFiniteScalar(g.scale, 'geometry.scale');
end

function m = iValidateMeshing(m)
iRequireStruct(m, 'meshing');

m.global_size = iValidatePositiveFiniteScalar(m.global_size, 'meshing.global_size');
m.growth_rate = iValidateRangeFiniteScalar(m.growth_rate, 'meshing.growth_rate', 1.0, 5.0, false, true);

iRequireField(m, 'local_sizing_rules', 'meshing');
m.local_sizing_rules = iValidateLocalSizingRules(m.local_sizing_rules);

iRequireField(m, 'boundary_layer', 'meshing');
m.boundary_layer = iValidateBoundaryLayer(m.boundary_layer);
end

function rules = iValidateLocalSizingRules(rules)
if isempty(rules)
    rules = struct('name', {}, 'target_entities', {}, 'size', {}, 'growth_rate', {}, 'enabled', {});
    return;
end

if ~isstruct(rules)
    error('cfd:config:InvalidLocalSizingRules', 'meshing.local_sizing_rules must be a struct array.');
end

required = {'name', 'target_entities', 'size', 'growth_rate', 'enabled'};
for i = 1:numel(rules)
    for r = 1:numel(required)
        if ~isfield(rules(i), required{r})
            error('cfd:config:MissingLocalSizingRuleField', ...
                'meshing.local_sizing_rules(%d) missing field %s.', i, required{r});
        end
    end

    rules(i).name = iValidateTextScalar(rules(i).name, sprintf('meshing.local_sizing_rules(%d).name', i), false);

    if ischar(rules(i).target_entities) || (isstring(rules(i).target_entities) && isscalar(rules(i).target_entities))
        rules(i).target_entities = {char(rules(i).target_entities)};
    end
    if ~iscellstr(rules(i).target_entities) %#ok<ISCLSTR>
        error('cfd:config:InvalidLocalTargetEntities', ...
            'meshing.local_sizing_rules(%d).target_entities must be cellstr.', i);
    end
    if isempty(rules(i).target_entities)
        error('cfd:config:EmptyLocalTargetEntities', ...
            'meshing.local_sizing_rules(%d).target_entities cannot be empty.', i);
    end

    rules(i).size = iValidatePositiveFiniteScalar(rules(i).size, sprintf('meshing.local_sizing_rules(%d).size', i));
    rules(i).growth_rate = iValidateRangeFiniteScalar( ...
        rules(i).growth_rate, sprintf('meshing.local_sizing_rules(%d).growth_rate', i), 1.0, 5.0, false, true);
    rules(i).enabled = iValidateLogicalScalar(rules(i).enabled, sprintf('meshing.local_sizing_rules(%d).enabled', i));
end
end

function bl = iValidateBoundaryLayer(bl)
iRequireStruct(bl, 'meshing.boundary_layer');

bl.enabled = iValidateLogicalScalar(bl.enabled, 'meshing.boundary_layer.enabled');
bl.first_layer_thickness = iValidatePositiveFiniteScalar(bl.first_layer_thickness, 'meshing.boundary_layer.first_layer_thickness');
bl.growth_rate = iValidateRangeFiniteScalar(bl.growth_rate, 'meshing.boundary_layer.growth_rate', 1.0, 5.0, false, true);
bl.num_layers = iValidateIntegerRange(bl.num_layers, 'meshing.boundary_layer.num_layers', 1, 200);
bl.max_thickness_ratio = iValidateRangeFiniteScalar( ...
    bl.max_thickness_ratio, 'meshing.boundary_layer.max_thickness_ratio', 1e-6, 1.0, false, true);
end

function mq = iValidateMeshQuality(mq)
iRequireStruct(mq, 'mesh_quality');

mq.max_skewness = iValidateRangeFiniteScalar(mq.max_skewness, 'mesh_quality.max_skewness', 0.0, 1.0, true, true);
mq.min_orthogonal_quality = iValidateRangeFiniteScalar( ...
    mq.min_orthogonal_quality, 'mesh_quality.min_orthogonal_quality', 0.0, 1.0, true, true);
mq.max_aspect_ratio = iValidateRangeFiniteScalar(mq.max_aspect_ratio, 'mesh_quality.max_aspect_ratio', 1.0, 1e6, false, true);
end

function s = iValidateSolver(s)
iRequireStruct(s, 'solver');

s.time_mode = iValidateEnum(s.time_mode, 'solver.time_mode', {'steady', 'transient'});
s.solver_type = iValidateEnum(s.solver_type, 'solver.solver_type', {'SIMPLE', 'SIMPLEC', 'PISO'});

if strcmp(s.time_mode, 'steady') && strcmp(s.solver_type, 'PISO')
    error('cfd:config:InvalidSolverCombination', ...
        'solver_type "PISO" is only supported with solver.time_mode="transient".');
end
end

function t = iValidateTurbulence(t)
iRequireStruct(t, 'turbulence');

validModels = { ...
    'spalart_allmaras', ...
    'k_epsilon_standard', ...
    'k_epsilon_rng', ...
    'k_epsilon_realizable', ...
    'k_omega_standard', ...
    'k_omega_sst'};
t.model = iValidateEnum(t.model, 'turbulence.model', validModels);
end

function b = iValidateBoundaries(b)
iRequireStruct(b, 'boundaries');

b.inlet = iValidateInlet(b.inlet);
b.outlet = iValidateOutlet(b.outlet);
b.wall = iValidateWall(b.wall);
b.symmetry = iValidateSymmetry(b.symmetry);
end

function inlet = iValidateInlet(inlet)
iRequireStruct(inlet, 'boundaries.inlet');
inlet.type = iValidateEnum(inlet.type, 'boundaries.inlet.type', {'velocity_inlet'});

if ~(isnumeric(inlet.velocity) && isvector(inlet.velocity) && numel(inlet.velocity) == 2 && all(isfinite(inlet.velocity)))
    error('cfd:config:InvalidInletVelocity', 'boundaries.inlet.velocity must be a finite 1x2 numeric vector.');
end
inlet.velocity = double(inlet.velocity(:)).';

inlet.turbulence_intensity = iValidateRangeFiniteScalar( ...
    inlet.turbulence_intensity, 'boundaries.inlet.turbulence_intensity', 1e-6, 1.0, false, true);
inlet.length_scale = iValidatePositiveFiniteScalar(inlet.length_scale, 'boundaries.inlet.length_scale');
end

function outlet = iValidateOutlet(outlet)
iRequireStruct(outlet, 'boundaries.outlet');
outlet.type = iValidateEnum(outlet.type, 'boundaries.outlet.type', {'pressure_outlet'});
outlet.gauge_pressure = iValidateFiniteScalar(outlet.gauge_pressure, 'boundaries.outlet.gauge_pressure');
end

function wall = iValidateWall(wall)
iRequireStruct(wall, 'boundaries.wall');
wall.type = iValidateEnum(wall.type, 'boundaries.wall.type', {'no_slip'});
wall.roughness_height = iValidateNonNegativeFiniteScalar(wall.roughness_height, 'boundaries.wall.roughness_height');
wall.roughness_constant = iValidateRangeFiniteScalar(wall.roughness_constant, 'boundaries.wall.roughness_constant', 0.1, 1.0, true, true);
end

function symmetry = iValidateSymmetry(symmetry)
iRequireStruct(symmetry, 'boundaries.symmetry');
symmetry.type = iValidateEnum(symmetry.type, 'boundaries.symmetry.type', {'symmetry_plane'});
end

function m = iValidateMaterials(m)
iRequireStruct(m, 'materials');
m.density = iValidatePositiveFiniteScalar(m.density, 'materials.density');
m.viscosity = iValidatePositiveFiniteScalar(m.viscosity, 'materials.viscosity');
end

function iRequireField(s, fieldName, scope)
if ~isfield(s, fieldName)
    error('cfd:config:MissingField', 'Missing required field %s.%s.', scope, fieldName);
end
end

function iRequireStruct(s, name)
if ~isstruct(s) || ~isscalar(s)
    error('cfd:config:InvalidStruct', '%s must be a scalar struct.', name);
end
end

function v = iValidateEnum(v, name, allowed)
v = iValidateTextScalar(v, name, false);
if ~any(strcmp(v, allowed))
    error('cfd:config:InvalidEnum', '%s must be one of: %s.', name, strjoin(allowed, ', '));
end
end

function v = iValidateTextScalar(v, name, allowEmpty)
if isstring(v)
    if ~isscalar(v)
        error('cfd:config:InvalidText', '%s must be a scalar string/char.', name);
    end
    v = char(v);
elseif ~ischar(v)
    error('cfd:config:InvalidTextType', '%s must be a string/char.', name);
end
v = strtrim(v);
if ~allowEmpty && isempty(v)
    error('cfd:config:EmptyText', '%s cannot be empty.', name);
end
end

function v = iValidateFiniteScalar(v, name)
if ~(isnumeric(v) && isscalar(v) && isfinite(v))
    error('cfd:config:InvalidNumeric', '%s must be a finite numeric scalar.', name);
end
v = double(v);
end

function v = iValidatePositiveFiniteScalar(v, name)
v = iValidateFiniteScalar(v, name);
if ~(v > 0)
    error('cfd:config:NonPositive', '%s must be > 0.', name);
end
end

function v = iValidateNonNegativeFiniteScalar(v, name)
v = iValidateFiniteScalar(v, name);
if v < 0
    error('cfd:config:NegativeValue', '%s must be >= 0.', name);
end
end

function v = iValidateRangeFiniteScalar(v, name, minV, maxV, minInclusive, maxInclusive)
v = iValidateFiniteScalar(v, name);

if minInclusive
    minOk = (v >= minV);
else
    minOk = (v > minV);
end
if maxInclusive
    maxOk = (v <= maxV);
else
    maxOk = (v < maxV);
end

if ~(minOk && maxOk)
    if minInclusive
        minBracket = '[';
    else
        minBracket = '(';
    end
    if maxInclusive
        maxBracket = ']';
    else
        maxBracket = ')';
    end
    error('cfd:config:OutOfRange', '%s must be in range %s%g, %g%s.', name, minBracket, minV, maxV, maxBracket);
end
end

function v = iValidateIntegerRange(v, name, minV, maxV)
if ~(isnumeric(v) && isscalar(v) && isfinite(v) && (floor(v) == v))
    error('cfd:config:InvalidInteger', '%s must be an integer scalar.', name);
end
v = double(v);
if v < minV || v > maxV
    error('cfd:config:OutOfRangeInteger', '%s must be in [%d, %d].', name, minV, maxV);
end
end

function v = iValidateLogicalScalar(v, name)
if islogical(v) && isscalar(v)
    return;
end
if isnumeric(v) && isscalar(v) && any(v == [0, 1])
    v = logical(v);
    return;
end
error('cfd:config:InvalidLogical', '%s must be a logical scalar.', name);
end
