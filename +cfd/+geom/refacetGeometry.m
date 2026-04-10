function state = refacetGeometry(state, targetEdgeLength)
%REFACETGEOMETRY Re-sample geometry boundary facets to target edge length.

if nargin < 2 || isempty(targetEdgeLength)
    targetEdgeLength = 0.01;
end
if ~(isnumeric(targetEdgeLength) && isscalar(targetEdgeLength) && isfinite(targetEdgeLength) && targetEdgeLength > 0)
    error('cfd:geom:InvalidTargetEdgeLength', 'targetEdgeLength must be positive finite scalar.');
end
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'poly') || isempty(state.poly)
    error('cfd:geom:MissingPoly', 'state.poly is required.');
end

v = state.poly.Vertices;
if size(v,1) < 3
    error('cfd:geom:InsufficientVertices', 'Geometry must have at least 3 vertices.');
end
if norm(v(1,:) - v(end,:)) > 0
    v(end+1,:) = v(1,:);
end

newV = zeros(0,2);
for i = 1:(size(v,1)-1)
    p1 = v(i,:); p2 = v(i+1,:);
    L = norm(p2 - p1);
    n = max(1, ceil(L / targetEdgeLength));
    t = linspace(0,1,n+1)';
    seg = p1 + (p2 - p1).*t;
    if i > 1
        seg = seg(2:end,:);
    end
    newV = [newV; seg]; %#ok<AGROW>
end

poly = polyshape(newV(:,1), newV(:,2), 'Simplify', true);
if area(poly) <= 0
    error('cfd:geom:RefacetFailed', 'Refaceting generated invalid geometry.');
end

state.poly = poly;
state = cfd.geom.logGeometryEvent(state, 'INFO', sprintf('Refaceted geometry with target edge length=%g', targetEdgeLength));
end
