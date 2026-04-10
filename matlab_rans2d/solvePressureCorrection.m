function [s, massImbalance] = solvePressureCorrection(s, mom, c, mesh)
% Pressure correction equation for SIMPLE / SIMPLEC.
Ny = mesh.Ny; Nx = mesh.Nx;
N = Nx*Ny;
rho = c.rho;

rows = zeros(5*N,1);
cols = zeros(5*N,1);
vals = zeros(5*N,1);
b = zeros(N,1);
ptr = 0;

flux = computeFaceFluxes(s, c, mesh);
mb = zeros(Ny,Nx);
for j = 1:Ny
    for i = 1:Nx
        if ~mesh.fluidMask(j,i)
            continue;
        end
        mb(j,i) = flux.Fw(j,i) - flux.Fe(j,i) + flux.Fs(j,i) - flux.Fn(j,i);
    end
end
massImbalance = sum(abs(mb(mesh.fluidMask))) / max(sum(mesh.vol(mesh.fluidMask)),1e-12);

for j = 1:Ny
    dy = mesh.dy(j);
    for i = 1:Nx
        P = sub2ind([Ny,Nx], j, i);

        if ~mesh.fluidMask(j,i)
            ptr=ptr+1; rows(ptr)=P; cols(ptr)=P; vals(ptr)=1; b(P)=0;
            continue;
        end

        dx = mesh.dx(i);
        iW = max(i-1,1); iE = min(i+1,Nx);
        jS = max(j-1,1); jN = min(j+1,Ny);

        dW = dy/max(mom.aPu(j,iW),1e-12);
        dE = dy/max(mom.aPu(j,i),1e-12);
        dS = dx/max(mom.aPv(jS,i),1e-12);
        dN = dx/max(mom.aPv(j,i),1e-12);

        if strcmpi(c.pvCoupling,'SIMPLEC')
            % practical SIMPLEC strengthening
            corr = 1.2;
        else
            corr = 1.0;
        end

        aW = rho*corr*dW;
        aE = rho*corr*dE;
        aS = rho*corr*dS;
        aN = rho*corr*dN;
        aP = aW + aE + aS + aN;

        if i == Nx
            % outlet pressure is fixed -> p' = 0
            aP = 1; aW=0; aE=0; aS=0; aN=0;
            b(P) = 0;
        else
            b(P) = mb(j,i);
        end

        ptr=ptr+1; rows(ptr)=P; cols(ptr)=P; vals(ptr)=aP;
        if i>1 && aW~=0
            W = sub2ind([Ny,Nx],j,i-1);
            ptr=ptr+1; rows(ptr)=P; cols(ptr)=W; vals(ptr)=-aW;
        end
        if i<Nx && aE~=0
            E = sub2ind([Ny,Nx],j,i+1);
            ptr=ptr+1; rows(ptr)=P; cols(ptr)=E; vals(ptr)=-aE;
        end
        if j>1 && aS~=0
            S = sub2ind([Ny,Nx],j-1,i);
            ptr=ptr+1; rows(ptr)=P; cols(ptr)=S; vals(ptr)=-aS;
        end
        if j<Ny && aN~=0
            Nn = sub2ind([Ny,Nx],j+1,i);
            ptr=ptr+1; rows(ptr)=P; cols(ptr)=Nn; vals(ptr)=-aN;
        end
    end
end

Ap = sparse(rows(1:ptr), cols(1:ptr), vals(1:ptr), N, N);
pc = Ap \ b;
s.pc = reshape(pc, Ny, Nx);

% Pressure correction
s.p = s.p + c.urf.p*s.pc;

% Velocity corrections
for j = 1:Ny
    dy = mesh.dy(j);
    for i = 2:Nx-1
        if ~mesh.fluidMask(j,i)
            continue;
        end
        du = dy/max(mom.aPu(j,i),1e-12) * (s.pc(j,i-1)-s.pc(j,i));
        s.u(j,i) = s.u(j,i) + du;
    end
end

for j = 2:Ny-1
    for i = 1:Nx
        if ~mesh.fluidMask(j,i)
            continue;
        end
        dx = mesh.dx(i);
        dv = dx/max(mom.aPv(j,i),1e-12) * (s.pc(j-1,i)-s.pc(j,i));
        s.v(j,i) = s.v(j,i) + dv;
    end
end
end
