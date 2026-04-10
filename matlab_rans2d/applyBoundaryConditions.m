function s = applyBoundaryConditions(s, c, mesh)
% Apply velocity, pressure and turbulence boundary conditions.
Ny = mesh.Ny; Nx = mesh.Nx;

inlet = computeTurbulenceInlet(c);

% Inlet (left)
for j = 1:Ny
    if ~mesh.fluidMask(j,1)
        s.u(j,1) = 0; s.v(j,1) = 0;
        s.k(j,1) = c.clip.kMin;
        s.epsilon(j,1) = c.clip.epsMin;
        s.omega(j,1) = c.clip.omMin;
        continue;
    end
    s.u(j,1) = c.bc.inlet.Ux;
    s.v(j,1) = c.bc.inlet.Uy;
    s.k(j,1) = inlet.k;
    s.epsilon(j,1) = inlet.epsilon;
    s.omega(j,1) = inlet.omega;
end

% Outlet (right): pressure fixed, zero-gradient for others
s.p(:,Nx) = c.bc.outlet.p;
if Nx > 1
    s.u(:,Nx) = s.u(:,Nx-1);
    s.v(:,Nx) = s.v(:,Nx-1);
    s.k(:,Nx) = s.k(:,Nx-1);
    s.epsilon(:,Nx) = s.epsilon(:,Nx-1);
    s.omega(:,Nx) = s.omega(:,Nx-1);
end

% Bottom and top BCs
for i = 1:Nx
    % Bottom
    if strcmpi(c.bc.bottom.type,'symmetry')
        if Ny > 1
            s.u(1,i) = s.u(2,i);
            s.v(1,i) = 0;
            s.k(1,i) = s.k(2,i);
            s.epsilon(1,i) = s.epsilon(2,i);
            s.omega(1,i) = s.omega(2,i);
        end
    else % wall
        s.u(1,i) = 0; s.v(1,i) = 0;
        s.k(1,i) = c.clip.kMin;
        y = max(mesh.wallDist(1,i),1e-8);
        s.epsilon(1,i) = max(c.clip.epsMin, 2*c.mu/c.rho*max(s.k(min(2,Ny),i),c.clip.kMin)/y^2);
        s.omega(1,i) = max(c.clip.omMin, 60*c.mu/(c.rho*0.075*y^2));
    end

    % Top
    if strcmpi(c.bc.top.type,'symmetry')
        if Ny > 1
            s.u(Ny,i) = s.u(Ny-1,i);
            s.v(Ny,i) = 0;
            s.k(Ny,i) = s.k(Ny-1,i);
            s.epsilon(Ny,i) = s.epsilon(Ny-1,i);
            s.omega(Ny,i) = s.omega(Ny-1,i);
        end
    else % wall
        s.u(Ny,i) = 0; s.v(Ny,i) = 0;
        s.k(Ny,i) = c.clip.kMin;
        y = max(mesh.wallDist(Ny,i),1e-8);
        s.epsilon(Ny,i) = max(c.clip.epsMin, 2*c.mu/c.rho*max(s.k(max(Ny-1,1),i),c.clip.kMin)/y^2);
        s.omega(Ny,i) = max(c.clip.omMin, 60*c.mu/(c.rho*0.075*y^2));
    end
end

% Solid mask support (BFS blocked cells)
solid = ~mesh.fluidMask;
s.u(solid) = 0; s.v(solid) = 0;
s.k(solid) = c.clip.kMin;
s.epsilon(solid) = c.clip.epsMin;
s.omega(solid) = c.clip.omMin;
s.mut(solid) = 0;

% Positivity clipping
s.k = max(s.k, c.clip.kMin);
s.epsilon = max(s.epsilon, c.clip.epsMin);
s.omega = max(s.omega, c.clip.omMin);
end
