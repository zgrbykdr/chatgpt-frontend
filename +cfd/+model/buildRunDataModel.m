function model = buildRunDataModel(configSource, overrides)
%BUILDRUNDATAMODEL Build validated run data model from config input.

if nargin < 1
    configSource = struct();
end
if nargin < 2
    overrides = struct();
end

cfg = cfd.config.loadConfig(configSource, overrides, true);
model = cfd.model.defaultDataModel(cfg);
end
