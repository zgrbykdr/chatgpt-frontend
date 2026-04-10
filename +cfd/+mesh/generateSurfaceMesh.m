function mesh_state = generateSurfaceMesh(mesh_state, cfg, geometry_state)
%GENERATESURFACEMESH Generate boundary edge discretization from geometry.

if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end
cfg = cfd.config.validateConfig(cfg);
poly = iGetPoly(geometry_state);

v = poly.Vertices;
if size(v,1) < 3
    error('cfd:mesh:InsufficientVertices', 'Need at least 3 vertices to generate surface mesh.');
end
if norm(v(1,:)-v(end,:)) > 0
    v(end+1,:) = v(1,:);
end

h = cfg.meshing.global_size;
nodes = zeros(0,2);
for i = 1:size(v,1)-1
    p1 = v(i,:); p2 = v(i+1,:);
    L = norm(p2-p1);
    nSeg = max(1, ceil(L/h));
    t = linspace(0,1,nSeg+1)';
    pts = p1 + (p2-p1).*t;
    if i > 1
        pts = pts(2:end,:);
    end
    nodes = [nodes; pts]; %#ok<AGROW>
end

if norm(nodes(1,:)-nodes(end,:)) < eps
    nodes = nodes(1:end-1,:);
end
m = size(nodes,1);
edges = [(1:m)' [2:m 1]'];

mesh_state.nodes = nodes;
mesh_state.boundary_edges = edges;
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', sprintf('Surface mesh created with %d boundary nodes.', m));
end

function poly = iGetPoly(geometry_state)
if ~isstruct(geometry_state) || ~isscalar(geometry_state)
    error('cfd:mesh:InvalidGeometryState', 'geometry_state must be scalar struct.');
end
if isfield(geometry_state, 'fluid_region') && ~isempty(geometry_state.fluid_region)
    poly = geometry_state.fluid_region;
elseif isfield(geometry_state, 'poly') && ~isempty(geometry_state.poly)
    poly = geometry_state.poly;
else
    error('cfd:mesh:MissingGeometry', 'geometry_state must have poly or fluid_region.');
end
end
