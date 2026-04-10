function state = validateWatertight(state, tolerance)
%VALIDATEWATERTIGHT Validate geometry watertightness and record diagnostics.

if nargin < 2 || isempty(tolerance)
    tolerance = 1e-8;
end
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end

leaks = cfd.geom.detectLeaks(state, tolerance);
isTight = (leaks.count == 0);

if ~isfield(state, 'quality') || ~isstruct(state.quality)
    state.quality = struct();
end
state.quality.leaks = leaks;
state.quality.is_watertight = isTight;

if isTight
    state = cfd.geom.logGeometryEvent(state, 'INFO', 'Watertight validation passed.');
else
    state = cfd.geom.logGeometryEvent(state, 'WARN', sprintf('Watertight validation failed with %d leak indicators.', leaks.count));
end
end
