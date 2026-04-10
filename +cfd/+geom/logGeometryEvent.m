function state = logGeometryEvent(state, level, message)
%LOGGEOMETRYEVENT Append a log event to geometry state.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be a scalar struct.');
end
if ~(ischar(level) || (isstring(level) && isscalar(level)))
    error('cfd:geom:InvalidLevel', 'level must be char or scalar string.');
end
if ~(ischar(message) || (isstring(message) && isscalar(message)))
    error('cfd:geom:InvalidMessage', 'message must be char or scalar string.');
end

if ~isfield(state, 'logs') || ~iscell(state.logs)
    state.logs = {};
end

entry = struct();
entry.timestamp_utc = char(datetime('now', 'TimeZone', 'UTC', 'Format', 'yyyy-MM-dd''T''HH:mm:ss''Z'''));
entry.level = upper(char(level));
entry.message = char(message);
state.logs{end+1,1} = entry;
end
