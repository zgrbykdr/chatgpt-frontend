function [Ap, bp, continuityResidual] = PressureCorrectionEquation(mesh_state, rho, uStar, vStar, apu, apv, bc)
%PRESSURECORRECTIONEQUATION Assemble pressure-correction Poisson system.

if ~isstruct(mesh_state) || ~isfield(mesh_state,'fv')
    error('cfd:solver:InvalidMeshState', 'mesh_state with fv data required.');
end
centers = mesh_state.fv.cell_centers;
areas = mesh_state.fv.cell_areas;
n = size(centers,1);
[neighbors, faceLen] = iCellNeighbors(mesh_state);

Ap = spalloc(n,n,7*n);
bp = zeros(n,1);
continuityResidual = 0;

for i = 1:n
    nb = neighbors{i};
    if isempty(nb)
        Ap(i,i) = 1;
        bp(i) = 0;
        continue;
    end

    aP = 0;
    massImb = 0;
    for k = 1:numel(nb)
        j = nb(k);
        d = norm(centers(j,:)-centers(i,:));
        e = (centers(j,:)-centers(i,:))/max(d,eps);
        Sf = faceLen{i}(k);
        dF = rho*Sf*Sf/(max(apu(i),eps)+max(apv(i),eps));

        Ap(i,j) = Ap(i,j) - dF;
        aP = aP + dF;

        Uface = 0.5*(uStar(i)+uStar(j));
        Vface = 0.5*(vStar(i)+vStar(j));
        F = rho*(Uface*e(1)+Vface*e(2))*Sf;
        massImb = massImb + F;
    end

    Ap(i,i) = Ap(i,i) + max(aP,eps);
    bp(i) = -massImb;
    continuityResidual = continuityResidual + abs(massImb)*areas(i);
end

[Ap,bp] = iApplyPressureBC(Ap,bp,centers,bc);
continuityResidual = continuityResidual / max(sum(areas),eps);
end

function [A,b] = iApplyPressureBC(A,b,centers,bc)
if ~isstruct(bc)
    return;
end
xmax = max(centers(:,1));
Lx = max(max(centers(:,1))-min(centers(:,1)),eps);
outletCells = find(abs(centers(:,1)-xmax) < 0.02*Lx);
if isfield(bc,'outlet') && isfield(bc.outlet,'gauge_pressure')
    pOut = bc.outlet.gauge_pressure;
    for i = outletCells(:)'
        A(i,:) = 0; A(i,i) = 1; b(i) = pOut;
    end
else
    A(1,:) = 0; A(1,1) = 1; b(1) = 0;
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
    nb = N(i,:); nb = nb(nb>0);
    neighbors{i} = nb(:)';
    fl = zeros(1,numel(nb));
    for k = 1:numel(nb)
        j = nb(k);
        shared = intersect(T(i,:), T(j,:));
        if numel(shared)==2
            fl(k) = norm(P(shared(1),:) - P(shared(2),:));
        else
            fl(k) = norm(cc(i,:) - cc(j,:));
        end
    end
    faceLen{i} = fl;
end
end
