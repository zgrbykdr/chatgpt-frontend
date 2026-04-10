function saveCheckpoint(checkpointPath, runState)
%SAVECHECKPOINT Save workflow checkpoint to MAT file atomically.

if ~(ischar(checkpointPath) || (isstring(checkpointPath) && isscalar(checkpointPath)))
    error('cfd:io:InvalidCheckpointPath', 'checkpointPath must be char/string scalar.');
end
checkpointPath = char(checkpointPath);
if ~isstruct(runState) || ~isscalar(runState)
    error('cfd:io:InvalidRunState', 'runState must be scalar struct.');
end

[d,~,~] = fileparts(checkpointPath);
if ~isempty(d) && ~exist(d,'dir')
    mkdir(d);
end

tmp = [checkpointPath '.tmp'];
state = runState; %#ok<NASGU>
save(tmp, 'state', '-mat');
movefile(tmp, checkpointPath, 'f');
end
