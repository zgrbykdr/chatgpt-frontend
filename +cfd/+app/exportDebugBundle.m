function bundlePath = exportDebugBundle(runState, outDir)
%EXPORTDEBUGBUNDLE Save detailed debug bundle for failed/safe-terminated runs.

if nargin < 2 || isempty(outDir)
    outDir = fullfile(pwd, 'debug');
end
if ~isstruct(runState) || ~isscalar(runState)
    error('cfd:app:InvalidRunState', 'runState must be scalar struct.');
end
if ~exist(outDir,'dir'); mkdir(outDir); end

ts = char(datetime('now','TimeZone','UTC','Format','yyyyMMdd''T''HHmmss''Z'''));
bundlePath = fullfile(outDir, ['debug_bundle_' ts '.mat']);
state = runState; %#ok<NASGU>
save(bundlePath, 'state', '-mat');
end
