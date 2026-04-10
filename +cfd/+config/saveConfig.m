function saveConfig(cfg, outputPath)
%SAVECONFIG Save validated CFD config to JSON or MAT.

if nargin < 2
    error('cfd:config:MissingOutputPath', 'outputPath is required.');
end

cfg = cfd.config.validateConfig(cfg);

if isstring(outputPath)
    if ~isscalar(outputPath)
        error('cfd:config:InvalidOutputPath', 'outputPath must be a scalar string/char.');
    end
    outputPath = char(outputPath);
end
if ~ischar(outputPath)
    error('cfd:config:InvalidOutputPathType', 'outputPath must be string/char.');
end

outputPath = strtrim(outputPath);
if isempty(outputPath)
    error('cfd:config:EmptyOutputPath', 'outputPath cannot be empty.');
end

[parentDir, ~, ext] = fileparts(outputPath);
if ~isempty(parentDir) && ~exist(parentDir, 'dir')
    mkdir(parentDir);
end

switch lower(ext)
    case '.json'
        jsonText = jsonencode(cfg, 'PrettyPrint', true);
        fid = fopen(outputPath, 'w');
        if fid == -1
            error('cfd:config:OpenFailed', 'Unable to open %s for writing.', outputPath);
        end
        cleaner = onCleanup(@() fclose(fid)); %#ok<NASGU>
        bytes = fwrite(fid, jsonText, 'char');
        if bytes <= 0
            error('cfd:config:WriteFailed', 'Failed to write JSON config to %s.', outputPath);
        end
    case '.mat'
        config = cfg; %#ok<NASGU>
        save(outputPath, 'config', '-mat');
    otherwise
        error('cfd:config:UnsupportedSaveType', 'Output extension must be .json or .mat.');
end
end
