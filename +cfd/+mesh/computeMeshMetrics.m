function mesh_state = computeMeshMetrics(mesh_state)
%COMPUTEMESHMETRICS Compute skewness, orthogonal quality, aspect ratio.

if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end
if isempty(mesh_state.elements)
    error('cfd:mesh:NoElements', 'No elements available to compute quality metrics.');
end

P = mesh_state.nodes;
T = mesh_state.elements;

p1 = P(T(:,1),:); p2 = P(T(:,2),:); p3 = P(T(:,3),:);
L1 = vecnorm(p2-p1,2,2); L2 = vecnorm(p3-p2,2,2); L3 = vecnorm(p1-p3,2,2);
A = 0.5*abs((p2(:,1)-p1(:,1)).*(p3(:,2)-p1(:,2)) - (p3(:,1)-p1(:,1)).*(p2(:,2)-p1(:,2)));

s = 0.5*(L1+L2+L3);
rIn = A ./ max(s, eps);
rCirc = (L1.*L2.*L3) ./ max(4*A, eps);

aspect = max([L1,L2,L3], [], 2) ./ max(min([L1,L2,L3], [], 2), eps);
ortho = 2*rIn ./ max(rCirc, eps);
skew = 1 - ortho;

mesh_state.quality.skewness = skew;
mesh_state.quality.orthogonal_quality = ortho;
mesh_state.quality.aspect_ratio = aspect;
mesh_state.quality.max_skewness = max(skew);
mesh_state.quality.min_orthogonal_quality = min(ortho);
mesh_state.quality.max_aspect_ratio = max(aspect);

mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', sprintf('Quality metrics computed for %d elements.', size(T,1)));
end
