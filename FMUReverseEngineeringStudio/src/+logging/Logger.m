classdef Logger < handle
    properties
        LogDir string
        LogFile string
    end
    methods
        function obj=Logger(logDir)
            if nargin<1 || strlength(logDir)==0, logDir='logs'; end
            if ~exist(char(logDir),'dir'), mkdir(char(logDir)); end
            obj.LogDir=string(logDir);
            obj.LogFile = string(fullfile(char(logDir), char("fmu_studio_" + string(datestr(now,'yyyymmdd_HHMMSS')) + ".log")));
            % Create file eagerly so users can immediately verify log output.
            fid = fopen(char(obj.LogFile),'a');
            if fid >= 0
                fprintf(fid,'=== FMU Reverse Engineering Studio log started %s ===\n', datestr(now,31));
                fclose(fid);
            end
        end
        function info(obj,msg), obj.write("INFO",msg); end
        function warn(obj,msg), obj.write("WARN",msg); end
        function error(obj,msg), obj.write("ERROR",msg); end
        function write(obj,level,msg)
            line = sprintf('%s [%s] %s\n', datestr(now,31), level, string(msg));
            fprintf('%s',line);
            fid=fopen(char(obj.LogFile),'a');
            if fid < 0
                % Fallback to temp directory if primary log file is unavailable.
                fallback = fullfile(tempdir, 'fmu_studio_fallback.log');
                fid = fopen(fallback,'a');
            end
            if fid >= 0
                fprintf(fid,'%s',line);
                fclose(fid);
            end
        end
    end
end
