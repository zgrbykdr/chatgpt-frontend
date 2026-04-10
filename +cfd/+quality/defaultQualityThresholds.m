function thresholds = defaultQualityThresholds()
%DEFAULTQUALITYTHRESHOLDS Safe default quality thresholds.

thresholds = struct();
thresholds.max_skewness = 0.85;
thresholds.min_orthogonal_quality = 0.15;
thresholds.max_aspect_ratio = 150;
thresholds.max_size_change = 3.0;
thresholds.allow_degenerate = false;
thresholds.allow_inverted = false;
thresholds.target_improvement = 0.05;
thresholds.min_attempt_improvement = 1e-3;
end
