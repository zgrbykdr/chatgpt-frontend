function mesh_state = convertToFvTopology(mesh_state)
%CONVERTTOFVTOPOLOGY Build finite-volume face/cell connectivity.

if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end
if isempty(mesh_state.elements)
    error('cfd:mesh:NoElements', 'elements required for FV conversion.');
end

T = mesh_state.elements;
P = mesh_state.nodes;

faces = [T(:,[1 2]); T(:,[2 3]); T(:,[3 1])];
faces = sort(faces,2);
[uf, ~, ic] = unique(faces, 'rows');

cellFaces = cell(size(T,1),1);
for c = 1:size(T,1)
    ids = [c; c+size(T,1); c+2*size(T,1)];
    cellFaces{c} = ic(ids).';
end

TR = triangulation(T,P);
cc = incenter(TR);
p1 = P(T(:,1),:); p2 = P(T(:,2),:); p3 = P(T(:,3),:);
a = 0.5*abs((p2(:,1)-p1(:,1)).*(p3(:,2)-p1(:,2)) - (p3(:,1)-p1(:,1)).*(p2(:,2)-p1(:,2)));

mesh_state.fv.face_nodes = uf;
mesh_state.fv.cell_faces = cellFaces;
mesh_state.fv.cell_centers = cc;
mesh_state.fv.cell_areas = a;

allEdges = sort(edges(TR),2);
be = sort(mesh_state.boundary_edges,2);
interiorMask = true(size(allEdges,1),1);
if ~isempty(be)
    [~, idxMatch] = ismember(allEdges, be, 'rows');
    interiorMask(idxMatch>0) = false;
end
mesh_state.interior_edges = allEdges(interiorMask,:);

mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', 'Converted mesh to FV topology.');
end
