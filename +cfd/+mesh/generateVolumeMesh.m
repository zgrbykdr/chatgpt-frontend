function mesh_state = generateVolumeMesh(mesh_state, cfg, geometry_state, options)
%GENERATEVOLUMEMESH Generate 2D triangular volume mesh using constrained DT.

if nargin < 4
    options = struct();
end
if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end
cfg = cfd.config.validateConfig(cfg);
poly = iGetPoly(geometry_state);

% Ensure boundary nodes exist.
if isempty(mesh_state.nodes) || isempty(mesh_state.boundary_edges)
    mesh_state = cfd.mesh.generateSurfaceMesh(mesh_state, cfg, geometry_state);
end

bnd = mesh_state.nodes;
edge = mesh_state.boundary_edges;

% Sample interior points based on global size.
bb = [min(bnd(:,1)) max(bnd(:,1)) min(bnd(:,2)) max(bnd(:,2))];
h = cfg.meshing.global_size;
xv = bb(1):h:bb(2);
yv = bb(3):h:bb(4);
[X,Y] = meshgrid(xv,yv);
P = [X(:), Y(:)];
in = isinterior(poly, P(:,1), P(:,2));
P = P(in,:);

allPts = [bnd; P];
allPts = unique(round(allPts, 12), 'rows', 'stable');

% Re-map edges after unique operation.
[~, loc] = ismember(round(bnd,12), round(allPts,12), 'rows');
constraints = [loc(edge(:,1)), loc(edge(:,2))];

dt = delaunayTriangulation(allPts, constraints);
TR = dt.ConnectivityList;
C = incenter(triangulation(TR, dt.Points));
inTri = isinterior(poly, C(:,1), C(:,2));
TR = TR(inTri,:);

if isempty(TR)
    error('cfd:mesh:EmptyTriangulation', 'Volume meshing produced zero elements.');
end

mesh_state.nodes = dt.Points;
mesh_state.elements = TR;
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', sprintf('Volume mesh generated: %d nodes, %d elements.', size(dt.Points,1), size(TR,1)));

if isfield(options, 'use_parallel') && options.use_parallel
    mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', 'Parallel meshing option requested.');
end
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
