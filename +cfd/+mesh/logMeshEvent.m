function state = logMeshEvent(state, level, message)
%LOGMESHEVENT Append mesh event to mesh_state logs.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:mesh:InvalidState', 'state must be scalar struct.');
end
if ~(ischar(level) || (isstring(level) && isscalar(level)))
    error('cfd:mesh:InvalidLevel', 'level must be char/string scalar.');
end
if ~(ischar(message) || (isstring(message) && isscalar(message)))
    error('cfd:mesh:InvalidMessage', 'message must be char/string scalar.');
end

if ~isfield(state, 'logs') || ~iscell(state.logs)
    state.logs = {};
end
entry = struct('timestamp_utc', char(datetime('now','TimeZone','UTC','Format','yyyy-MM-dd''T''HH:mm:ss''Z''')), ...
               'level', upper(char(level)), 'message', char(message));
state.logs{end+1,1} = entry;
end
