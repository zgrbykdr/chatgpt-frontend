function [u, v, p, res] = CouplingSchemeSIMPLE(state, cfg, fields)
%COUPLINGSCHEMESIMPLE One SIMPLE iteration.

rho = cfg.materials.density;
mu = cfg.materials.viscosity;
if isfield(fields,'muEff') && ~isempty(fields.muEff)
    mu = fields.muEff;
end
dt = 1;
if isfield(fields,'dt'); dt = fields.dt; end

[A_u,b_u,apu] = cfd.solver.MomentumEquation(state.mesh, rho, mu, fields.u, fields.v, fields.p, dt, 'u', fields.convection_scheme, cfg.boundaries, cfg.solver.time_mode);
[A_v,b_v,apv] = cfd.solver.MomentumEquation(state.mesh, rho, mu, fields.u, fields.v, fields.p, dt, 'v', fields.convection_scheme, cfg.boundaries, cfg.solver.time_mode);

[uStar,~] = cfd.solver.LinearSolverFactory(A_u,b_u,fields.linear_solver,fields.lin_tol,fields.lin_maxit,fields.u);
[vStar,~] = cfd.solver.LinearSolverFactory(A_v,b_v,fields.linear_solver,fields.lin_tol,fields.lin_maxit,fields.v);

[Ap,bp,rc] = cfd.solver.PressureCorrectionEquation(state.mesh, rho, uStar, vStar, apu, apv, cfg.boundaries);
[pPrime,~] = cfd.solver.LinearSolverFactory(Ap,bp,fields.linear_solver,fields.lin_tol,fields.lin_maxit,zeros(size(fields.p)));

urf = fields.urf;
p = fields.p + urf.p * pPrime;
u = uStar;
v = vStar;

res = struct();
res.u = norm(A_u*u - b_u)/max(norm(b_u),eps);
res.v = norm(A_v*v - b_v)/max(norm(b_v),eps);
res.p = norm(Ap*pPrime - bp)/max(norm(bp),eps);
res.continuity = rc;
end
