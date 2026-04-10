function exportResults(fileBase, state, report)
% Export result fields to MAT and CSV.
if nargin<1 || isempty(fileBase)
    fileBase = fullfile(pwd, ['rans2d_' datestr(now,'yyyymmdd_HHMMSS')]);
end

mesh = report.mesh;
post = report.post;

matFile = [fileBase '.mat'];
save(matFile, 'state', 'report', 'mesh', 'post');

csvFile = [fileBase '.csv'];
[X,Y] = meshgrid(mesh.xc, mesh.yc);
T = table(X(:), Y(:), state.u(:), state.v(:), state.p(:), state.k(:), state.epsilon(:), state.omega(:), state.mut(:), ...
    'VariableNames', {'x','y','u','v','p','k','epsilon','omega','mut'});
writetable(T, csvFile);
end
