classdef ExportManager
    properties, Logger, end
    methods
        function obj=ExportManager(logger), obj.Logger=logger; end
        function exportAll(obj,modelResult,outDir)
            if ~exist(outDir,'dir'), mkdir(outDir); end
            exporter.MatlabExporter.exportModel(modelResult.BestModel, outDir);
            exporter.ReportExporter.writeComparison(modelResult, outDir);
            obj.Logger.info("Exports created in " + outDir);
        end
    end
end
