function mesh_state = applyLocalSizing(mesh_state, localRules)
%APPLYLOCALSIZING Apply local edge/region size rules to size field.

if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end
if isempty(localRules)
    return;
end
if ~isstruct(localRules)
    error('cfd:mesh:InvalidLocalRules', 'localRules must be struct array.');
end

n = size(mesh_state.nodes,1);
if n == 0
    return;
end
if ~isfield(mesh_state, 'size_field') || ~isstruct(mesh_state.size_field) || ~isfield(mesh_state.size_field, 'point_size') || isempty(mesh_state.size_field.point_size)
    mesh_state.size_field.point_size = mesh_state.size_field.global_size * ones(n,1);
end

for i = 1:numel(localRules)
    if ~isfield(localRules(i), 'enabled') || ~logical(localRules(i).enabled)
        continue;
    end
    if ~isfield(localRules(i), 'size') || ~(isnumeric(localRules(i).size) && isscalar(localRules(i).size) && localRules(i).size > 0)
        error('cfd:mesh:InvalidLocalRuleSize', 'localRules(%d).size invalid.', i);
    end
    targetSize = double(localRules(i).size);
    idx = true(n,1);

    if isfield(localRules(i), 'target_entities') && ~isempty(localRules(i).target_entities)
        te = localRules(i).target_entities;
        if ischar(te); te = {te}; end
        if isstring(te) && isscalar(te); te = {char(te)}; end
        if ~iscellstr(te) %#ok<ISCLSTR>
            error('cfd:mesh:InvalidTargetEntities', 'localRules(%d).target_entities must be cellstr.', i);
        end
        if any(strcmp(te, 'boundary'))
            idx = false(n,1);
            idx(unique(mesh_state.boundary_edges(:))) = true;
        elseif any(strcmp(te, 'interior'))
            idx = true(n,1);
            idx(unique(mesh_state.boundary_edges(:))) = false;
        else
            idx = true(n,1);
        end
    end

    mesh_state.size_field.point_size(idx) = min(mesh_state.size_field.point_size(idx), targetSize);
end

mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', sprintf('Applied %d local sizing rules.', numel(localRules)));
end
