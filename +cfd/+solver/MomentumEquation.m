function [A, b, ap] = MomentumEquation(mesh_state, rho, mu, u, v, p, dt, component, scheme, bc, timeMode)
%MOMENTUMEQUATION Assemble momentum equation matrix for u or v.

if ~isstruct(mesh_state) || ~isfield(mesh_state,'fv') || isempty(mesh_state.fv.cell_centers)
    error('cfd:solver:InvalidMeshState', 'mesh_state with fv cell centers required.');
end
n = size(mesh_state.fv.cell_centers,1);
if n < 1
    error('cfd:solver:NoCells', 'No FV cells available.');
end

centers = mesh_state.fv.cell_centers;
areas = mesh_state.fv.cell_areas;
[neighbors, faceLen] = iCellNeighbors(mesh_state);

A = spalloc(n,n,7*n);
b = zeros(n,1);
ap = zeros(n,1);

if strcmpi(component,'u')
    phi = u;
else
    phi = v;
end

[gradPx, gradPy] = cfd.numerics.GradientReconstruction(p, centers, neighbors);

for i = 1:n
    nb = neighbors{i};
    if isempty(nb)
        A(i,i) = 1;
        b(i) = phi(i);
        ap(i) = 1;
        continue;
    end

    aP = 0;
    rhs = 0;
    for k = 1:numel(nb)
        j = nb(k);
        d = norm(centers(j,:)-centers(i,:));
        mui = iCellMu(mu, i);
        muj = iCellMu(mu, j);
        muFace = 0.5*(mui + muj);
        D = muFace * faceLen{i}(k) / max(d, eps);

        Uface = 0.5*(u(i)+u(j));
        Vface = 0.5*(v(i)+v(j));
        e = (centers(j,:)-centers(i,:))/max(d,eps);
        F = rho*(Uface*e(1) + Vface*e(2))*faceLen{i}(k);

        gradPi = [gradPx(i), gradPy(i)];
        phiFace = cfd.numerics.ConvectionSchemes(phi(i), phi(j), gradPi, centers(j,:)-centers(i,:), scheme, F);

        aN = D + max(-F,0);
        A(i,j) = A(i,j) - aN;
        aP = aP + D + max(F,0);
        rhs = rhs + F*phiFace;
    end

    if strcmpi(component,'u')
        rhs = rhs - areas(i)*gradPx(i);
    else
        rhs = rhs - areas(i)*gradPy(i);
    end

    if strcmpi(timeMode,'transient')
        aT = rho*areas(i)/max(dt,eps);
        aP = aP + aT;
        rhs = rhs + aT*phi(i);
    end

    A(i,i) = A(i,i) + aP;
    b(i) = rhs;
    ap(i) = max(aP, eps);
end

    [A,b] = iApplyMomentumBC(A,b,centers,component,bc);
end

function [A,b] = iApplyMomentumBC(A,b,centers,component,bc)
if ~isstruct(bc)
    return;
end
xmin = min(centers(:,1));
xmax = max(centers(:,1));
ymin = min(centers(:,2));
ymax = max(centers(:,2));
Lx = max(xmax-xmin,eps);
Ly = max(ymax-ymin,eps);

inletCells = find(abs(centers(:,1)-xmin) < 0.02*Lx);
outletCells = find(abs(centers(:,1)-xmax) < 0.02*Lx);
wallCells = find(abs(centers(:,2)-ymin) < 0.02*Ly | abs(centers(:,2)-ymax) < 0.02*Ly);

if isfield(bc,'inlet') && isfield(bc.inlet,'velocity')
    vel = bc.inlet.velocity;
    if numel(vel) == 2
        target = vel(1);
        if strcmpi(component,'v'); target = vel(2); end
        for i = inletCells(:)'
            A(i,:) = 0; A(i,i) = 1; b(i) = target;
        end
    end
end

if strcmpi(component,'u') && isfield(bc,'wall')
    for i = wallCells(:)'
        A(i,:) = 0; A(i,i) = 1; b(i) = 0;
    end
elseif strcmpi(component,'v') && isfield(bc,'wall')
    for i = wallCells(:)'
        A(i,:) = 0; A(i,i) = 1; b(i) = 0;
    end
end

if isfield(bc,'symmetry')
    for i = wallCells(:)'
        if strcmpi(component,'v')
            A(i,:) = 0; A(i,i) = 1; b(i) = 0;
        end
    end
end

if isfield(bc,'outlet')
    for i = outletCells(:)'
        if A(i,i) ~= 1
            A(i,i) = A(i,i) + 1e-9;
        end
    end
end
end

function [neighbors, faceLen] = iCellNeighbors(mesh_state)
T = mesh_state.elements;
P = mesh_state.nodes;
TR = triangulation(T,P);
N = neighbors(TR);
cc = incenter(TR);
neighbors = cell(size(T,1),1);
faceLen = cell(size(T,1),1);
for i = 1:size(T,1)
    nb = N(i,:);
    nb = nb(nb>0);
    neighbors{i} = nb(:)';
    fl = zeros(1,numel(nb));
    for k = 1:numel(nb)
        j = nb(k);
        shared = intersect(T(i,:), T(j,:));
        if numel(shared) == 2
            fl(k) = norm(P(shared(1),:) - P(shared(2),:));
        else
            fl(k) = norm(cc(i,:) - cc(j,:));
        end
    end
    faceLen{i} = fl;
end

function muCell = iCellMu(mu, idx)
if isscalar(mu)
    muCell = mu;
elseif isnumeric(mu) && isvector(mu) && numel(mu) >= idx
    muCell = mu(idx);
else
    error('cfd:solver:InvalidViscosityField', 'mu must be scalar or per-cell vector.');
end
end
end
