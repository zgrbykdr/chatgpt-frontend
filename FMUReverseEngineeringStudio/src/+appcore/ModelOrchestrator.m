classdef ModelOrchestrator < handle
    properties
        Logger
        FallbackChain string = ["equation.simple","equation.rich","equation.sparse","piecewise","dynamic","statistical","lut"]
    end

    methods
        function obj = ModelOrchestrator(logger)
            obj.Logger = logger;
        end

        function out = fitAndRank(obj, dataset, diagnostics, mode)
            factory = models.ModelFactory(obj.Logger);
            scorer = validation.ModelScorer();
            allCandidates = struct([]);
            k=1;
            for family = obj.FallbackChain
                mdl = factory.create(family, diagnostics, mode);
                try
                    fitted = mdl.fit(dataset);
                    val = validation.ValidationRunner().evaluate(fitted, dataset);
                    score = scorer.score(val, fitted);
                    allCandidates(k).Name = fitted.Name;
                    allCandidates(k).Family = string(family);
                    allCandidates(k).Metrics = val;
                    allCandidates(k).Score = score.Total;
                    allCandidates(k).Interpretability = score.Interpretability;
                    allCandidates(k).Runtime = score.Runtime;
                    k = k + 1;
                catch ME
                    obj.Logger.warn("Model family failed: " + family + " - " + ME.message);
                end
            end
            if isempty(allCandidates)
                error('No candidate models were fit successfully.');
            end
            [~,idx] = sort([allCandidates.Score],'descend');
            ranked = allCandidates(idx);
            out = struct('BestModel',ranked(1), 'Candidates',ranked, 'Scoreboard', ranked);
        end
    end
end
