function mesh_state = smoothMesh(mesh_state, iterations)
%SMOOTHMESH Laplacian smoothing on interior nodes.

if nargin < 2 || isempty(iterations)
    iterations = 5;
end
if ~(isnumeric(iterations) && isscalar(iterations) && isfinite(iterations) && iterations >= 1)
    error('cfd:mesh:InvalidIterations', 'iterations must be integer >=1');
end
if isempty(mesh_state.elements)
    return;
end

P = mesh_state.nodes;
T = mesh_state.elements;
TR = triangulation(T,P);
E = edges(TR);
nb = cell(size(P,1),1);
for i = 1:size(E,1)
    a = E(i,1); b = E(i,2);
    nb{a}(end+1) = b; %#ok<AGROW>
    nb{b}(end+1) = a; %#ok<AGROW>
end

isBoundary = false(size(P,1),1);
isBoundary(unique(mesh_state.boundary_edges(:))) = true;

for it = 1:iterations
    Pnew = P;
    for n = 1:size(P,1)
        if isBoundary(n) || isempty(nb{n})
            continue;
        end
        Pnew(n,:) = mean(P(nb{n},:),1);
    end
    P = Pnew;
end

mesh_state.nodes = P;
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', sprintf('Smoothed mesh with %d iterations.', iterations));
end
