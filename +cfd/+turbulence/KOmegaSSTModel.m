function turb = KOmegaSSTModel(mesh_state, flow, turb, cfg, dt)
%KOMEGASSTMODEL k-omega SST blended update.

n = numel(flow.u);
if nargin < 3 || isempty(turb) || ~all(isfield(turb, {'k','omega','nut'}))
    turb = struct('k',1e-4*ones(n,1),'omega',1*ones(n,1),'nut',1e-5*ones(n,1));
end
if nargin < 5; dt = 1e-3; end

rho = cfg.materials.density;
mu = cfg.materials.viscosity;
Pk = cfd.turbulence.computeProductionTerms(mesh_state, flow.u, flow.v, rho, mu + rho*turb.nut);

wall = cfd.turbulence.NearWallTreatment(mesh_state, flow.u, rho, mu);
F1 = tanh((wall.y_plus/17).^4);

betaStar1 = 0.09; beta1 = 0.075; gamma1 = 5/9;
beta2 = 0.0828; gamma2 = 0.44;

beta = F1.*beta1 + (1-F1).*beta2;
gamma = F1.*gamma1 + (1-F1).*gamma2;

turb.k = turb.k + dt*(Pk - betaStar1*rho*turb.k.*turb.omega);
turb.omega = turb.omega + dt*(gamma.*Pk./max(rho*turb.k,1e-12) - beta.*turb.omega.^2);

a1 = 0.31;
S = sqrt(max(Pk,0)./max(rho*turb.nut,1e-12));
turb.nut = a1*turb.k ./ max(a1*turb.omega, S.*F1 + 1e-12);

turb = cfd.turbulence.WallFunctionManager(turb, wall);
turb = cfd.turbulence.TurbulenceFieldLimiter(turb);
end
