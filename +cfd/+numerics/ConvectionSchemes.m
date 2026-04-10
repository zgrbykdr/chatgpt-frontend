function phiFace = ConvectionSchemes(phiP, phiN, gradP, dPN, scheme, massFlux)
%CONVECTIONSCHEMES Compute face value for upwind schemes.

if nargin < 6
    error('cfd:numerics:MissingArgs', 'Need phiP, phiN, gradP, dPN, scheme, massFlux.');
end
if ~(isnumeric(phiP)&&isscalar(phiP)&&isfinite(phiP)&&isnumeric(phiN)&&isscalar(phiN)&&isfinite(phiN))
    error('cfd:numerics:InvalidPhi', 'phiP and phiN must be finite scalars.');
end
if ~(isnumeric(gradP)&&numel(gradP)==2&&all(isfinite(gradP)))
    error('cfd:numerics:InvalidGrad', 'gradP must be finite 1x2 vector.');
end
if ~(isnumeric(dPN)&&numel(dPN)==2&&all(isfinite(dPN)))
    error('cfd:numerics:InvalidDPN', 'dPN must be finite 1x2 vector.');
end

switch lower(scheme)
    case 'first_order_upwind'
        if massFlux >= 0
            phiFace = phiP;
        else
            phiFace = phiN;
        end
    case 'second_order_upwind'
        if massFlux >= 0
            phiFace = phiP + dot(gradP(:), 0.5*dPN(:));
        else
            phiFace = phiN;
        end
    otherwise
        error('cfd:numerics:UnknownScheme', 'Unknown convection scheme: %s', scheme);
end
end
