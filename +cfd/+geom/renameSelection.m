function state = renameSelection(state, fromName, toName)
%RENAMESELECTION Persistently rename a named selection.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
fromName = iName(fromName, 'fromName');
toName = iName(toName, 'toName');

if ~isfield(state, 'named_selections') || ~isstruct(state.named_selections)
    state.named_selections = struct();
end
if ~isfield(state.named_selections, fromName)
    error('cfd:geom:MissingSelection', 'Selection %s does not exist.', fromName);
end
if isfield(state.named_selections, toName)
    error('cfd:geom:SelectionExists', 'Selection %s already exists.', toName);
end

state.named_selections.(toName) = state.named_selections.(fromName);
state.named_selections = rmfield(state.named_selections, fromName);

entry = struct('from', fromName, 'to', toName, ...
    'timestamp_utc', char(datetime('now','TimeZone','UTC','Format','yyyy-MM-dd''T''HH:mm:ss''Z''')));
if ~isfield(state, 'rename_history') || ~isstruct(state.rename_history)
    state.rename_history = entry;
else
    state.rename_history(end+1) = entry;
end

state = cfd.geom.logGeometryEvent(state, 'INFO', sprintf('Renamed selection %s -> %s', fromName, toName));
end

function n = iName(v, field)
if isstring(v)
    if ~isscalar(v); error('cfd:geom:InvalidName', '%s must be scalar text.', field); end
    v = char(v);
end
if ~ischar(v)
    error('cfd:geom:InvalidNameType', '%s must be char/string.', field);
end
n = matlab.lang.makeValidName(strtrim(v));
if isempty(n)
    error('cfd:geom:EmptyName', '%s cannot be empty.', field);
end
end
