function state = simplifyGeometry(state, tolerance)
%SIMPLIFYGEOMETRY Simplify geometry vertices using reducepoly.

if nargin < 2 || isempty(tolerance)
    tolerance = 1e-4;
end
if ~(isnumeric(tolerance) && isscalar(tolerance) && isfinite(tolerance) && tolerance > 0)
    error('cfd:geom:InvalidTolerance', 'tolerance must be positive finite scalar.');
end
if ~isstruct(state) || ~isscalar(state) || ~isfield(state,'poly') || isempty(state.poly)
    error('cfd:geom:InvalidState', 'Valid state.poly is required.');
end

v = state.poly.Vertices;
if size(v,1) < 4
    return;
end
if norm(v(1,:) - v(end,:)) > 0
    v(end+1,:) = v(1,:);
end

v2 = reducepoly(v, tolerance);
if size(v2,1) < 4
    error('cfd:geom:SimplifyTooAggressive', 'Simplification removed too many vertices.');
end
poly = polyshape(v2(:,1), v2(:,2), 'Simplify', true);
if area(poly) <= 0
    error('cfd:geom:InvalidSimplifiedArea', 'Simplified geometry has invalid area.');
end

state.poly = poly;
state = cfd.geom.logGeometryEvent(state, 'INFO', sprintf('Geometry simplified with tolerance=%g.', tolerance));
end
