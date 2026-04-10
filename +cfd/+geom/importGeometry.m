function state = importGeometry(state, source, mode)
%IMPORTGEOMETRY Import 2D geometry from supported source types.

if nargin < 3 || isempty(mode)
    mode = 'auto';
end
state = iValidateState(state);
mode = iText(mode, 'mode');

if isstruct(source)
    [pts, seg] = iFromStruct(source);
elseif ischar(source) || (isstring(source) && isscalar(source))
    [pts, seg] = iFromFile(char(source), mode);
else
    error('cfd:geom:InvalidSource', 'source must be a struct or file path.');
end

if size(pts,1) < 3
    error('cfd:geom:InsufficientPoints', 'Geometry must contain at least 3 points.');
end

state.raw.points = pts;
state.raw.segments = seg;
if ischar(source)
    state.raw.source = source;
elseif isstring(source)
    state.raw.source = char(source);
else
    state.raw.source = 'struct_input';
end

poly = polyshape(pts(:,1), pts(:,2), 'Simplify', true);
if area(poly) <= 0
    error('cfd:geom:ZeroAreaGeometry', 'Imported geometry has zero/negative area.');
end
state.poly = poly;
state.metrics.area = area(poly);
state.metrics.perimeter = perimeter(poly);
state.metrics.bounding_box = [min(pts(:,1)) max(pts(:,1)) min(pts(:,2)) max(pts(:,2))];
state = cfd.geom.logGeometryEvent(state, 'INFO', sprintf('Imported geometry with %d points.', size(pts,1)));
end

function state = iValidateState(state)
if ~isstruct(state) || ~isscalar(state)
    error('cfd:geom:InvalidState', 'state must be a scalar struct.');
end
end

function txt = iText(val, name)
if isstring(val)
    if ~isscalar(val)
        error('cfd:geom:InvalidText', '%s must be scalar text.', name);
    end
    val = char(val);
end
if ~ischar(val)
    error('cfd:geom:InvalidTextType', '%s must be char/string.', name);
end
txt = strtrim(val);
if isempty(txt)
    error('cfd:geom:EmptyText', '%s cannot be empty.', name);
end
end

function [pts, seg] = iFromStruct(s)
if isfield(s, 'points')
    pts = s.points;
else
    error('cfd:geom:MissingPoints', 'Struct source must contain field "points".');
end
if isfield(s, 'segments')
    seg = s.segments;
else
    seg = [(1:size(pts,1)-1)' (2:size(pts,1))'; size(pts,1) 1];
end
pts = iValidatePoints(pts);
seg = iValidateSegments(seg, size(pts,1));
end

function [pts, seg] = iFromFile(pathIn, mode)
if ~exist(pathIn, 'file')
    error('cfd:geom:FileNotFound', 'Geometry file not found: %s', pathIn);
end
[~,~,ext] = fileparts(pathIn);
ext = lower(ext);
if strcmpi(mode, 'auto')
    mode = ext;
end

switch mode
    case {'.mat','mat'}
        raw = load(pathIn);
        fn = fieldnames(raw);
        selected = [];
        for i = 1:numel(fn)
            if isstruct(raw.(fn{i})) && isfield(raw.(fn{i}), 'points')
                selected = raw.(fn{i});
                break;
            end
        end
        if isempty(selected)
            if isfield(raw, 'points')
                selected = struct('points', raw.points);
                if isfield(raw,'segments'); selected.segments = raw.segments; end
            else
                error('cfd:geom:MatFormat', 'MAT file must contain points or struct with points.');
            end
        end
        [pts, seg] = iFromStruct(selected);
    case {'.json','json'}
        raw = jsondecode(fileread(pathIn));
        [pts, seg] = iFromStruct(raw);
    case {'.txt','txt','.csv','csv'}
        m = readmatrix(pathIn);
        if size(m,2) < 2
            error('cfd:geom:TextFormat', 'Text geometry requires at least 2 columns [x y].');
        end
        pts = iValidatePoints(m(:,1:2));
        seg = [(1:size(pts,1)-1)' (2:size(pts,1))'; size(pts,1) 1];
    otherwise
        error('cfd:geom:UnsupportedFormat', 'Unsupported geometry format: %s', mode);
end
end

function pts = iValidatePoints(pts)
if ~(isnumeric(pts) && size(pts,2)==2 && all(isfinite(pts(:))))
    error('cfd:geom:InvalidPoints', 'points must be finite numeric Nx2 array.');
end
pts = double(pts);
if size(unique(round(pts,12),'rows'),1) < 3
    error('cfd:geom:DegeneratePoints', 'At least three unique points are required.');
end
end

function seg = iValidateSegments(seg, nPts)
if ~(isnumeric(seg) && size(seg,2)==2)
    error('cfd:geom:InvalidSegments', 'segments must be numeric Mx2 array.');
end
if any(seg(:) < 1 | seg(:) > nPts | floor(seg(:))~=seg(:))
    error('cfd:geom:InvalidSegmentIndices', 'segments contain invalid indices.');
end
seg = double(seg);
end
