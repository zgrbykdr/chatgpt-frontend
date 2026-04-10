function logger = Logger(logPath)
%LOGGER Create structured logger with file sink and in-memory events.

if nargin < 1 || isempty(logPath)
    logPath = fullfile(pwd, 'run.log');
end
if ~(ischar(logPath) || (isstring(logPath) && isscalar(logPath)))
    error('cfd:log:InvalidPath', 'logPath must be char/string scalar.');
end
logPath = char(logPath);
[logDir,~,~] = fileparts(logPath);
if ~isempty(logDir) && ~exist(logDir,'dir')
    mkdir(logDir);
end

state = struct('path',logPath,'events',{{}});

logger = struct();
logger.info = @(msg) iWrite('INFO', msg);
logger.warn = @(msg) iWrite('WARN', msg);
logger.error = @(msg) iWrite('ERROR', msg);
logger.getEvents = @() state.events;
logger.path = logPath;

    function iWrite(level, msg)
        if ~(ischar(msg) || (isstring(msg) && isscalar(msg)))
            error('cfd:log:InvalidMessage', 'Message must be char/string scalar.');
        end
        entry = struct('timestamp_utc', char(datetime('now','TimeZone','UTC','Format','yyyy-MM-dd''T''HH:mm:ss''Z''')), ...
            'level', upper(level), 'message', char(msg));
        state.events{end+1,1} = entry;
        fid = fopen(state.path, 'a');
        if fid ~= -1
            fprintf(fid, '[%s] %s %s\n', entry.timestamp_utc, entry.level, entry.message);
            fclose(fid);
        end
    end
end
