function mesh_state = localRefineMesh(mesh_state, elementIds, useParallel)
%LOCALREFINEMESH Refine selected triangles by centroid insertion.

if nargin < 3 || isempty(useParallel)
    useParallel = false;
end
if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end
if isempty(elementIds)
    return;
end
if any(elementIds < 1) || any(elementIds > size(mesh_state.elements,1))
    error('cfd:mesh:InvalidElementIds', 'elementIds out of range.');
end

P = mesh_state.nodes;
T = mesh_state.elements;
refineMask = false(size(T,1),1);
refineMask(unique(elementIds)) = true;

Tkeep = T(~refineMask,:);
Tref = T(refineMask,:);
newT = zeros(0,3);
newPts = zeros(size(Tref,1),2);

if useParallel && license('test','Distrib_Computing_Toolbox')
    parfor i = 1:size(Tref,1)
        tri = Tref(i,:);
        newPts(i,:) = mean(P(tri,:),1);
    end
else
    for i = 1:size(Tref,1)
        tri = Tref(i,:);
        newPts(i,:) = mean(P(tri,:),1);
    end
end

startIdx = size(P,1);
P = [P; newPts];
for i = 1:size(Tref,1)
    tri = Tref(i,:);
    c = startIdx + i;
    newT = [newT; tri(1) tri(2) c; tri(2) tri(3) c; tri(3) tri(1) c]; %#ok<AGROW>
end

mesh_state.nodes = P;
mesh_state.elements = [Tkeep; newT];
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', sprintf('Locally refined %d elements.', numel(elementIds)));
end
