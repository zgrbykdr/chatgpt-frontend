function s = solveTurbulence(s, c, mesh)
% Solve turbulence transport equations for selected model.
model = lower(strtrim(c.model));
if strcmp(model,'laminar')
    s.k(:) = c.clip.kMin;
    s.epsilon(:) = c.clip.epsMin;
    s.omega(:) = c.clip.omMin;
    s.mut(:) = 0;
    return;
end

Gk = productionTerm(s, c, mesh);

if contains(model,'epsilon')
    [kNew,~] = solveTransport(s.k, s, c, mesh, c.mu + s.mut/1.0, Gk, 'k');
    [eNew,~] = solveTransport(s.epsilon, s, c, mesh, c.mu + s.mut/1.3, Gk, 'epsilon');

    s.k = c.urf.k*kNew + (1-c.urf.k)*s.k;
    s.epsilon = c.urf.epsilon*eNew + (1-c.urf.epsilon)*s.epsilon;

elseif contains(model,'omega')
    [kNew,~] = solveTransport(s.k, s, c, mesh, c.mu + s.mut/2.0, Gk, 'k');
    [oNew,~] = solveTransport(s.omega, s, c, mesh, c.mu + s.mut/2.0, Gk, 'omega');

    s.k = c.urf.k*kNew + (1-c.urf.k)*s.k;
    s.omega = c.urf.omega*oNew + (1-c.urf.omega)*s.omega;
end

s.k = max(s.k, c.clip.kMin);
s.epsilon = max(s.epsilon, c.clip.epsMin);
s.omega = max(s.omega, c.clip.omMin);

s = updateTurbulenceViscosity(s, c, mesh);
end

function Gk = productionTerm(s, c, mesh)
[dux, duy] = grad(s.u, mesh);
[dvx, dvy] = grad(s.v, mesh);
S2 = 2*(dux.^2 + dvy.^2) + (duy + dvx).^2;
Gk = max(s.mut .* S2, 0);

if strcmpi(c.model,'SST k-omega')
    Gk = min(Gk, 10*c.rho*0.09.*s.k.*s.omega);
end
end

function [phiNew, aPField] = solveTransport(phi, s, c, mesh, gamma, Gk, kind)
Ny = mesh.Ny; Nx = mesh.Nx;
N = Ny*Nx;
rho = c.rho;

rows = zeros(5*N,1);
cols = zeros(5*N,1);
vals = zeros(5*N,1);
b = zeros(N,1);
ptr = 0;
aPField = ones(Ny,Nx);

flux = computeFaceFluxes(s, c, mesh);
inlet = computeTurbulenceInlet(c);

for j = 1:Ny
    dy = mesh.dy(j);
    for i = 1:Nx
        P = sub2ind([Ny,Nx],j,i);

        if ~mesh.fluidMask(j,i)
            ptr=ptr+1; rows(ptr)=P; cols(ptr)=P; vals(ptr)=1; b(P)=0;
            continue;
        end

        dx = mesh.dx(i);
        iW = max(1,i-1); iE = min(Nx,i+1);
        jS = max(1,j-1); jN = min(Ny,j+1);

        Fw = flux.Fw(j,i); Fe = flux.Fe(j,i); Fs = flux.Fs(j,i); Fn = flux.Fn(j,i);
        Dw = 0.5*(gamma(j,i)+gamma(j,iW))*dy/max(mesh.xc(i)-mesh.xc(iW),1e-12);
        De = 0.5*(gamma(j,i)+gamma(j,iE))*dy/max(mesh.xc(iE)-mesh.xc(i),1e-12);
        Ds = 0.5*(gamma(j,i)+gamma(jS,i))*dx/max(mesh.yc(j)-mesh.yc(jS),1e-12);
        Dn = 0.5*(gamma(j,i)+gamma(jN,i))*dx/max(mesh.yc(jN)-mesh.yc(j),1e-12);

        aW = Dw + max(Fw,0);
        aE = De + max(-Fe,0);
        aS = Ds + max(Fs,0);
        aN = Dn + max(-Fn,0);

        [Sp, Su] = sourceTerms(kind, s, c, Gk(j,i), j, i, mesh);
        aP = aW + aE + aS + aN - Sp*dx*dy;

        if i == 1
            switch kind
                case 'k', val = inlet.k;
                case 'epsilon', val = inlet.epsilon;
                case 'omega', val = inlet.omega;
                otherwise, val = 0;
            end
            aP=1; aW=0; aE=0; aS=0; aN=0; Su = val/(dx*dy);
        elseif i == Nx
            aE = 0; % zero-gradient outlet
        end

        if j == 1 || j == Ny
            if strcmp(kind,'k')
                val = c.clip.kMin;
            elseif strcmp(kind,'epsilon')
                y = max(mesh.wallDist(j,i),1e-8);
                val = max(c.clip.epsMin, 2*c.mu/c.rho*max(s.k(j,i),c.clip.kMin)/y^2);
            else
                y = max(mesh.wallDist(j,i),1e-8);
                val = max(c.clip.omMin, 60*c.mu/(c.rho*0.075*y^2));
            end
            aP=1; aW=0; aE=0; aS=0; aN=0; Su = val/(dx*dy);
        end

        aP = max(aP,1e-12);
        aPField(j,i) = aP;

        b(P) = Su*dx*dy;
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

function [Sp, Su] = sourceTerms(kind, s, c, Gk, j, i, mesh)
rho = c.rho;
k = max(s.k(j,i),c.clip.kMin);
epsVal = max(s.epsilon(j,i),c.clip.epsMin);
omegaVal = max(s.omega(j,i),c.clip.omMin);

switch lower(kind)
    case 'k'
        Sp = 0;
        Su = max(Gk - rho*epsVal, 0);

    case 'epsilon'
        switch lower(c.model)
            case 'rng k-epsilon'
                C1 = 1.42; C2 = 1.68;
            case 'realizable k-epsilon'
                C1 = 1.44;
                C2 = 1.90;
            otherwise
                C1 = 1.44; C2 = 1.92;
        end
        Su = C1*(epsVal/k)*Gk;
        Sp = -rho*C2*(epsVal/k);

    case 'omega'
        if strcmpi(c.model,'sst k-omega')
            alpha = 0.52;
            beta = 0.075;
            [dkdx, dkdy] = grad(s.k, mesh);
            [dwdx, dwdy] = grad(s.omega, mesh);
            crossDiff = max(2*rho*0.856*(dkdx(j,i)*dwdx(j,i)+dkdy(j,i)*dwdy(j,i))/max(omegaVal,1e-10),0);
        else
            alpha = 5/9;
            beta = 0.072;
            crossDiff = 0;
        end
        Su = alpha*(omegaVal/k)*Gk + crossDiff;
        Sp = -rho*beta*omegaVal;

    otherwise
        Sp = 0;
        Su = 0;
end
end

function [gx, gy] = grad(phi, mesh)
[Ny,Nx] = size(phi);
gx = zeros(Ny,Nx); gy = zeros(Ny,Nx);
for i=2:Nx-1
    gx(:,i) = (phi(:,i+1)-phi(:,i-1))/max(mesh.xc(i+1)-mesh.xc(i-1),1e-12);
end
gx(:,1) = gx(:,2); gx(:,Nx)=gx(:,Nx-1);
for j=2:Ny-1
    gy(j,:) = (phi(j+1,:)-phi(j-1,:))/max(mesh.yc(j+1)-mesh.yc(j-1),1e-12);
end
gy(1,:)=gy(2,:); gy(Ny,:)=gy(Ny-1,:);
end
