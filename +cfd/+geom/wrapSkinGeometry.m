function state = wrapSkinGeometry(state, alphaRadius)
%WRAPSKINGEOMETRY Wrap geometry using alphaShape and rebuild polyshape skin.

if nargin < 2 || isempty(alphaRadius)
    alphaRadius = NaN;
end
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'poly') || isempty(state.poly)
    error('cfd:geom:MissingPoly', 'state.poly is required.');
end

v = state.poly.Vertices;
if size(v,1) < 4
    error('cfd:geom:InsufficientVertices', 'Need >=4 vertices for alpha-shape wrapping.');
end

if isnan(alphaRadius)
    ash = alphaShape(v(:,1), v(:,2));
else
    if ~(isnumeric(alphaRadius) && isscalar(alphaRadius) && isfinite(alphaRadius) && alphaRadius > 0)
        error('cfd:geom:InvalidAlphaRadius', 'alphaRadius must be positive finite scalar.');
    end
    ash = alphaShape(v(:,1), v(:,2), alphaRadius);
end

[bf, pts] = boundaryFacets(ash);
if isempty(bf)
    error('cfd:geom:WrapFailed', 'alphaShape returned empty boundary facets.');
end

boundaryIdx = unique(bf(:));
bv = pts(boundaryIdx, :);
k = convhull(bv(:,1), bv(:,2));
poly = polyshape(bv(k,1), bv(k,2), 'Simplify', true);

if area(poly) <= 0
    error('cfd:geom:WrapInvalidArea', 'Wrapped skin has non-positive area.');
end

state.poly = poly;
state = cfd.geom.logGeometryEvent(state, 'INFO', 'Wrapped/skinned geometry using alphaShape.');
end
