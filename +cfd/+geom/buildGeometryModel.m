function state = buildGeometryModel(state)
%BUILDGEOMETRYMODEL Build PDE Toolbox model from geometry polyshape.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'fluid_region') || isempty(state.fluid_region)
    if isfield(state, 'poly') && ~isempty(state.poly)
        state.fluid_region = state.poly;
    else
        error('cfd:geom:NoFluidRegion', 'No fluid region available for PDE model build.');
    end
end

poly = state.fluid_region;
v = poly.Vertices;
if size(v,1) < 3
    error('cfd:geom:InsufficientVertices', 'Need at least 3 vertices for PDE geometry.');
end
if norm(v(1,:) - v(end,:)) < eps
    v = v(1:end-1,:);
end

model = createpde();
if numel(regions(poly)) > 1
    poly = union(poly);
end

gd = [2; size(v,1); v(:,1); v(:,2)];
ns = char('P1');
ns = ns';
sf = 'P1';
[dl, bt] = decsg(gd, sf, ns);
geometryFromEdges(model, dl);

state.pde_model = model;
state = cfd.geom.logGeometryEvent(state, 'INFO', sprintf('PDE model built with %d edges.', size(bt,2)));
end
