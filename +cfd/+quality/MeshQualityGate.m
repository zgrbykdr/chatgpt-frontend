function gate = MeshQualityGate(mesh_state, thresholds)
%MESHQUALITYGATE Evaluate pass/fail and build detailed quality report.

if nargin < 2 || isempty(thresholds)
    thresholds = cfd.quality.defaultQualityThresholds();
end
if ~isstruct(thresholds) || ~isscalar(thresholds)
    error('cfd:quality:InvalidThresholds', 'thresholds must be scalar struct.');
end

req = {'max_skewness','min_orthogonal_quality','max_aspect_ratio','max_size_change','allow_degenerate','allow_inverted'};
for i = 1:numel(req)
    if ~isfield(thresholds, req{i})
        error('cfd:quality:MissingThreshold', 'Missing threshold field: %s', req{i});
    end
end

q = cfd.quality.analyzeMeshQuality(mesh_state);

checks = struct();
checks.skewness_pass = q.summary.max_skewness_equiangular <= thresholds.max_skewness;
checks.orthogonal_pass = q.summary.min_orthogonal_quality >= thresholds.min_orthogonal_quality;
checks.aspect_ratio_pass = q.summary.max_aspect_ratio <= thresholds.max_aspect_ratio;
checks.size_change_pass = q.summary.max_size_change <= thresholds.max_size_change;
checks.degenerate_pass = thresholds.allow_degenerate || (q.summary.num_degenerate == 0);
checks.inverted_pass = thresholds.allow_inverted || (q.summary.num_inverted == 0);

pass = checks.skewness_pass && checks.orthogonal_pass && checks.aspect_ratio_pass && ...
       checks.size_change_pass && checks.degenerate_pass && checks.inverted_pass;

violations = {};
if ~checks.skewness_pass
    violations{end+1} = sprintf('max skewness %.6g > threshold %.6g', q.summary.max_skewness_equiangular, thresholds.max_skewness); %#ok<AGROW>
end
if ~checks.orthogonal_pass
    violations{end+1} = sprintf('min orthogonal quality %.6g < threshold %.6g', q.summary.min_orthogonal_quality, thresholds.min_orthogonal_quality); %#ok<AGROW>
end
if ~checks.aspect_ratio_pass
    violations{end+1} = sprintf('max aspect ratio %.6g > threshold %.6g', q.summary.max_aspect_ratio, thresholds.max_aspect_ratio); %#ok<AGROW>
end
if ~checks.size_change_pass
    violations{end+1} = sprintf('max size change %.6g > threshold %.6g', q.summary.max_size_change, thresholds.max_size_change); %#ok<AGROW>
end
if ~checks.degenerate_pass
    violations{end+1} = sprintf('degenerate elements detected: %d', q.summary.num_degenerate); %#ok<AGROW>
end
if ~checks.inverted_pass
    violations{end+1} = sprintf('inverted elements detected: %d', q.summary.num_inverted); %#ok<AGROW>
end

gate = struct();
gate.pass = pass;
gate.checks = checks;
gate.thresholds = thresholds;
gate.quality = q;
gate.violations = violations;
gate.report = cfd.quality.generateQualityReport(gate);
end
