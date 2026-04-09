classdef (Abstract) CandidateModel < handle
    properties
        Name string
        Family string
        TrainedModel
        Metadata struct = struct()
    end
    methods (Abstract)
        out = fit(obj,dataset)
        y = predict(obj,X)
    end
end
