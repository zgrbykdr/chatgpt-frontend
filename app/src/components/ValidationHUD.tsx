import React from 'react';
import type { ValidationSummary } from '../lib/schemas';

interface Props {
  validation: ValidationSummary;
}

export const ValidationHUD: React.FC<Props> = ({ validation }) => {
  return (
    <div className="pointer-events-none absolute bottom-4 left-4 w-72 rounded-lg border border-slate-700 bg-slate-900/80 p-3 text-xs text-slate-200 shadow">
      <p className="text-sm font-semibold text-slate-100">Validation</p>
      <div className="mt-2 space-y-1">
        <div className="flex justify-between">
          <span>Energy residual</span>
          <span>{validation.energyResidual.toExponential(2)}</span>
        </div>
        <div className="flex justify-between">
          <span>Jacobian κ</span>
          <span>{validation.jacobianCondition.toFixed(1)}</span>
        </div>
      </div>
      {validation.warnings.length > 0 && (
        <ul className="mt-2 list-disc pl-4 text-[11px] text-amber-300">
          {validation.warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      )}
    </div>
  );
};
