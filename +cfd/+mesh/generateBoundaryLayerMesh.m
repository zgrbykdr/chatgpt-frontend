function mesh_state = generateBoundaryLayerMesh(mesh_state, cfg)
%GENERATEBOUNDARYLAYERMESH Generate pseudo boundary-layer nodes/elements.

cfg = cfd.config.validateConfig(cfg);
bl = cfg.meshing.boundary_layer;
if ~bl.enabled || isempty(mesh_state.boundary_edges)
    return;
end
if isempty(mesh_state.nodes)
    error('cfd:mesh:MissingNodes', 'nodes are required for boundary layer generation.');
end

baseNodes = mesh_state.nodes;
bEdges = mesh_state.boundary_edges;
layerNodes = zeros(0,2);
layerElems = zeros(0,3);

offset = 0;
for l = 1:bl.num_layers
    t = bl.first_layer_thickness * bl.growth_rate^(l-1);
    for e = 1:size(bEdges,1)
        i1 = bEdges(e,1); i2 = bEdges(e,2);
        p1 = baseNodes(i1,:); p2 = baseNodes(i2,:);
        tvec = p2-p1;
        nvec = [ -tvec(2), tvec(1) ];
        nrm = norm(nvec);
        if nrm < eps
            continue;
        end
        nvec = nvec/nrm;
        q1 = p1 + t*nvec;
        q2 = p2 + t*nvec;

        layerNodes = [layerNodes; q1; q2]; %#ok<AGROW>
        idx1 = offset + size(layerNodes,1)-1;
        idx2 = offset + size(layerNodes,1);
        layerElems = [layerElems; i1 i2 idx1; i2 idx2 idx1]; %#ok<AGROW>
    end
end

mesh_state.boundary_layer.nodes = layerNodes;
mesh_state.boundary_layer.elements = layerElems;
mesh_state.boundary_layer.num_layers = bl.num_layers;
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', sprintf('Boundary layer generated with %d layers.', bl.num_layers));
end
