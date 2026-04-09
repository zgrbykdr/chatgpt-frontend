classdef ModelScorer
    methods
        function s = score(~, metrics, model)
            acc = 1/(1+metrics.RMSE+metrics.MAE);
            complexity = 0.2 + 0.1*contains(lower(class(model.TrainedModel)),'ensemble');
            interpret = 1 - complexity;
            runtime = 0.8;
            robust = max(0, 1-metrics.MaxError/(metrics.MaxError+1));
            s = struct('Accuracy',acc,'Interpretability',interpret,'Runtime',runtime, ...
                'Robustness',robust,'Total', 0.45*acc + 0.25*interpret + 0.15*runtime + 0.15*robust);
        end
    end
end
