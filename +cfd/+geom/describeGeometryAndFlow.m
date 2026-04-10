function state = describeGeometryAndFlow(state, cfg)
%DESCRIBEGEOMETRYANDFLOW Compute geometric and flow reference metrics.

if nargin < 2
    cfg = cfd.config.defaultConfig();
end
cfg = cfd.config.validateConfig(cfg);
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'poly') || isempty(state.poly)
    error('cfd:geom:MissingPoly', 'state.poly is required.');
end

poly = state.poly;
a = area(poly);
p = perimeter(poly);
verts = poly.Vertices;

if isempty(verts)
    error('cfd:geom:EmptyVertices', 'Geometry has no vertices.');
end

bbox = [min(verts(:,1)) max(verts(:,1)) min(verts(:,2)) max(verts(:,2))];
charLength = sqrt(4*a/pi);
uIn = norm(cfg.boundaries.inlet.velocity);
Re = cfg.materials.density * uIn * charLength / cfg.materials.viscosity;

state.metrics.area = a;
state.metrics.perimeter = p;
state.metrics.bounding_box = bbox;
state.flow_description = struct( ...
    'inlet_speed', uIn, ...
    'reference_length', charLength, ...
    'reynolds_number', Re);
state = cfd.geom.logGeometryEvent(state, 'INFO', sprintf('Geometry area=%.6g, Re=%.6g', a, Re));
end
