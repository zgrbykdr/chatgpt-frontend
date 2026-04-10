function mesh_state = detectBadElements(mesh_state, qualityCfg)
%DETECTBADELEMENTS Identify elements violating quality thresholds.

if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:mesh:InvalidMeshState', 'mesh_state must be scalar struct.');
end
if ~isstruct(qualityCfg) || ~isscalar(qualityCfg)
    error('cfd:mesh:InvalidQualityCfg', 'qualityCfg must be scalar struct.');
end
if isempty(mesh_state.quality.skewness)
    mesh_state = cfd.mesh.computeMeshMetrics(mesh_state);
end

bad = mesh_state.quality.skewness > qualityCfg.max_skewness | ...
      mesh_state.quality.orthogonal_quality < qualityCfg.min_orthogonal_quality | ...
      mesh_state.quality.aspect_ratio > qualityCfg.max_aspect_ratio;

mesh_state.quality.bad_element_ids = find(bad);
mesh_state = cfd.mesh.logMeshEvent(mesh_state, 'INFO', sprintf('Detected %d bad elements.', nnz(bad)));
end
