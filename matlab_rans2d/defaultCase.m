function c = defaultCase()
% Default case settings for RANS2D solver.
c.name = 'Default Channel';

% Domain and mesh
c.Lx = 5.0;
c.Ly = 1.0;
c.Nx = 80;
c.Ny = 32;

% Fluid
c.rho = 1.225;
c.mu = 1.7894e-5;

% Boundary conditions
c.bc.inlet.type = 'velocity_inlet';
c.bc.inlet.Ux = 10.0;
c.bc.inlet.Uy = 0.0;
c.bc.inlet.turbulenceInput = 'I-L'; % I-L or I-Dh
c.bc.inlet.intensity = 0.05;
c.bc.inlet.lengthScale = 0.07*c.Ly;
c.bc.inlet.Dh = 2*c.Ly;

c.bc.outlet.type = 'pressure_outlet';
c.bc.outlet.p = 0.0;

c.bc.top.type = 'wall';      % wall | symmetry
c.bc.bottom.type = 'wall';   % wall | symmetry

% Numerics
c.model = 'Standard k-epsilon';
c.scheme = 'First-order upwind';
c.pvCoupling = 'SIMPLE'; % SIMPLE or SIMPLEC
c.maxIter = 1500;
c.tol = 1e-5;

c.urf.u = 0.5;
c.urf.v = 0.5;
c.urf.p = 0.25;
c.urf.k = 0.5;
c.urf.epsilon = 0.5;
c.urf.omega = 0.5;

% Limits / clipping
c.clip.kMin = 1e-10;
c.clip.epsMin = 1e-10;
c.clip.omMin = 1e-8;
c.clip.mutMax = 1e3;

% Geometry mode
c.geometry = 'channel'; % channel | bfs | flatplate
c.stepHeight = 0.4*c.Ly;
end
