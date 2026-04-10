function state = updateBoundaries(state, boundaryMap)
%UPDATEBOUNDARIES Update boundary labels and named selections.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isstruct(boundaryMap) || ~isscalar(boundaryMap)
    error('cfd:geom:InvalidBoundaryMap', 'boundaryMap must be scalar struct.');
end

required = {'inlet','outlet','wall','symmetry'};
for i = 1:numel(required)
    fn = required{i};
    if ~isfield(boundaryMap, fn)
        error('cfd:geom:MissingBoundaryField', 'Missing boundary field: %s', fn);
    end
    val = boundaryMap.(fn);
    if ischar(val); val = {val}; end
    if isstring(val) && isscalar(val); val = {char(val)}; end
    if ~iscellstr(val) %#ok<ISCLSTR>
        error('cfd:geom:InvalidBoundarySelection', 'boundaryMap.%s must be cellstr.', fn);
    end
    state.boundary_labels.(fn) = val;
end

state.named_selections = cfd.geom.setNamedSelections(state.named_selections, state.boundary_labels);
state = cfd.geom.logGeometryEvent(state, 'INFO', 'Boundary labels updated.');
end
