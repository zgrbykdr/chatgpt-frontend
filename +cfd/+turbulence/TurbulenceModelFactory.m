function model = TurbulenceModelFactory(modelName)
%TURBULENCEMODELFACTORY Return turbulence model update function handle.

if isstring(modelName)
    if ~isscalar(modelName)
        error('cfd:turbulence:InvalidModelName', 'modelName must be scalar.');
    end
    modelName = char(modelName);
end
if ~ischar(modelName)
    error('cfd:turbulence:InvalidModelNameType', 'modelName must be char/string.');
end

switch lower(strtrim(modelName))
    case 'spalart_allmaras'
        model = @cfd.turbulence.SpalartAllmarasModel;
    case 'k_epsilon_standard'
        model = @cfd.turbulence.KEpsilonStandardModel;
    case 'k_epsilon_rng'
        model = @cfd.turbulence.KEpsilonRNGModel;
    case 'k_epsilon_realizable'
        model = @cfd.turbulence.KEpsilonRealizableModel;
    case 'k_omega_standard'
        model = @cfd.turbulence.KOmegaStandardModel;
    case 'k_omega_sst'
        model = @cfd.turbulence.KOmegaSSTModel;
    otherwise
        error('cfd:turbulence:UnsupportedModel', 'Unsupported turbulence model: %s', modelName);
end
end
