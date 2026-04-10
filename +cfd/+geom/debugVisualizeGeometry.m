function fig = debugVisualizeGeometry(state, titleText)
%DEBUGVISUALIZEGEOMETRY Plot geometry diagnostics for debug workflows.

if nargin < 2 || isempty(titleText)
    titleText = 'Geometry Debug View';
end
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be scalar struct.');
end
if ~(ischar(titleText) || (isstring(titleText) && isscalar(titleText)))
    error('cfd:geom:InvalidTitle', 'titleText must be char/string scalar.');
end

fig = figure('Name', char(titleText), 'Color', 'w');
ax = axes(fig);
hold(ax, 'on'); axis(ax, 'equal'); grid(ax, 'on');

if isfield(state, 'poly') && ~isempty(state.poly)
    plot(ax, state.poly, 'FaceColor', [0.8 0.9 1.0], 'FaceAlpha', 0.35, 'EdgeColor', [0.1 0.2 0.8]);
end
if isfield(state, 'fluid_region') && ~isempty(state.fluid_region)
    plot(ax, state.fluid_region, 'FaceColor', [0.8 1.0 0.8], 'FaceAlpha', 0.25, 'EdgeColor', [0.0 0.5 0.0]);
end
if isfield(state, 'enclosure') && ~isempty(state.enclosure)
    plot(ax, state.enclosure, 'FaceColor', 'none', 'LineStyle', '--', 'EdgeColor', [0.6 0.1 0.1]);
end

if isfield(state, 'raw') && isstruct(state.raw) && isfield(state.raw, 'points') && ~isempty(state.raw.points)
    scatter(ax, state.raw.points(:,1), state.raw.points(:,2), 12, 'k', 'filled');
end

xlabel(ax, 'X'); ylabel(ax, 'Y');
title(ax, char(titleText), 'Interpreter', 'none');
legend(ax, {'poly','fluid_region','enclosure','raw_points'}, 'Location', 'bestoutside');

if nargout == 0
    clear fig;
end
end
