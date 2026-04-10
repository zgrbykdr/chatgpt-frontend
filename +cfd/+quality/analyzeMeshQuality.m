function quality = analyzeMeshQuality(mesh_state)
%ANALYZEMESHQUALITY Compute comprehensive mesh-quality metrics.
% Metrics:
% - skewness (normalized equiangular)
% - orthogonal quality
% - aspect ratio
% - change in size
% - degenerate elements
% - inverted elements

if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:quality:InvalidMeshState', 'mesh_state must be a scalar struct.');
end
if ~isfield(mesh_state, 'nodes') || ~isfield(mesh_state, 'elements')
    error('cfd:quality:MissingMeshFields', 'mesh_state must include nodes and elements.');
end
P = mesh_state.nodes;
T = mesh_state.elements;
if ~(isnumeric(P) && size(P,2)==2 && all(isfinite(P(:))))
    error('cfd:quality:InvalidNodes', 'nodes must be finite numeric Nx2.');
end
if ~(isnumeric(T) && size(T,2)==3)
    error('cfd:quality:InvalidElements', 'elements must be numeric Mx3.');
end
if isempty(T)
    error('cfd:quality:EmptyElements', 'No elements available for quality analysis.');
end
if any(T(:) < 1 | T(:) > size(P,1) | floor(T(:))~=T(:))
    error('cfd:quality:InvalidConnectivity', 'elements contain invalid node indices.');
end

p1 = P(T(:,1),:); p2 = P(T(:,2),:); p3 = P(T(:,3),:);

L1 = vecnorm(p2-p1,2,2);
L2 = vecnorm(p3-p2,2,2);
L3 = vecnorm(p1-p3,2,2);

% Signed twice-area /2 for inversion detection.
signedA = 0.5*((p2(:,1)-p1(:,1)).*(p3(:,2)-p1(:,2)) - (p3(:,1)-p1(:,1)).*(p2(:,2)-p1(:,2)));
A = abs(signedA);

minL = min([L1 L2 L3],[],2);
maxL = max([L1 L2 L3],[],2);
aspectRatio = maxL ./ max(minL, eps);

% Normalized equiangular skewness for triangles.
% s = max((theta_max-60)/120, (60-theta_min)/60)
ang1 = iAngle(p2-p1, p3-p1);
ang2 = iAngle(p1-p2, p3-p2);
ang3 = iAngle(p1-p3, p2-p3);
theta = [ang1 ang2 ang3];
thetaMax = max(theta,[],2);
thetaMin = min(theta,[],2);
skewEquiangular = max((thetaMax - 60)./120, (60 - thetaMin)./60);
skewEquiangular = max(min(skewEquiangular, 1), 0);

% Orthogonal quality approximation: ratio of inradius/circumradius scaled to [0,1].
s = 0.5*(L1+L2+L3);
rIn = A ./ max(s, eps);
rCirc = (L1.*L2.*L3) ./ max(4*A, eps);
orthogonalQuality = 2*rIn ./ max(rCirc, eps);
orthogonalQuality = max(min(orthogonalQuality, 1), 0);

% Size-change metric on neighboring cells.
TR = triangulation(T, P);
N = neighbors(TR);
charSize = sqrt(max(A, eps));
sizeChange = ones(size(T,1),1);
for i = 1:size(T,1)
    nb = N(i,:);
    nb = nb(nb>0);
    if isempty(nb)
        sizeChange(i) = 1;
    else
        ratio = max(charSize(i), charSize(nb)) / max(min(charSize(i), charSize(nb)), eps);
        sizeChange(i) = max(ratio);
    end
end

% Degenerate and inverted elements.
degenerateMask = A <= (1e-14 * max(A));
invertedMask = signedA <= 0;

quality = struct();
quality.element_count = size(T,1);
quality.skewness_equiangular = skewEquiangular;
quality.orthogonal_quality = orthogonalQuality;
quality.aspect_ratio = aspectRatio;
quality.size_change = sizeChange;
quality.degenerate_elements = find(degenerateMask);
quality.inverted_elements = find(invertedMask);

quality.summary = struct( ...
    'max_skewness_equiangular', max(skewEquiangular), ...
    'min_orthogonal_quality', min(orthogonalQuality), ...
    'max_aspect_ratio', max(aspectRatio), ...
    'max_size_change', max(sizeChange), ...
    'num_degenerate', nnz(degenerateMask), ...
    'num_inverted', nnz(invertedMask));
end

function ang = iAngle(a, b)
den = vecnorm(a,2,2).*vecnorm(b,2,2);
cosv = dot(a,b,2) ./ max(den, eps);
cosv = max(min(cosv,1),-1);
ang = acosd(cosv);
end
