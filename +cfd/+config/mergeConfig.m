function out = mergeConfig(base, override)
%MERGECONFIG Recursively merge struct override into base.

if nargin < 1 || isempty(base)
    base = struct();
end
if nargin < 2 || isempty(override)
    out = base;
    return;
end

if ~isstruct(base) || ~isscalar(base)
    error('cfd:config:InvalidBaseConfig', 'Base config must be a scalar struct.');
end
if ~isstruct(override) || ~isscalar(override)
    error('cfd:config:InvalidOverrideConfig', 'Override config must be a scalar struct.');
end

out = base;
fields = fieldnames(override);
for k = 1:numel(fields)
    fn = fields{k};
    val = override.(fn);
    if isfield(out, fn) && isstruct(out.(fn)) && isscalar(out.(fn)) && isstruct(val) && isscalar(val)
        out.(fn) = cfd.config.mergeConfig(out.(fn), val);
    else
        out.(fn) = val;
    end
end
end
