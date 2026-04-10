function state = createCappingSurfaces(state)
%CREATECAPPINGSURFACES Close small open gaps by endpoint capping.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'raw') || ~isstruct(state.raw) || ~isfield(state.raw, 'points')
    error('cfd:geom:MissingRawPoints', 'state.raw.points is required.');
end

pts = state.raw.points;
if isempty(pts)
    error('cfd:geom:EmptyPoints', 'No raw points available for capping.');
end

if norm(pts(1,:) - pts(end,:)) > 1.0e-10
    pts(end+1,:) = pts(1,:);
end

poly = polyshape(pts(:,1), pts(:,2), 'Simplify', true);
if area(poly) <= 0
    error('cfd:geom:CappingFailed', 'Capping produced invalid geometry area.');
end

state.poly = poly;
state.raw.points = pts;
state = cfd.geom.logGeometryEvent(state, 'INFO', 'Capping surfaces created/verified.');
end
