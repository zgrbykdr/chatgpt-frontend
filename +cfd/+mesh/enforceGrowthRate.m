function mesh_state = enforceGrowthRate(mesh_state, growthRate)
%ENFORCEGROWTHRATE Limit neighboring element size jumps.

if ~(isnumeric(growthRate) && isscalar(growthRate) && isfinite(growthRate) && growthRate >= 1.0)
    error('cfd:mesh:InvalidGrowthRate', 'growthRate must be finite scalar >= 1.0');
end
if isempty(mesh_state.elements)
    return;
end

A = iTriangleAreas(mesh_state.nodes, mesh_state.elements);
S = sqrt(max(A, eps));
adj = triangulation(mesh_state.elements, mesh_state.nodes).neighbors;

for it = 1:2
    for k = 1:numel(S)
        nb = adj(k,:);
        nb = nb(nb>0);
        if isempty(nb)
            continue;
        end
        smax = max(S(nb));
        smin = min(S(nb));
        if smax > growthRate*smin
            S(k) = min(S(k), growthRate*smin);
        end
    end
end

mesh_state.size_field.point_size = min(mesh_state.size_field.point_size, median(S)*ones(size(mesh_state.nodes,1),1));
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', sprintf('Growth rate control enforced (<= %g).', growthRate));
end

function A = iTriangleAreas(P,T)
p1 = P(T(:,1),:); p2 = P(T(:,2),:); p3 = P(T(:,3),:);
A = 0.5*abs((p2(:,1)-p1(:,1)).*(p3(:,2)-p1(:,2)) - (p3(:,1)-p1(:,1)).*(p2(:,2)-p1(:,2)));
end
