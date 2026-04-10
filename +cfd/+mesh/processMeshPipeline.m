function mesh_state = processMeshPipeline(cfg, geometry_state, options)
%PROCESSMESHPIPELINE Execute meshing workflows (watertight/fault-tolerant).

if nargin < 1
    cfg = cfd.config.defaultConfig();
end
if nargin < 2
    error('cfd:mesh:MissingGeometryState', 'geometry_state is required.');
end
if nargin < 3
    options = struct();
end

cfg = cfd.config.validateConfig(cfg);
options = iNormalizeOptions(options);
mesh_state = cfd.mesh.createMeshState(cfg, geometry_state);
mesh_state.workflow = options.workflow;
mesh_state.status = 'running';

stages = {@iStageSurface, @iStageVolume, @iStageBoundaryLayer, @iStageSizing, ...
          @iStageCurvature, @iStageProximity, @iStageGrowthControl, @iStageSmooth, ...
          @iStageQuality, @iStageRepair, @iStageFv};

for i = 1:numel(stages)
    try
        mesh_state = stages{i}(mesh_state, cfg, geometry_state, options);
    catch ME
        mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'ERROR', sprintf('Stage %d failed: %s', i, ME.message));
        [mesh_state, recovered] = iRetry(mesh_state, cfg, geometry_state, options, i);
        if ~recovered
            mesh_state.status = 'failed';
            mesh_state.error = ME.message;
            rethrow(ME);
        end
    end
end

mesh_state.status = 'completed';
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', 'Meshing pipeline completed.');
end

function options = iNormalizeOptions(options)
if ~isstruct(options) || ~isscalar(options)
    error('cfd:mesh:InvalidOptions', 'options must be scalar struct.');
end
options = cfd.config.mergeConfig(struct( ...
    'workflow', 'watertight', ...
    'max_retries', 2, ...
    'use_parallel', false, ...
    'quality_repair_iterations', 3, ...
    'auto_remesh', true), options);

if ~any(strcmp(options.workflow, {'watertight','fault_tolerant'}))
    error('cfd:mesh:InvalidWorkflow', 'workflow must be watertight or fault_tolerant.');
end
end

function mesh_state = iStageSurface(mesh_state, cfg, geometry_state, ~)
mesh_state = cfd.mesh.generateSurfaceMesh(mesh_state, cfg, geometry_state);
end
function mesh_state = iStageVolume(mesh_state, cfg, geometry_state, options)
mesh_state = cfd.mesh.generateVolumeMesh(mesh_state, cfg, geometry_state, options);
end
function mesh_state = iStageBoundaryLayer(mesh_state, cfg, ~, ~)
mesh_state = cfd.mesh.generateBoundaryLayerMesh(mesh_state, cfg);
end
function mesh_state = iStageSizing(mesh_state, cfg, ~, ~)
mesh_state = cfd.mesh.applyGlobalSizing(mesh_state, cfg.meshing.global_size);
mesh_state = cfd.mesh.applyLocalSizing(mesh_state, cfg.meshing.local_sizing_rules);
end
function mesh_state = iStageCurvature(mesh_state, ~, geometry_state, ~)
mesh_state = cfd.mesh.applyCurvatureRefinement(mesh_state, geometry_state);
end
function mesh_state = iStageProximity(mesh_state, ~, geometry_state, ~)
mesh_state = cfd.mesh.applyProximityRefinement(mesh_state, geometry_state);
end
function mesh_state = iStageGrowthControl(mesh_state, cfg, ~, ~)
mesh_state = cfd.mesh.enforceGrowthRate(mesh_state, cfg.meshing.growth_rate);
end
function mesh_state = iStageSmooth(mesh_state, ~, ~, ~)
mesh_state = cfd.mesh.smoothMesh(mesh_state, 8);
end
function mesh_state = iStageQuality(mesh_state, cfg, ~, ~)
mesh_state = cfd.mesh.computeMeshMetrics(mesh_state);
mesh_state = cfd.mesh.detectBadElements(mesh_state, cfg.mesh_quality);
end
function mesh_state = iStageRepair(mesh_state, cfg, geometry_state, options)
mesh_state = cfd.mesh.repairBadElements(mesh_state, cfg, geometry_state, options);
end
function mesh_state = iStageFv(mesh_state, ~, ~, ~)
mesh_state = cfd.mesh.convertToFvTopology(mesh_state);
end

function [mesh_state, recovered] = iRetry(mesh_state, cfg, geometry_state, options, stageIdx)
recovered = false;
if mesh_state.retry_count >= options.max_retries
    return;
end
mesh_state.retry_count = mesh_state.retry_count + 1;
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'WARN', sprintf('Retry %d at stage %d', mesh_state.retry_count, stageIdx));

try
    if options.auto_remesh
        mesh_state = cfd.mesh.automaticRemesh(mesh_state, cfg, geometry_state, options);
    end
    mesh_state = cfd.mesh.computeMeshMetrics(mesh_state);
    recovered = true;
catch ME
    mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'ERROR', ['Retry failed: ' ME.message]);
    if strcmp(options.workflow, 'fault_tolerant')
        try
            loCfg = cfg;
            loCfg.meshing.global_size = cfg.meshing.global_size * 1.25;
            loCfg.meshing.growth_rate = min(cfg.meshing.growth_rate + 0.1, 2.5);
            mesh_state = cfd.mesh.generateVolumeMesh(mesh_state, loCfg, geometry_state, options);
            mesh_state = cfd.mesh.computeMeshMetrics(mesh_state);
            recovered = true;
        catch ME2
            mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'ERROR', ['Fault-tolerant fallback failed: ' ME2.message]);
        end
    end
end
end
