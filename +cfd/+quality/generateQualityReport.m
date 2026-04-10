function txt = generateQualityReport(gate)
%GENERATEQUALITYREPORT Build detailed text report for quality gate.

if ~isstruct(gate) || ~isscalar(gate)
    error('cfd:quality:InvalidGate', 'gate must be scalar struct.');
end
if ~isfield(gate, 'quality') || ~isfield(gate.quality, 'summary')
    error('cfd:quality:MissingQualitySummary', 'gate.quality.summary is required.');
end

s = gate.quality.summary;
status = 'FAIL';
if isfield(gate,'pass') && gate.pass
    status = 'PASS';
end

lines = { ...
    sprintf('Mesh Quality Gate: %s', status), ...
    sprintf('  max skewness (equiangular): %.6g', s.max_skewness_equiangular), ...
    sprintf('  min orthogonal quality: %.6g', s.min_orthogonal_quality), ...
    sprintf('  max aspect ratio: %.6g', s.max_aspect_ratio), ...
    sprintf('  max size change: %.6g', s.max_size_change), ...
    sprintf('  degenerate elements: %d', s.num_degenerate), ...
    sprintf('  inverted elements: %d', s.num_inverted)};

if isfield(gate, 'violations') && ~isempty(gate.violations)
    lines{end+1} = 'Violations:'; %#ok<AGROW>
    for i = 1:numel(gate.violations)
        lines{end+1} = sprintf('  - %s', gate.violations{i}); %#ok<AGROW>
    end
end

txt = strjoin(lines, newline);
end
