function state = repairTopology(state)
%REPAIRTOPOLOGY Repair self-intersections and normalize orientation.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'poly') || isempty(state.poly)
    error('cfd:geom:MissingPoly', 'state.poly is required.');
end

poly = rmholes(state.poly);
poly = union(poly);
poly = simplify(poly);

if area(poly) <= 0
    error('cfd:geom:RepairTopologyFailed', 'Topology repair produced invalid area.');
end

state.poly = poly;
state = cfd.geom.logGeometryEvent(state, 'INFO', 'Topology repair completed.');
end
