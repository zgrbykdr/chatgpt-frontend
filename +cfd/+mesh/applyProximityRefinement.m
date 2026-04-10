function mesh_state = applyProximityRefinement(mesh_state, geometry_state)
%APPLYPROXIMITYREFINEMENT Refine mesh where boundaries are close.

if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end
if isempty(mesh_state.nodes) || isempty(mesh_state.boundary_edges)
    return;
end

if ~isstruct(geometry_state) || ~isscalar(geometry_state)
    error('cfd:mesh:InvalidGeometryState', 'geometry_state must be scalar struct.');
end

bidx = unique(mesh_state.boundary_edges(:));
bpts = mesh_state.nodes(bidx,:);
if size(bpts,1) < 4
    return;
end

D = pdist2(bpts, bpts);
D(D==0) = inf;
minD = min(D,[],2);
threshold = 2.5*mesh_state.size_field.global_size;
closePts = bpts(minD < threshold, :);

ps = mesh_state.size_field.point_size;
if isempty(ps)
    ps = mesh_state.size_field.global_size*ones(size(mesh_state.nodes,1),1);
end
for i = 1:size(closePts,1)
    d = hypot(mesh_state.nodes(:,1)-closePts(i,1), mesh_state.nodes(:,2)-closePts(i,2));
    idx = d < threshold;
    ps(idx) = min(ps(idx), 0.6*mesh_state.size_field.global_size);
end
mesh_state.size_field.point_size = ps;
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', 'Proximity refinement applied.');
end
