function state = repairShortEdges(state, minEdgeLength)
%REPAIRSHORTEDGES Collapse edges shorter than threshold.

if nargin < 2 || isempty(minEdgeLength)
    minEdgeLength = 1e-5;
end
if ~(isnumeric(minEdgeLength) && isscalar(minEdgeLength) && isfinite(minEdgeLength) && minEdgeLength > 0)
    error('cfd:geom:InvalidMinEdgeLength', 'minEdgeLength must be positive finite scalar.');
end
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'poly') || isempty(state.poly)
    error('cfd:geom:MissingPoly', 'state.poly is required.');
end

v = state.poly.Vertices;
if isempty(v)
    error('cfd:geom:EmptyVertices', 'No vertices available for short-edge repair.');
end
if norm(v(1,:)-v(end,:)) > 0
    v(end+1,:) = v(1,:);
end

keep = true(size(v,1),1);
fixCount = 0;
for i = 1:(size(v,1)-1)
    if norm(v(i+1,:) - v(i,:)) < minEdgeLength
        keep(i+1) = false;
        fixCount = fixCount + 1;
    end
end

v2 = v(keep,:);
if size(v2,1) < 4
    error('cfd:geom:RepairCollapsed', 'Short edge repair collapsed geometry below minimum vertices.');
end
poly = polyshape(v2(:,1), v2(:,2), 'Simplify', true);
if area(poly) <= 0
    error('cfd:geom:RepairInvalidArea', 'Short edge repair produced invalid area.');
end

state.poly = poly;
state.quality.short_edges_fixed = fixCount;
state = cfd.geom.logGeometryEvent(state, 'INFO', sprintf('Short edge repair fixed %d edges.', fixCount));
end
