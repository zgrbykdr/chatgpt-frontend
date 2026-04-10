function state = shareTopologyApprox(state, tolerance)
%SHARETOPOLOGYAPPROX Approximate shared topology via vertex snapping.

if nargin < 2 || isempty(tolerance)
    tolerance = 1e-6;
end
if ~isnumeric(tolerance) || ~isscalar(tolerance) || ~isfinite(tolerance) || tolerance <= 0
    error('cfd:geom:InvalidTolerance', 'tolerance must be positive finite scalar.');
end
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'poly') || isempty(state.poly)
    error('cfd:geom:MissingPoly', 'state.poly is required.');
end

v = state.poly.Vertices;
if size(v,1) < 3
    error('cfd:geom:InsufficientVertices', 'Need at least 3 vertices for topology sharing.');
end

vSnap = round(v / tolerance) * tolerance;
poly = polyshape(vSnap(:,1), vSnap(:,2), 'Simplify', true);
if area(poly) <= 0
    error('cfd:geom:TopologyShareFailed', 'Topology sharing produced invalid geometry.');
end

state.poly = poly;
state.topology.shared_vertex_tolerance = tolerance;
state.topology.is_shared = true;
state = cfd.geom.logGeometryEvent(state, 'INFO', sprintf('Shared topology with tolerance=%g', tolerance));
end
