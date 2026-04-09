classdef RangeInferenceEngine
    properties, Logger, end
    methods
        function obj = RangeInferenceEngine(logger), obj.Logger=logger; end

        function rangeState = inferInitialRanges(obj, catalog, ~)
            n = height(catalog);
            rangeState = table('Size',[n 6], 'VariableTypes',{'string','double','double','string','double','string'}, ...
                'VariableNames',{'name','low','high','source','confidence','strictness'});
            for i=1:n
                lo = str2double(catalog.minValue(i));
                hi = str2double(catalog.maxValue(i));
                src="fmu"; conf=0.9; strict="hard";
                if isnan(lo) || isnan(hi) || lo>=hi
                    sv = str2double(catalog.startValue(i));
                    if isnan(sv), sv = 0; end
                    lo = sv - max(1,abs(sv))*2;
                    hi = sv + max(1,abs(sv))*2;
                    src="inferred"; conf=0.55; strict="soft";
                end
                rangeState.name(i)=catalog.name(i);
                rangeState.low(i)=lo;
                rangeState.high(i)=hi;
                rangeState.source(i)=src;
                rangeState.confidence(i)=conf;
                rangeState.strictness(i)=strict;
                catalog.inferredRange(i)=sprintf('[%g,%g]',lo,hi);
            end
        end

        function [ok,newRange] = safeProbe(~, baseRange, probePoint, isStableFcn)
            ok = false; newRange = baseRange;
            try
                if isStableFcn(probePoint)
                    newRange = [min(baseRange(1),probePoint), max(baseRange(2),probePoint)];
                    ok = true;
                end
            catch
                ok = false; % rollback behavior
            end
        end
    end
end
