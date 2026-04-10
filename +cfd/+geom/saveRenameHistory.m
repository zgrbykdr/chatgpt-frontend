function saveRenameHistory(state, outputPath)
%SAVERENAMEHISTORY Persist selection rename history to MAT/JSON.

if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~(ischar(outputPath) || (isstring(outputPath) && isscalar(outputPath)))
    error('cfd:geom:InvalidOutputPath', 'outputPath must be char/string scalar.');
end
outputPath = char(outputPath);
[dirp,~,ext] = fileparts(outputPath);
if ~isempty(dirp) && ~exist(dirp,'dir')
    mkdir(dirp);
end
rename_history = state.rename_history; %#ok<NASGU>
switch lower(ext)
    case '.mat'
        save(outputPath, 'rename_history', '-mat');
    case '.json'
        txt = jsonencode(rename_history, 'PrettyPrint', true);
        fid = fopen(outputPath, 'w');
        if fid < 0
            error('cfd:geom:OpenFailed', 'Cannot open %s for writing.', outputPath);
        end
        c = onCleanup(@() fclose(fid)); %#ok<NASGU>
        fwrite(fid, txt, 'char');
    otherwise
        error('cfd:geom:UnsupportedFile', 'Use .mat or .json extension.');
end
end
