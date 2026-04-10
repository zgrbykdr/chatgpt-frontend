function runState = StageRunner(runState, stageName, stageFn, logger, checkpointPath)
%STAGERUNNER Execute stage with logging and checkpoint write.

if ~isstruct(runState) || ~isscalar(runState)
    error('cfd:app:InvalidRunState', 'runState must be scalar struct.');
end
if ~(ischar(stageName) || (isstring(stageName) && isscalar(stageName)))
    error('cfd:app:InvalidStageName', 'stageName must be char/string scalar.');
end
if ~isa(stageFn, 'function_handle')
    error('cfd:app:InvalidStageFunction', 'stageFn must be function_handle.');
end

stageName = char(stageName);
logger.info(['Starting stage: ' stageName]);
runState.stage = stageName;
runState.last_stage_started_utc = char(datetime('now','TimeZone','UTC','Format','yyyy-MM-dd''T''HH:mm:ss''Z'''));

runState = stageFn(runState);

runState.completed_stages{end+1,1} = stageName;
runState.last_stage_completed_utc = char(datetime('now','TimeZone','UTC','Format','yyyy-MM-dd''T''HH:mm:ss''Z'''));
logger.info(['Completed stage: ' stageName]);

if nargin >= 5 && ~isempty(checkpointPath)
    cfd.io.saveCheckpoint(checkpointPath, runState);
    logger.info(['Checkpoint saved after stage: ' stageName]);
end
end
