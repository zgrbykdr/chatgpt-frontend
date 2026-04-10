function mesh_state = applyGlobalSizing(mesh_state, globalSize)
%APPLYGLOBALSIZING Update mesh size field with global size.

if ~(isnumeric(globalSize) && isscalar(globalSize) && isfinite(globalSize) && globalSize > 0)
    error('cfd:mesh:InvalidGlobalSize', 'globalSize must be positive finite scalar.');
end
if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end

n = size(mesh_state.nodes,1);
mesh_state.size_field.global_size = globalSize;
mesh_state.size_field.point_size = globalSize*ones(n,1);
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', sprintf('Applied global sizing h=%g', globalSize));
end
