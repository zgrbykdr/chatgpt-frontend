function state = initFields(c, mesh)
% Initialize all flow/turbulence fields.
Ny = mesh.Ny; Nx = mesh.Nx;

state.u = c.bc.inlet.Ux*ones(Ny,Nx);
state.v = c.bc.inlet.Uy*ones(Ny,Nx);
state.p = c.bc.outlet.p*ones(Ny,Nx);
state.pc = zeros(Ny,Nx);

tin = computeTurbulenceInlet(c);
state.k = tin.k*ones(Ny,Nx);
state.epsilon = tin.epsilon*ones(Ny,Nx);
state.omega = tin.omega*ones(Ny,Nx);
state.mut = zeros(Ny,Nx);

state.iter = 0;
state.residualHistory = [];
state.massImbalanceHistory = [];
state.converged = false;
state.diverged = false;
state.stopRequested = false;

state = applyBoundaryConditions(state, c, mesh);
state = updateTurbulenceViscosity(state, c, mesh);
end
