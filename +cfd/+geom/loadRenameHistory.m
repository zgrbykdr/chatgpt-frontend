function state = loadRenameHistory(state, inputPath)
%LOADRENAMEHISTORY Load persisted rename history and apply map updates.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~(ischar(inputPath) || (isstring(inputPath) && isscalar(inputPath)))
    error('cfd:geom:InvalidInputPath', 'inputPath must be char/string scalar.');
end
inputPath = char(inputPath);
if ~exist(inputPath, 'file')
    error('cfd:geom:MissingFile', 'Rename history file does not exist: %s', inputPath);
end

[~,~,ext] = fileparts(inputPath);
switch lower(ext)
    case '.mat'
        raw = load(inputPath);
        if isfield(raw, 'rename_history')
            rh = raw.rename_history;
        else
            error('cfd:geom:InvalidMat', 'MAT file missing variable rename_history.');
        end
    case '.json'
        rh = jsondecode(fileread(inputPath));
    otherwise
        error('cfd:geom:UnsupportedFile', 'Use .mat or .json extension.');
end

if isempty(rh)
    return;
end
if ~isstruct(rh)
    error('cfd:geom:InvalidHistory', 'rename_history must be struct array.');
end

for i = 1:numel(rh)
    if isfield(rh(i), 'from') && isfield(rh(i), 'to') && isfield(state,'named_selections') ...
            && isfield(state.named_selections, rh(i).from) && ~isfield(state.named_selections, rh(i).to)
        state.named_selections.(rh(i).to) = state.named_selections.(rh(i).from);
        state.named_selections = rmfield(state.named_selections, rh(i).from);
    end
end
state.rename_history = rh;
state = cfd.geom.logGeometryEvent(state, 'INFO', sprintf('Loaded %d rename history entries.', numel(rh)));
end
