function [s, mom] = solveMomentum(s, c, mesh)
% Solve u and v momentum equations with FVM and linear system assembly.
muEff = c.mu + s.mut;

[uNew, aPu] = solveScalarMomentum(s, c, mesh, muEff, 'u');
[vNew, aPv] = solveScalarMomentum(s, c, mesh, muEff, 'v');

s.u = c.urf.u*uNew + (1-c.urf.u)*s.u;
s.v = c.urf.v*vNew + (1-c.urf.v)*s.v;

mom.aPu = aPu;
mom.aPv = aPv;
end

function [phiNew, aPField] = solveScalarMomentum(s, c, mesh, gamma, comp)
Ny = mesh.Ny; Nx = mesh.Nx;
N = Nx*Ny;
rho = c.rho;

rows = zeros(5*N,1);
cols = zeros(5*N,1);
vals = zeros(5*N,1);
b = zeros(N,1);
aPField = ones(Ny,Nx);
ptr = 0;

flux = computeFaceFluxes(s, c, mesh);

for j = 1:Ny
    dy = mesh.dy(j);
    for i = 1:Nx
        P = sub2ind([Ny,Nx], j, i);

        if ~mesh.fluidMask(j,i)
            ptr = ptr + 1; rows(ptr)=P; cols(ptr)=P; vals(ptr)=1; b(P)=0;
            continue;
        end

        dx = mesh.dx(i);
        iW = max(i-1,1); iE = min(i+1,Nx);
        jS = max(j-1,1); jN = min(j+1,Ny);

        Fw = flux.Fw(j,i); Fe = flux.Fe(j,i); Fs = flux.Fs(j,i); Fn = flux.Fn(j,i);

        Dw = 0.5*(gamma(j,i)+gamma(j,iW))*dy/max(mesh.xc(i)-mesh.xc(iW),1e-12);
        De = 0.5*(gamma(j,i)+gamma(j,iE))*dy/max(mesh.xc(iE)-mesh.xc(i),1e-12);
        Ds = 0.5*(gamma(j,i)+gamma(jS,i))*dx/max(mesh.yc(j)-mesh.yc(jS),1e-12);
        Dn = 0.5*(gamma(j,i)+gamma(jN,i))*dx/max(mesh.yc(jN)-mesh.yc(j),1e-12);

        if strcmpi(c.scheme,'Second-order upwind')
            beta = 0.15;
        else
            beta = 0.0;
        end

        aW = Dw + max(Fw,0) + beta*abs(Fw);
        aE = De + max(-Fe,0) + beta*abs(Fe);
        aS = Ds + max(Fs,0) + beta*abs(Fs);
        aN = Dn + max(-Fn,0) + beta*abs(Fn);
        aP = aW + aE + aS + aN + (Fe-Fw + Fn-Fs);

        if comp == 'u'
            pW = s.p(j,iW); pE = s.p(j,iE);
            Su = (pW - pE)*dy;
            inletVal = c.bc.inlet.Ux;
        else
            pS = s.p(jS,i); pN = s.p(jN,i);
            Su = (pS - pN)*dx;
            inletVal = c.bc.inlet.Uy;
        end

        % Strong BC enforcement
        if i == 1
            aP = 1; aW=0; aE=0; aS=0; aN=0; Su=inletVal;
        elseif i == Nx
            % zero-gradient outlet
            aE = 0;
        end

        if (j == 1 && strcmpi(c.bc.bottom.type,'wall')) || (j == Ny && strcmpi(c.bc.top.type,'wall'))
            aP = 1; aW=0; aE=0; aS=0; aN=0; Su=0;
        end

        aP = max(aP,1e-12);
        aPField(j,i) = aP;

        b(P) = Su;
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

A = sparse(rows(1:ptr), cols(1:ptr), vals(1:ptr), N, N);
phiVec = A \ b;
phiNew = reshape(phiVec, Ny, Nx);
phiNew(~mesh.fluidMask) = 0;
end
