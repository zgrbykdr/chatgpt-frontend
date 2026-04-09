classdef ModelFactory
    properties, Logger, end
    methods
        function obj=ModelFactory(logger), obj.Logger=logger; end
        function mdl = create(obj, family, ~, ~)
            family = string(family);
            if startsWith(family,"equation")
                mdl = models.equation.EquationModeler(obj.Logger,family);
            elseif family=="piecewise"
                mdl = models.piecewise.PiecewiseModeler(obj.Logger);
            elseif family=="dynamic"
                mdl = models.dynamic.DynamicModeler(obj.Logger);
            elseif family=="statistical"
                mdl = models.statistical.StatisticalModeler(obj.Logger);
            else
                mdl = models.lut.LUTModeler(obj.Logger);
            end
        end
    end
end
