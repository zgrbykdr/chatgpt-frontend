function turb = KEpsilonRealizableModel(mesh_state, flow, turb, cfg, dt)
%KEPSILONREALIZABLEMODEL Realizable k-epsilon update.

n = numel(flow.u);
if nargin < 3 || isempty(turb) || ~all(isfield(turb, {'k','epsilon','nut'}))
    turb = struct('k',1e-4*ones(n,1),'epsilon',1e-5*ones(n,1),'nut',1e-5*ones(n,1));
end
if nargin < 5; dt = 1e-3; end

rho = cfg.materials.density;
mu = cfg.materials.viscosity;
A0 = 4.04;

Pk = cfd.turbulence.computeProductionTerms(mesh_state, flow.u, flow.v, rho, mu + rho*turb.nut);
S = sqrt(max(Pk,0)./max(rho*turb.nut,1e-12));
Cmu = 1 ./ max(A0 + S.*turb.k./max(turb.epsilon,1e-12), 1e-6);
C1e = 1.44; C2e = 1.9;

turb.k = turb.k + dt*(Pk - rho*turb.epsilon);
turb.epsilon = turb.epsilon + dt*(C1e*Pk.*turb.epsilon./max(turb.k,1e-12) - C2e*rho*(turb.epsilon.^2)./max(turb.k,1e-12));
turb.nut = Cmu.*(turb.k.^2)./max(turb.epsilon,1e-12);

wall = cfd.turbulence.NearWallTreatment(mesh_state, flow.u, rho, mu);
turb = cfd.turbulence.WallFunctionManager(turb, wall);
turb = cfd.turbulence.TurbulenceFieldLimiter(turb);
end
