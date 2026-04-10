function state = createEnclosure(state, paddingFactor)
%CREATEENCLOSURE Create rectangular enclosure around current geometry.

if nargin < 2 || isempty(paddingFactor)
    paddingFactor = 2.0;
end
if ~(isnumeric(paddingFactor) && isscalar(paddingFactor) && isfinite(paddingFactor) && paddingFactor > 1.0)
    error('cfd:geom:InvalidPadding', 'paddingFactor must be finite scalar > 1.0');
end
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'poly') || isempty(state.poly)
    error('cfd:geom:MissingPoly', 'state.poly is required.');
end

v = state.poly.Vertices;
xMin = min(v(:,1)); xMax = max(v(:,1));
yMin = min(v(:,2)); yMax = max(v(:,2));
dx = (xMax - xMin); dy = (yMax - yMin);
if dx <= 0 || dy <= 0
    error('cfd:geom:DegenerateBBox', 'Geometry bounding box is degenerate.');
end

padX = 0.5 * (paddingFactor - 1.0) * dx;
padY = 0.5 * (paddingFactor - 1.0) * dy;

x = [xMin-padX; xMax+padX; xMax+padX; xMin-padX];
y = [yMin-padY; yMin-padY; yMax+padY; yMax+padY];
enc = polyshape(x, y, 'Simplify', true);
if area(enc) <= area(state.poly)
    error('cfd:geom:EnclosureTooSmall', 'Enclosure area must exceed geometry area.');
end

state.enclosure = enc;
state = cfd.geom.logGeometryEvent(state, 'INFO', 'Enclosure geometry created.');
end
