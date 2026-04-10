function edges = detectFeatureEdges(state, angleThresholdDeg)
%DETECTFEATUREEDGES Detect sharp feature edges on polygon boundary.

if nargin < 2 || isempty(angleThresholdDeg)
    angleThresholdDeg = 25;
end
if ~(isnumeric(angleThresholdDeg) && isscalar(angleThresholdDeg) && isfinite(angleThresholdDeg) && angleThresholdDeg > 0 && angleThresholdDeg < 180)
    error('cfd:geom:InvalidAngleThreshold', 'angleThresholdDeg must be in (0,180).');
end
if ~isstruct(state) || ~isscalar(state) || ~isfield(state, 'poly') || isempty(state.poly)
    error('cfd:geom:InvalidState', 'Valid state.poly is required.');
end

v = state.poly.Vertices;
if size(v,1) < 4
    edges = zeros(0,2);
    return;
end

if norm(v(1,:) - v(end,:)) > 0
    v(end+1,:) = v(1,:);
end
n = size(v,1)-1;
mark = false(n,1);
for i = 2:(n-1)
    a = v(i,:) - v(i-1,:);
    b = v(i+1,:) - v(i,:);
    ang = acosd(max(-1,min(1, dot(a,b)/(norm(a)*norm(b)+eps))));
    if abs(180-ang) > angleThresholdDeg
        mark(i) = true;
    end
end
idx = find(mark);
edges = [idx idx+1];
end
