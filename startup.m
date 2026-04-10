function startup()
%STARTUP Add project paths for MATLAB execution.

root = fileparts(mfilename('fullpath'));
addpath(root);
fprintf('CFD project paths initialized from: %s\n', root);
end
