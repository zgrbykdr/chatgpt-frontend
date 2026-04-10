function state = mergeBodies(state, bodies)
%MERGEBODIES Merge multiple geometry bodies into a unified polyshape.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if nargin < 2 || isempty(bodies)
    if isfield(state, 'poly') && ~isempty(state.poly)
        bodies = state.poly;
    else
        error('cfd:geom:NoBodies', 'No bodies provided and state.poly is empty.');
    end
end

if isa(bodies, 'polyshape')
    merged = union(bodies);
elseif iscell(bodies)
    if isempty(bodies)
        error('cfd:geom:NoBodies', 'bodies cell cannot be empty.');
    end
    merged = bodies{1};
    for i = 2:numel(bodies)
        merged = union(merged, bodies{i});
    end
else
    error('cfd:geom:InvalidBodies', 'bodies must be polyshape or cell array of polyshape.');
end

if area(merged) <= 0
    error('cfd:geom:MergeFailed', 'Merging bodies produced invalid geometry area.');
end

state.poly = merged;
state = cfd.geom.logGeometryEvent(state, 'INFO', 'Merged geometry bodies.');
end
