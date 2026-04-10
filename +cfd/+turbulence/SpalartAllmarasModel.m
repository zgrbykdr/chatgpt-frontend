function turb = SpalartAllmarasModel(mesh_state, flow, turb, cfg, dt)
%SPALARTALLMARASMODEL Update SA turbulence variable and eddy viscosity.

n = numel(flow.u);
if nargin < 3 || isempty(turb) || ~isfield(turb,'nu_tilde')
    turb = struct('nu_tilde', 1e-6*ones(n,1), 'nut', 1e-6*ones(n,1));
end
if nargin < 5 || isempty(dt)
    dt = 1e-3;
end

rho = cfg.materials.density;
nu = cfg.materials.viscosity/rho;
prod = cfd.turbulence.computeProductionTerms(mesh_state, flow.u, flow.v, rho, cfg.materials.viscosity);

Cb1 = 0.1355; Cw1 = 3.239;
chi = turb.nu_tilde./max(nu,1e-12);
fv1 = chi.^3 ./ max(chi.^3 + 7.1^3, 1e-12);
P = Cb1 * prod;
D = Cw1 * (turb.nu_tilde.^2) ./ max(1e-6, ones(n,1));

turb.nu_tilde = turb.nu_tilde + dt*(P - D);
turb.nut = turb.nu_tilde .* fv1;

wall = cfd.turbulence.NearWallTreatment(mesh_state, flow.u, rho, cfg.materials.viscosity);
turb = cfd.turbulence.WallFunctionManager(turb, wall);
turb = cfd.turbulence.TurbulenceFieldLimiter(turb);
end
