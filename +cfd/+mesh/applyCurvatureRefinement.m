function mesh_state = applyCurvatureRefinement(mesh_state, geometry_state)
%APPLYCURVATUREREFINEMENT Refine near high-curvature boundary points.

if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end
if isempty(mesh_state.nodes)
    return;
end
if ~isstruct(geometry_state) || ~isscalar(geometry_state)
    error('cfd:mesh:InvalidGeometryState', 'geometry_state must be scalar struct.');
end
if ~isfield(geometry_state,'poly') || isempty(geometry_state.poly)
    return;
end

v = geometry_state.poly.Vertices;
if size(v,1) < 4
    return;
end

if norm(v(1,:)-v(end,:)) > 0
    v(end+1,:) = v(1,:);
end
curvPts = false(size(v,1),1);
for i = 2:size(v,1)-1
    a = v(i,:) - v(i-1,:);
    b = v(i+1,:) - v(i,:);
    ang = acosd(max(-1,min(1, dot(a,b)/(norm(a)*norm(b)+eps))));
    if abs(180-ang) > 20
        curvPts(i) = true;
    end
end
cp = v(curvPts,:);
if isempty(cp)
    return;
end

ps = mesh_state.size_field.point_size;
if isempty(ps)
    ps = mesh_state.size_field.global_size*ones(size(mesh_state.nodes,1),1);
end
for k = 1:size(cp,1)
    d = hypot(mesh_state.nodes(:,1)-cp(k,1), mesh_state.nodes(:,2)-cp(k,2));
    idx = d < 3*mesh_state.size_field.global_size;
    ps(idx) = min(ps(idx), 0.7*mesh_state.size_field.global_size);
end
mesh_state.size_field.point_size = ps;
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', 'Curvature refinement applied.');
end
