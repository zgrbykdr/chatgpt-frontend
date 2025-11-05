import React from 'react';
import { useSimulationStore } from '../state/simulationStore';

export const InspectorOverlay: React.FC = () => {
  const { nodes, edges } = useSimulationStore((state) => ({
    nodes: state.nodes,
    edges: state.edges,
  }));

  return (
    <div className="pointer-events-auto absolute right-4 bottom-4 w-80 rounded-lg border border-slate-700 bg-slate-900/75 p-3 text-xs text-slate-200 shadow">
      <p className="text-sm font-semibold text-slate-100">Inspector</p>
      <div className="mt-2 max-h-48 space-y-2 overflow-y-auto">
        <div>
          <p className="text-[11px] uppercase tracking-wide text-slate-400">Nodes</p>
          <ul className="space-y-1">
            {nodes.map((node) => (
              <li key={node.id} className="flex justify-between text-[11px]">
                <span>{node.type}</span>
                <span>
                  ({node.position.x.toFixed(1)}, {node.position.y.toFixed(1)})
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-wide text-slate-400">Edges</p>
          <ul className="space-y-1">
            {edges.map((edge) => (
              <li key={edge.id} className="flex justify-between text-[11px]">
                <span>
                  {edge.from.id}:{edge.from.port}
                </span>
                <span>
                  → {edge.to.id}:{edge.to.port}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
