import React, { useMemo } from 'react';
import { useSimulationStore } from '../state/simulationStore';

const componentLibrary = [
  { type: 'Evaporator', modeling: 'MB' },
  { type: 'Condenser', modeling: 'MB' },
  { type: 'PlateHX', modeling: 'FVM' },
  { type: 'Pipe', modeling: 'FVM' },
  { type: 'Pump', modeling: 'LUMPED' },
  { type: 'Compressor', modeling: 'LUMPED' },
  { type: 'ExpansionValve', modeling: 'LUMPED' },
  { type: 'HeatPort', modeling: 'LUMPED' },
  { type: 'Sensor', modeling: 'LUMPED' },
  { type: 'PID', modeling: 'LUMPED' },
];

export const NodePalette: React.FC = () => {
  const addNode = useSimulationStore((state) => state.addNode);

  const items = useMemo(() => componentLibrary, []);

  const handleAdd = (type: string, modeling: string) => {
    addNode({
      type,
      params: {
        modeling,
      },
      ports: [
        { name: 'in', direction: 'in', medium: 'refrigerant' },
        { name: 'out', direction: 'out', medium: 'refrigerant' },
      ],
      position: { x: Math.random() * 300 - 150, y: Math.random() * 300 - 150 },
    });
  };

  return (
    <div className="w-64 border-r border-slate-800 bg-slate-900/80 p-4 backdrop-blur">
      <h2 className="mb-4 text-lg font-semibold text-slate-100">Library</h2>
      <div className="space-y-2 overflow-y-auto">
        {items.map((item) => (
          <button
            key={item.type}
            className="flex w-full items-center justify-between rounded border border-slate-700 bg-slate-800 px-3 py-2 text-left text-sm hover:bg-slate-700"
            onClick={() => handleAdd(item.type, item.modeling)}
          >
            <span>{item.type}</span>
            <span className="rounded bg-slate-600 px-2 py-0.5 text-xs uppercase text-slate-100">{item.modeling}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
