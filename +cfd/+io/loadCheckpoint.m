function runState = loadCheckpoint(checkpointPath)
%LOADCHECKPOINT Load workflow checkpoint state.

if ~(ischar(checkpointPath) || (isstring(checkpointPath) && isscalar(checkpointPath)))
    error('cfd:io:InvalidCheckpointPath', 'checkpointPath must be char/string scalar.');
end
checkpointPath = char(checkpointPath);
if ~exist(checkpointPath, 'file')
    error('cfd:io:CheckpointNotFound', 'Checkpoint not found: %s', checkpointPath);
end

raw = load(checkpointPath, '-mat');
if ~isfield(raw, 'state') || ~isstruct(raw.state)
    error('cfd:io:InvalidCheckpoint', 'Checkpoint file missing struct variable "state".');
end
runState = raw.state;
end
