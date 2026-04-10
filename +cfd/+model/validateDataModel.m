function model = validateDataModel(model)
%VALIDATEDATAMODEL Validate CFD runtime data model struct integrity.

if ~isstruct(model) || ~isscalar(model)
    error('cfd:model:InvalidModel', 'Data model must be a scalar struct.');
end

requiredTop = {'meta','config','geometry_state','mesh_state','physics_state','iteration_state','solution_state','run_report'};
for i = 1:numel(requiredTop)
    if ~isfield(model, requiredTop{i})
        error('cfd:model:MissingField', 'Missing top-level model field: %s', requiredTop{i});
    end
end

if ~isstruct(model.meta) || ~isscalar(model.meta)
    error('cfd:model:InvalidMeta', 'meta must be a scalar struct.');
end
if ~isfield(model.meta, 'schema_version') || isempty(strtrim(char(model.meta.schema_version)))
    error('cfd:model:InvalidMetaSchemaVersion', 'meta.schema_version must be non-empty.');
end
if ~isfield(model.meta, 'status')
    error('cfd:model:InvalidMetaStatus', 'meta.status is required.');
end

model.config = cfd.config.validateConfig(model.config);

iRequireStruct(model.geometry_state, 'geometry_state');
iRequireStruct(model.mesh_state, 'mesh_state');
iRequireStruct(model.physics_state, 'physics_state');
iRequireStruct(model.iteration_state, 'iteration_state');
iRequireStruct(model.solution_state, 'solution_state');
iRequireStruct(model.run_report, 'run_report');

iRequireField(model.geometry_state, 'is_prepared', 'geometry_state');
iRequireField(model.mesh_state, 'is_generated', 'mesh_state');
iRequireField(model.physics_state, 'is_initialized', 'physics_state');
iRequireField(model.solution_state, 'is_solved', 'solution_state');
iRequireField(model.iteration_state, 'iteration', 'iteration_state');

iValidateLogical(model.geometry_state.is_prepared, 'geometry_state.is_prepared');
iValidateLogical(model.mesh_state.is_generated, 'mesh_state.is_generated');
iValidateLogical(model.physics_state.is_initialized, 'physics_state.is_initialized');
iValidateLogical(model.solution_state.is_solved, 'solution_state.is_solved');

iValidateNonNegativeInteger(model.iteration_state.iteration, 'iteration_state.iteration');

if ~isfield(model.mesh_state, 'nodes') || ~(isnumeric(model.mesh_state.nodes) && size(model.mesh_state.nodes,2) == 2)
    error('cfd:model:InvalidNodes', 'mesh_state.nodes must be numeric Nx2.');
end
if ~isfield(model.mesh_state, 'elements') || ~(isnumeric(model.mesh_state.elements) && size(model.mesh_state.elements,2) == 3)
    error('cfd:model:InvalidElements', 'mesh_state.elements must be numeric Mx3.');
end
if ~isfield(model.mesh_state, 'num_nodes') || model.mesh_state.num_nodes < 0
    error('cfd:model:InvalidNumNodes', 'mesh_state.num_nodes must be >= 0.');
end
if ~isfield(model.mesh_state, 'num_elements') || model.mesh_state.num_elements < 0
    error('cfd:model:InvalidNumElements', 'mesh_state.num_elements must be >= 0.');
end

if model.mesh_state.num_nodes ~= size(model.mesh_state.nodes,1)
    error('cfd:model:NodeCountMismatch', 'mesh_state.num_nodes does not match size(mesh_state.nodes,1).');
end
if model.mesh_state.num_elements ~= size(model.mesh_state.elements,1)
    error('cfd:model:ElementCountMismatch', 'mesh_state.num_elements does not match size(mesh_state.elements,1).');
end

if ~isfield(model.run_report, 'warnings') || ~iscell(model.run_report.warnings)
    error('cfd:model:InvalidWarnings', 'run_report.warnings must be a cell array.');
end
if ~isfield(model.run_report, 'errors') || ~iscell(model.run_report.errors)
    error('cfd:model:InvalidErrors', 'run_report.errors must be a cell array.');
end
if ~isfield(model.run_report, 'termination_reason')
    error('cfd:model:MissingTerminationReason', 'run_report.termination_reason is required.');
end
end

function iRequireStruct(s, name)
if ~isstruct(s) || ~isscalar(s)
    error('cfd:model:InvalidStruct', '%s must be a scalar struct.', name);
end
end

function iRequireField(s, fieldName, scope)
if ~isfield(s, fieldName)
    error('cfd:model:MissingField', '%s missing required field: %s', scope, fieldName);
end
end

function iValidateLogical(v, name)
if ~(islogical(v) && isscalar(v))
    error('cfd:model:InvalidLogical', '%s must be a logical scalar.', name);
end
end

function iValidateNonNegativeInteger(v, name)
if ~(isnumeric(v) && isscalar(v) && isfinite(v) && v >= 0 && floor(v) == v)
    error('cfd:model:InvalidInteger', '%s must be a nonnegative integer scalar.', name);
end
end
