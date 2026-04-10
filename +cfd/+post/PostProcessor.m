function post = PostProcessor(cfg, mesh_state, solution, outDir)
%POSTPROCESSOR Generate postprocess artifacts and summary.

if nargin < 4 || isempty(outDir)
    outDir = fullfile(pwd, 'outputs');
end
cfg = cfd.config.validateConfig(cfg);
if ~exist(outDir,'dir'); mkdir(outDir); end

cc = mesh_state.fv.cell_centers;
u = solution.u; v = solution.v; p = solution.p;
velMag = sqrt(u.^2 + v.^2);

summary = struct();
summary.mean_velocity = mean(velMag);
summary.max_velocity = max(velMag);
summary.min_pressure = min(p);
summary.max_pressure = max(p);
summary.converged = logical(solution.converged(1));
summary.turbulence_model = cfg.turbulence.model;

csvPath = fullfile(outDir, 'field_cells.csv');
T = table(cc(:,1), cc(:,2), u, v, p, velMag, 'VariableNames', {'x','y','u','v','p','vel_mag'});
writetable(T, csvPath);

jsonPath = fullfile(outDir, 'summary.json');
fid = fopen(jsonPath, 'w');
if fid == -1
    error('cfd:post:FileOpenFailed', 'Could not open summary.json for writing.');
end
c = onCleanup(@() fclose(fid)); %#ok<NASGU>
fwrite(fid, jsonencode(summary, 'PrettyPrint', true), 'char');

post = struct('summary',summary,'cell_csv',csvPath,'summary_json',jsonPath);
end
