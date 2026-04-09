classdef MetricCalculator
    methods (Static)
        function m = compute(y,yhat)
            e = y-yhat;
            m = struct();
            m.RMSE = sqrt(mean(e.^2,'omitnan'));
            m.MAE = mean(abs(e),'omitnan');
            m.MaxError = max(abs(e));
            m.R2 = 1 - sum(e.^2)/max(eps,sum((y-mean(y)).^2));
            m.NRMSE = m.RMSE/max(eps,(max(y)-min(y)));
            m.TransientError = prctile(abs(e),95);
            m.SteadyStateError = mean(abs(e(end-max(1,floor(numel(e)/10)):end)));
        end
    end
end
