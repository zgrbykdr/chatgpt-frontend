function improvement = trackQualityImprovement(prevGate, nextGate)
%TRACKQUALITYIMPROVEMENT Compute scalar quality improvement score.

if ~isstruct(prevGate) || ~isstruct(nextGate)
    error('cfd:quality:InvalidGate', 'prevGate and nextGate must be structs.');
end

p = prevGate.quality.summary;
n = nextGate.quality.summary;

dSkew = p.max_skewness_equiangular - n.max_skewness_equiangular;
dOrtho = n.min_orthogonal_quality - p.min_orthogonal_quality;
dAspect = p.max_aspect_ratio - n.max_aspect_ratio;
dSize = p.max_size_change - n.max_size_change;
dDeg = p.num_degenerate - n.num_degenerate;
dInv = p.num_inverted - n.num_inverted;

improvement = struct();
improvement.delta_skewness = dSkew;
improvement.delta_orthogonal_quality = dOrtho;
improvement.delta_aspect_ratio = dAspect;
improvement.delta_size_change = dSize;
improvement.delta_degenerate = dDeg;
improvement.delta_inverted = dInv;
improvement.total_score = dSkew + dOrtho + 0.1*dAspect + 0.1*dSize + dDeg + dInv;
end
