function result = WorkflowController(caseInput, options)
%WORKFLOWCONTROLLER Full orchestration pipeline with resume/checkpoints.
% Stages: geometry, meshing, mesh quality, repair loop,
% solver setup, solve, postprocess.

if nargin < 2
    options = struct();
end
options = iNormalizeOptions(options);
logger = cfd.logging.Logger(options.log_path);

runState = struct();
runState.id = char(java.util.UUID.randomUUID);
runState.started_utc = char(datetime('now','TimeZone','UTC','Format','yyyy-MM-dd''T''HH:mm:ss''Z'''));
runState.completed_stages = {};
runState.stage = 'init';
runState.status = 'running';
runState.error = '';

try
    if options.resume && exist(options.checkpoint_path, 'file')
        logger.info(['Resuming from checkpoint: ' options.checkpoint_path]);
        runState = cfd.io.loadCheckpoint(options.checkpoint_path);
    end

    runState = cfd.app.StageRunner(runState, 'load_config', @(s) iStageLoadConfig(s, caseInput, options), logger, options.checkpoint_path);
    runState = cfd.app.StageRunner(runState, 'geometry', @iStageGeometry, logger, options.checkpoint_path);
    runState = cfd.app.StageRunner(runState, 'meshing', @iStageMeshing, logger, options.checkpoint_path);
    runState = cfd.app.StageRunner(runState, 'mesh_quality', @iStageMeshQuality, logger, options.checkpoint_path);
    runState = cfd.app.StageRunner(runState, 'repair_loop', @iStageRepairLoop, logger, options.checkpoint_path);
    runState = cfd.app.StageRunner(runState, 'solver_setup', @iStageSolverSetup, logger, options.checkpoint_path);
    runState = cfd.app.StageRunner(runState, 'solve', @iStageSolve, logger, options.checkpoint_path);
    runState = cfd.app.StageRunner(runState, 'postprocess', @(s) iStagePostprocess(s, options.output_dir), logger, options.checkpoint_path);

    runState.status = 'completed';
    runState.finished_utc = char(datetime('now','TimeZone','UTC','Format','yyyy-MM-dd''T''HH:mm:ss''Z'''));
    logger.info('Workflow completed successfully.');
catch ME
    runState.status = 'failed';
    runState.error = ME.message;
    runState.finished_utc = char(datetime('now','TimeZone','UTC','Format','yyyy-MM-dd''T''HH:mm:ss''Z'''));
    logger.error(['Workflow failed: ' ME.message]);

    runState.debug_bundle = cfd.app.exportDebugBundle(runState, options.debug_dir);
    if options.safe_termination
        logger.warn('Safe termination enabled; returning failure state without throwing.');
    else
        rethrow(ME);
    end
end

cfd.io.saveCheckpoint(options.checkpoint_path, runState);
result = runState;
end

function state = iStageLoadConfig(state, caseInput, options)
if isstruct(caseInput)
    cfg = cfd.config.loadConfig(caseInput, options.config_overrides, true);
else
    cfg = cfd.config.loadConfig(caseInput, options.config_overrides, true);
end
state.cfg = cfg;
end

function state = iStageGeometry(state)
if strcmp(state.cfg.geometry.mode, 'parametric') || isempty(strtrim(state.cfg.geometry.file_path))
    src = iDefaultParametricGeometry();
else
    src = state.cfg.geometry.file_path;
end
state.geometry_state = cfd.geom.processGeometryPipeline(state.cfg, src, struct('attempt_recovery', true));
end

function state = iStageMeshing(state)
state.mesh_state = cfd.mesh.processMeshPipeline(state.cfg, state.geometry_state, struct('workflow','watertight','auto_remesh',true));
end

function state = iStageMeshQuality(state)
state.quality_gate = cfd.quality.MeshQualityGate(state.mesh_state, cfd.quality.defaultQualityThresholds());
end

function state = iStageRepairLoop(state)
if state.quality_gate.pass
    state.repair_result = struct('pass', true, 'history', []);
    return;
end
state.repair_result = cfd.quality.MeshRepairEngine(state.mesh_state, state.cfg, state.geometry_state, struct());
state.mesh_state = state.repair_result.mesh_state;
state.quality_gate = state.repair_result.final_gate;
end

function state = iStageSolverSetup(state)
state.mesh_state = cfd.mesh.convertToFvTopology(state.mesh_state);
end

function state = iStageSolve(state)
state.solution = cfd.solver.PressureBasedSolver(state.cfg, state.mesh_state, struct());
end

function state = iStagePostprocess(state, outDir)
state.post = cfd.post.PostProcessor(state.cfg, state.mesh_state, state.solution, outDir);
end

function options = iNormalizeOptions(options)
if ~isstruct(options) || ~isscalar(options)
    error('cfd:app:InvalidOptions', 'options must be scalar struct.');
end
def = struct();
def.resume = false;
def.checkpoint_path = fullfile(pwd, 'checkpoints', 'latest_checkpoint.mat');
def.log_path = fullfile(pwd, 'logs', 'run.log');
def.debug_dir = fullfile(pwd, 'debug');
def.output_dir = fullfile(pwd, 'outputs');
def.safe_termination = true;
def.config_overrides = struct();
options = cfd.config.mergeConfig(def, options);
end

function src = iDefaultParametricGeometry()
% Default channel-like rectangle geometry for parametric mode.
pts = [0 0; 4 0; 4 1; 0 1; 0 0];
src = struct('points', pts, 'segments', [(1:4)' (2:5)']);
end
