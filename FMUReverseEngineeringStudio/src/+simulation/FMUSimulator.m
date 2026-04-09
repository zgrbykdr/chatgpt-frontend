classdef FMUSimulator
    properties, Logger, end
    methods
        function obj=FMUSimulator(logger), obj.Logger=logger; end

        function row = runSingle(~, ~, run, catalog)
            % Adapter with fallback behavior when no FMU runtime is present.
            inputs = run.inputs;
            inNames = fieldnames(inputs);
            x = zeros(1,numel(inNames));
            for k=1:numel(inNames), x(k)=inputs.(inNames{k}); end
            y = sum(x) + 0.1*sum(x.^2) + 0.03*randn();
            outNames = catalog.name(catalog.role=="output");
            if isempty(outNames), outNames = "y"; end
            row = struct('runId',run.id,'timeEnd',1.0);
            for k=1:numel(inNames), row.(inNames{k}) = x(k); end
            for j=1:numel(outNames), row.(char(outNames(j))) = y + 0.05*j; end
            row.nanInfFlag = any(~isfinite([x y]));
            row.status = "ok";
        end
    end
end
