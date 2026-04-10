function turb = KOmegaStandardModel(mesh_state, flow, turb, cfg, dt)
%KOMEGASTANDARDMODEL Standard k-omega update.

n = numel(flow.u);
if nargin < 3 || isempty(turb) || ~all(isfield(turb, {'k','omega','nut'}))
    turb = struct('k',1e-4*ones(n,1),'omega',1*ones(n,1),'nut',1e-5*ones(n,1));
end
if nargin < 5; dt = 1e-3; end

rho = cfg.materials.density;
mu = cfg.materials.viscosity;
betaStar = 0.09; beta = 0.075; gamma = 5/9;

Pk = cfd.turbulence.computeProductionTerms(mesh_state, flow.u, flow.v, rho, mu + rho*turb.nut);

turb.k = turb.k + dt*(Pk - betaStar*rho*turb.k.*turb.omega);
turb.omega = turb.omega + dt*(gamma*Pk./max(rho*turb.k,1e-12) - beta*turb.omega.^2);
turb.nut = turb.k ./ max(turb.omega,1e-12);

wall = cfd.turbulence.NearWallTreatment(mesh_state, flow.u, rho, mu);
turb = cfd.turbulence.WallFunctionManager(turb, wall);
turb = cfd.turbulence.TurbulenceFieldLimiter(turb);
end
