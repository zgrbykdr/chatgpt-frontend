classdef DatasetRepository < handle
    properties
        Runs table = table()
        Train table = table()
        Validation table = table()
        Test table = table()
    end
    methods
        function ingest(obj,t), obj.Runs = [obj.Runs; t]; end
        function split(obj)
            n=height(obj.Runs); idx=randperm(n);
            ntr=round(0.7*n); nv=round(0.15*n);
            obj.Train = obj.Runs(idx(1:ntr),:);
            obj.Validation = obj.Runs(idx(ntr+1:ntr+nv),:);
            obj.Test = obj.Runs(idx(ntr+nv+1:end),:);
        end
    end
end
