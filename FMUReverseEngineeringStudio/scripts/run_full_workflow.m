% run_full_workflow - one-command automatic workflow.
root = fileparts(fileparts(mfilename('fullpath')));
addpath(genpath(fullfile(root,'src')),'-begin');
logger = logging.Logger(fullfile(root,'logs'));
pm = project.ProjectManager(root, logger);

% Update with real FMU path.
fmuPath = fullfile(root,'examples','sample.fmu');
if ~isfile(fmuPath)
    warning('No sample FMU found. Create examples/sample.fmu or choose from app UI.');
else
    pm.loadFMU(fmuPath);
    wf = appcore.WorkflowManager(pm,logger);
    result = wf.run('automatic'); %#ok<NASGU>
end
