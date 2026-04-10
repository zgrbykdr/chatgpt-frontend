function leaks = detectLeaks(state, tolerance)
%DETECTLEAKS Detect open-boundary leaks using raw segments and polygon closure.

if nargin < 2 || isempty(tolerance)
    tolerance = 1e-8;
end
if ~(isnumeric(tolerance) && isscalar(tolerance) && isfinite(tolerance) && tolerance > 0)
    error('cfd:geom:InvalidTolerance', 'tolerance must be positive finite scalar.');
end
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end

leakIdx = [];
if isfield(state, 'raw') && isstruct(state.raw) && isfield(state.raw, 'points') && ~isempty(state.raw.points)
    pts = state.raw.points;
    if norm(pts(1,:) - pts(end,:)) > tolerance
        leakIdx(end+1) = 1; %#ok<AGROW>
    end
end

if isfield(state, 'poly') && ~isempty(state.poly)
    v = state.poly.Vertices;
    if size(v,1) < 3 || area(state.poly) <= tolerance
        leakIdx(end+1) = 2; %#ok<AGROW>
    end
else
    leakIdx(end+1) = 3; %#ok<AGROW>
end

leaks = struct('count', numel(unique(leakIdx)), 'indices', unique(leakIdx));
end
