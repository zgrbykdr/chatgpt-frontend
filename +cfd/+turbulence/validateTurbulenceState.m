function [isStable, details] = validateTurbulenceState(turb)
%VALIDATETURBULENCESTATE Stability checks for turbulence fields.

if ~isstruct(turb) || ~isscalar(turb)
    error('cfd:turbulence:InvalidState', 'turb must be scalar struct.');
end

fields = fieldnames(turb);
numInvalid = 0;
numNegative = 0;
for i = 1:numel(fields)
    v = turb.(fields{i});
    if isnumeric(v)
        numInvalid = numInvalid + nnz(~isfinite(v));
        numNegative = numNegative + nnz(v < 0);
    end
end

isStable = (numInvalid == 0) && (numNegative == 0);
details = struct('invalid_count',numInvalid,'negative_count',numNegative);
end
