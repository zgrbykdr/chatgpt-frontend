function [gradX, gradY] = GradientReconstruction(phi, cellCenters, neighbors)
%GRADIENTRECONSTRUCTION Least-squares gradient reconstruction.

if ~(isnumeric(phi) && isvector(phi))
    error('cfd:numerics:InvalidPhi', 'phi must be numeric vector.');
end
if ~(isnumeric(cellCenters) && size(cellCenters,2)==2)
    error('cfd:numerics:InvalidCenters', 'cellCenters must be Nx2.');
end
if numel(phi) ~= size(cellCenters,1)
    error('cfd:numerics:SizeMismatch', 'phi and centers size mismatch.');
end
if ~iscell(neighbors)
    error('cfd:numerics:InvalidNeighbors', 'neighbors must be cell array.');
end

n = numel(phi);
gradX = zeros(n,1);
gradY = zeros(n,1);
for i = 1:n
    nb = neighbors{i};
    if isempty(nb)
        continue;
    end
    dx = cellCenters(nb,1) - cellCenters(i,1);
    dy = cellCenters(nb,2) - cellCenters(i,2);
    dp = phi(nb) - phi(i);
    M = [dx dy];
    if rank(M) < 2
        continue;
    end
    g = M\dp;
    gradX(i) = g(1);
    gradY(i) = g(2);
end
end
