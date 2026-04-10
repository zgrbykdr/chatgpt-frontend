function state = processGeometryPipeline(cfg, source, options)
%PROCESSGEOMETRYPIPELINE Execute complete robust geometry processing pipeline.

if nargin < 1
    cfg = cfd.config.defaultConfig();
end
if nargin < 2 || isempty(source)
    source = cfg.geometry.file_path;
end
if nargin < 3 || isempty(options)
    options = struct();
end

cfg = cfd.config.validateConfig(cfg);
options = iNormalizeOptions(options);

state = cfd.geom.createGeometryState(cfg);
state.status = 'running';

stages = {@iStageImport, @iStageDescribe, @iStageShareTopology, @iStageCap, @iStageRepair, ...
          @iStageDefeature, @iStageExtractFluid, @iStageEnclosure, @iStageWrap, ...
          @iStageRefacet, @iStageLeakCheck, @iStageBuildPde};

for i = 1:numel(stages)
    stageFunc = stages{i};
    try
        state = stageFunc(state, cfg, source, options);
    catch ME
        state = cfd.geom.logGeometryEvent(state, 'ERROR', sprintf('Stage %d failed: %s', i, ME.message));
        [state, recovered] = iAttemptRecovery(state, cfg, source, options, i);
        if ~recovered
            state.status = 'failed';
            state.error = ME.message;
            rethrow(ME);
        end
    end
end

state = cfd.geom.validateWatertight(state, options.leak_tolerance);
if ~state.quality.is_watertight
    state.status = 'failed';
    state.error = 'Watertight validation failed.';
    error('cfd:geom:NotWatertight', 'Geometry pipeline completed but watertight validation failed.');
end

state.status = 'completed';
state = cfd.geom.logGeometryEvent(state, 'INFO', 'Geometry pipeline completed successfully.');

if options.debug_visualize
    fig = cfd.geom.debugVisualizeGeometry(state, 'Geometry Pipeline Result');
    state.debug.figures = [state.debug.figures fig];
end
end

function options = iNormalizeOptions(options)
if ~isstruct(options) || ~isscalar(options)
    error('cfd:geom:InvalidOptions', 'options must be scalar struct.');
end
options = cfd.config.mergeConfig(struct( ...
    'topology_tolerance', 1e-6, ...
    'min_feature_area', 1e-6, ...
    'min_feature_length', 1e-5, ...
    'enclosure_padding_factor', 2.0, ...
    'alpha_radius', NaN, ...
    'refacet_edge_length', 0.01, ...
    'leak_tolerance', 1e-8, ...
    'attempt_recovery', true, ...
    'debug_visualize', false), options);
end

function state = iStageImport(state, ~, source, ~)
state = cfd.geom.importGeometry(state, source, 'auto');
end
function state = iStageDescribe(state, cfg, ~, ~)
state = cfd.geom.describeGeometryAndFlow(state, cfg);
end
function state = iStageShareTopology(state, ~, ~, options)
state = cfd.geom.shareTopologyApprox(state, options.topology_tolerance);
end
function state = iStageCap(state, ~, ~, ~)
state = cfd.geom.createCappingSurfaces(state);
end
function state = iStageRepair(state, ~, ~, ~)
state = cfd.geom.repairTopology(state);
end
function state = iStageDefeature(state, ~, ~, options)
state = cfd.geom.defeatureGeometry(state, options.min_feature_area, options.min_feature_length);
end
function state = iStageExtractFluid(state, ~, ~, ~)
state = cfd.geom.extractFluidRegion(state);
end
function state = iStageEnclosure(state, ~, ~, options)
state = cfd.geom.createEnclosure(state, options.enclosure_padding_factor);
end
function state = iStageWrap(state, ~, ~, options)
state = cfd.geom.wrapSkinGeometry(state, options.alpha_radius);
end
function state = iStageRefacet(state, ~, ~, options)
state = cfd.geom.refacetGeometry(state, options.refacet_edge_length);
end
function state = iStageLeakCheck(state, ~, ~, options)
state = cfd.geom.validateWatertight(state, options.leak_tolerance);
if ~state.quality.is_watertight
    error('cfd:geom:LeakDetected', 'Leak detection failed inside pipeline.');
end
end
function state = iStageBuildPde(state, ~, ~, ~)
state = cfd.geom.buildGeometryModel(state);
end

function [state, recovered] = iAttemptRecovery(state, cfg, source, options, stageId)
recovered = false;
if ~options.attempt_recovery
    return;
end

state.recovery_attempted = true;
state = cfd.geom.logGeometryEvent(state, 'WARN', sprintf('Attempting recovery at stage %d.', stageId));

try
    switch stageId
        case {5,6,10}
            state = cfd.geom.importGeometry(state, source, 'auto');
            state = cfd.geom.shareTopologyApprox(state, options.topology_tolerance*10);
            state = cfd.geom.repairTopology(state);
            state = cfd.geom.repairShortEdges(state, options.min_feature_length*10);
            state = cfd.geom.extractFluidRegion(state);
            state = cfd.geom.buildGeometryModel(state);
            recovered = true;
        case {11,12}
            state = cfd.geom.repairTopology(state);
            state = cfd.geom.repairShortEdges(state, options.min_feature_length*10);
            state = cfd.geom.validateWatertight(state, options.leak_tolerance*10);
            if state.quality.is_watertight
                state = cfd.geom.buildGeometryModel(state);
                recovered = true;
            end
        otherwise
            recovered = false;
    end
catch ME
    state = cfd.geom.logGeometryEvent(state, 'ERROR', ['Recovery failed: ' ME.message]);
end
end
