function turb = TurbulenceFieldLimiter(turb)
%TURBULENCEFIELDLIMITER Enforce positivity and bounded turbulence fields.

if ~isstruct(turb) || ~isscalar(turb)
    error('cfd:turbulence:InvalidState', 'turb must be scalar struct.');
end

minVal = 1e-12;
maxNut = 1e3;
fields = fieldnames(turb);
for i = 1:numel(fields)
    fn = fields{i};
    v = turb.(fn);
    if isnumeric(v)
        v(~isfinite(v)) = minVal;
        if strcmp(fn,'nut') || strcmp(fn,'nu_tilde')
            v = min(max(v,minVal),maxNut);
        else
            v = max(v,minVal);
        end
        turb.(fn) = v;
    end
end
end
