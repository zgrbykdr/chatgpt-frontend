function selections = setNamedSelections(selections, updates)
%SETNAMEDSELECTIONS Create/update named selections map.

if nargin < 1 || isempty(selections)
    selections = struct();
end
if ~isstruct(selections) || ~isscalar(selections)
    error('cfd:geom:InvalidSelections', 'selections must be scalar struct.');
end
if ~isstruct(updates) || ~isscalar(updates)
    error('cfd:geom:InvalidUpdates', 'updates must be scalar struct.');
end

fns = fieldnames(updates);
for i = 1:numel(fns)
    name = fns{i};
    value = updates.(name);
    if ischar(value)
        value = {value};
    elseif isstring(value) && isscalar(value)
        value = {char(value)};
    end
    if ~iscellstr(value) %#ok<ISCLSTR>
        error('cfd:geom:InvalidSelectionValue', 'Selection %s must be cellstr.', name);
    end
    selections.(name) = value;
end
end
