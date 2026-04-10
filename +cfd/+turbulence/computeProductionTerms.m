function prod = computeProductionTerms(mesh_state, u, v, rho, muEff)
%COMPUTEPRODUCTIONTERMS Estimate turbulence production on collocated FV cells.

if ~isstruct(mesh_state) || ~isfield(mesh_state,'fv')
    error('cfd:turbulence:InvalidMeshState', 'mesh_state.fv required.');
end
cc = mesh_state.fv.cell_centers;
T = mesh_state.elements;
P = mesh_state.nodes;
TR = triangulation(T,P);
N = neighbors(TR);
nb = cell(size(N,1),1);
for i = 1:size(N,1)
    x = N(i,:); x = x(x>0);
    nb{i} = x(:)';
end

[dudx, dudy] = cfd.numerics.GradientReconstruction(u, cc, nb);
[dvdx, dvdy] = cfd.numerics.GradientReconstruction(v, cc, nb);

Sxx = dudx;
Syy = dvdy;
Sxy = 0.5*(dudy + dvdx);
S2 = 2*(Sxx.^2 + Syy.^2 + 2*Sxy.^2);

if isscalar(muEff)
    muEff = muEff*ones(size(S2));
end
muEff = muEff(:);
prod = rho .* (muEff./rho) .* S2;
prod = max(prod, 0);
end
