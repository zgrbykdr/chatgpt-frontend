function cfg = loadConfig(source, overrides, validateOutput)
%LOADCONFIG Load CFD configuration from struct/JSON/MAT with overrides.
%   cfg = cfd.config.loadConfig(source)
%   cfg = cfd.config.loadConfig(source, overrides)
%   cfg = cfd.config.loadConfig(source, overrides, validateOutput)
%
% source can be:
%   - struct: merged over defaults
%   - char/string path to .json or .mat
%
% overrides must be a struct and is merged last.

if nargin < 1 || isempty(source)
    source = struct();
end
if nargin < 2 || isempty(overrides)
    overrides = struct();
end
if nargin < 3 || isempty(validateOutput)
    validateOutput = true;
end

if ~isstruct(overrides)
    error('cfd:config:InvalidOverrides', 'Overrides must be a struct.');
end
if ~(islogical(validateOutput) && isscalar(validateOutput))
    error('cfd:config:InvalidValidateFlag', 'validateOutput must be a logical scalar.');
end

cfg = cfd.config.defaultConfig();
loaded = iReadSource(source);

cfg = cfd.config.mergeConfig(cfg, loaded);
cfg = cfd.config.mergeConfig(cfg, overrides);

if validateOutput
    cfg = cfd.config.validateConfig(cfg);
end
end

function loaded = iReadSource(source)
if isstruct(source)
    loaded = source;
    return;
end

if isstring(source)
    if ~isscalar(source)
        error('cfd:config:InvalidSource', 'String source must be scalar.');
    end
    source = char(source);
end

if ~ischar(source)
    error('cfd:config:InvalidSourceType', 'Source must be a struct or file path.');
end

pathIn = strtrim(source);
if isempty(pathIn)
    loaded = struct();
    return;
end

if ~exist(pathIn, 'file')
    error('cfd:config:FileNotFound', 'Configuration file not found: %s', pathIn);
end

[~, ~, ext] = fileparts(pathIn);
ext = lower(ext);

switch ext
    case '.json'
        loaded = iReadJson(pathIn);
    case '.mat'
        loaded = iReadMat(pathIn);
    otherwise
        error('cfd:config:UnsupportedFileType', ...
            'Unsupported config file extension "%s". Use .json or .mat.', ext);
end
end

function s = iReadJson(pathIn)
raw = fileread(pathIn);
if isempty(strtrim(raw))
    error('cfd:config:EmptyJson', 'JSON config file is empty: %s', pathIn);
end

try
    s = jsondecode(raw);
catch ME
    error('cfd:config:InvalidJson', 'Failed to parse JSON file %s. %s', pathIn, ME.message);
end

if ~isstruct(s)
    error('cfd:config:JsonRootType', 'JSON root must decode to a struct/object.');
end
end

function s = iReadMat(pathIn)
raw = load(pathIn);
if ~isstruct(raw)
    error('cfd:config:InvalidMatContent', 'MAT file did not load as struct.');
end

if isfield(raw, 'cfg') && isstruct(raw.cfg)
    s = raw.cfg;
    return;
end
if isfield(raw, 'config') && isstruct(raw.config)
    s = raw.config;
    return;
end

fns = fieldnames(raw);
if numel(fns) == 1 && isstruct(raw.(fns{1}))
    s = raw.(fns{1});
    return;
end

error('cfd:config:MissingMatStruct', ...
    'MAT file must contain struct variable named cfg/config or a single struct variable.');
end
