function wall = NearWallTreatment(mesh_state, u, rho, mu)
%NEARWALLTREATMENT Compute approximate near-wall metrics (y+, uTau).

if ~isstruct(mesh_state) || ~isfield(mesh_state,'fv')
    error('cfd:turbulence:InvalidMeshState', 'mesh_state.fv is required.');
end
centers = mesh_state.fv.cell_centers;
areas = mesh_state.fv.cell_areas;
if isempty(centers)
    error('cfd:turbulence:NoCells', 'No cell centers available.');
end

xmin = min(centers(:,1)); xmax = max(centers(:,1));
ymin = min(centers(:,2)); ymax = max(centers(:,2));
Lx = max(xmax-xmin,eps); Ly = max(ymax-ymin,eps);
wallMask = abs(centers(:,2)-ymin)<0.02*Ly | abs(centers(:,2)-ymax)<0.02*Ly;
yDist = min(abs(centers(:,2)-ymin), abs(ymax-centers(:,2)));

nu = mu/rho;
delta = sqrt(max(areas,eps));
shear = abs(u)./max(delta,eps);
uTau = sqrt(max(mu*shear/rho, 0));
yPlus = rho .* max(uTau,1e-12) .* max(yDist,1e-12) ./ max(mu,1e-12);

wall = struct();
wall.wall_mask = wallMask;
wall.y = yDist;
wall.u_tau = uTau;
wall.y_plus = yPlus;
wall.nu = nu;
end
