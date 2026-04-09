classdef Preprocessor
    methods
        function out = clean(~, raw)
            if isempty(raw), out = table(); return; end
            out = raw;
            out = out(~any(ismissing(out),2),:);
            numVars = varfun(@isnumeric,out,'OutputFormat','uniform');
            cols = out.Properties.VariableNames(numVars);
            for c=1:numel(cols)
                v = out.(cols{c});
                q = quantile(v,[0.01 0.99]);
                out.(cols{c}) = min(max(v,q(1)),q(2));
            end
        end
    end
end
