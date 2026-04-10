function state = extractFluidRegion(state)
%EXTRACTFLUIDREGION Extract main fluid domain region from geometry polyshape.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'poly') || isempty(state.poly)
    error('cfd:geom:MissingPoly', 'state.poly is required.');
end

regions = regions(state.poly);
if isempty(regions)
    error('cfd:geom:NoRegions', 'No regions found in geometry.');
end

areas = zeros(numel(regions),1);
for i = 1:numel(regions)
    areas(i) = area(regions(i));
end
[~, idx] = max(areas);
fluid = regions(idx);

if area(fluid) <= 0
    error('cfd:geom:InvalidFluidRegion', 'Extracted fluid region has non-positive area.');
end

state.fluid_region = fluid;
state = cfd.geom.logGeometryEvent(state, 'INFO', sprintf('Extracted fluid region area=%.6g', area(fluid)));
end
