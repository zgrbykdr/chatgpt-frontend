function state = GeometryManager(cfg, source, options)
%GEOMETRYMANAGER Facade for full geometry processing execution.

if nargin < 1
    cfg = cfd.config.defaultConfig();
end
if nargin < 2 || isempty(source)
    source = cfg.geometry.file_path;
end
if nargin < 3
    options = struct();
end

state = cfd.geom.processGeometryPipeline(cfg, source, options);
end
