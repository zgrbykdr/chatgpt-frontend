function state = defeatureGeometry(state, minFeatureArea, minFeatureLength)
%DEFEATUREGEOMETRY Remove small regions/holes and tiny perimeter features.

if nargin < 2 || isempty(minFeatureArea)
    minFeatureArea = 1e-6;
end
if nargin < 3 || isempty(minFeatureLength)
    minFeatureLength = 1e-4;
end

if ~(isnumeric(minFeatureArea) && isscalar(minFeatureArea) && isfinite(minFeatureArea) && minFeatureArea >= 0)
    error('cfd:geom:InvalidMinFeatureArea', 'minFeatureArea must be finite scalar >= 0.');
end
if ~(isnumeric(minFeatureLength) && isscalar(minFeatureLength) && isfinite(minFeatureLength) && minFeatureLength >= 0)
    error('cfd:geom:InvalidMinFeatureLength', 'minFeatureLength must be finite scalar >= 0.');
end
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~isfield(state, 'poly') || isempty(state.poly)
    error('cfd:geom:MissingPoly', 'state.poly is required.');
end

regs = regions(state.poly);
keep = polyshape.empty(0,1);
for i = 1:numel(regs)
    if area(regs(i)) >= minFeatureArea
        keep(end+1,1) = regs(i); %#ok<AGROW>
    end
end
if isempty(keep)
    error('cfd:geom:DefeatureRemovedAll', 'Defeaturing removed all geometry regions.');
end
combined = union(keep);
state.poly = combined;
state = cfd.geom.repairShortEdges(state, minFeatureLength);
state = cfd.geom.logGeometryEvent(state, 'INFO', 'Defeaturing completed.');
end
