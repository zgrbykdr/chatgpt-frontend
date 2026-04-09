classdef Logger < handle
    properties
        LogDir string
        LogFile string
    end
    methods
        function obj=Logger(logDir)
            if nargin<1 || strlength(logDir)==0, logDir='logs'; end
            if ~exist(logDir,'dir'), mkdir(logDir); end
            obj.LogDir=string(logDir);
            obj.LogFile = fullfile(logDir, "fmu_studio_" + string(datestr(now,'yyyymmdd_HHMMSS')) + ".log");
        end
        function info(obj,msg), obj.write("INFO",msg); end
        function warn(obj,msg), obj.write("WARN",msg); end
        function error(obj,msg), obj.write("ERROR",msg); end
        function write(obj,level,msg)
            line = sprintf('%s [%s] %s\n', datestr(now,31), level, string(msg));
            fprintf('%s',line);
            fid=fopen(obj.LogFile,'a'); fprintf(fid,'%s',line); fclose(fid);
        end
    end
end
