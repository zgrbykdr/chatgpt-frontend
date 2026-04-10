function turb = updateTurbulenceFields(cfg, mesh_state, flow, turb, dt)
%UPDATETURBULENCEFIELDS Update turbulence fields for selected model.

if nargin < 5 || isempty(dt)
    dt = 1e-3;
end
cfg = cfd.config.validateConfig(cfg);
modelFn = cfd.turbulence.TurbulenceModelFactory(cfg.turbulence.model);

turb = modelFn(mesh_state, flow, turb, cfg, dt);
turb = cfd.turbulence.TurbulenceFieldLimiter(turb);
[ok, details] = cfd.turbulence.validateTurbulenceState(turb);
if ~ok
    error('cfd:turbulence:UnstableFields', 'Unstable turbulence fields detected (invalid=%d, negative=%d).', ...
        details.invalid_count, details.negative_count);
end
end
