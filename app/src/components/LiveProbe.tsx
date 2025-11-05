import React from 'react';
import { useSimulationStore } from '../state/simulationStore';

interface ProbeProps {
  probe: { type: 'node' | 'edge'; id: string } | null;
}

export const LiveProbe: React.FC<ProbeProps> = ({ probe }) => {
  const { nodes, edges } = useSimulationStore((state) => ({
    nodes: state.nodes,
    edges: state.edges,
  }));

  if (!probe) return null;

  const payload = probe.type === 'node' ? nodes.find((node) => node.id === probe.id) : edges.find((edge) => edge.id === probe.id);
  if (!payload) return null;

  const stats = probe.type === 'node'
    ? {
        pressure: payload.params.pressure ?? 6,
        temperature: payload.params.temperature ?? 5,
        quality: payload.params.quality ?? 0,
        massFlow: payload.params.massFlow ?? 0.1,
        heatDuty: payload.params.heatDuty ?? 0,
      }
    : {
        pressure: 5,
        temperature: 7,
        quality: 0.2,
        massFlow: 0.1,
        heatDuty: 2.5,
      };

  return (
    <div className="pointer-events-none absolute right-4 top-4 w-56 rounded-lg border border-slate-700 bg-slate-900/80 p-3 text-xs text-slate-100 shadow-lg">
      <p className="text-sm font-semibold text-slate-100">Live Probe</p>
      <p className="text-slate-400">Target: {probe.type === 'node' ? 'Node' : 'Edge'} {probe.id}</p>
      <div className="mt-2 space-y-1">
        <div className="flex justify-between">
          <span>p</span>
          <span>{stats.pressure.toFixed(2)} bar</span>
        </div>
        <div className="flex justify-between">
          <span>T</span>
          <span>{stats.temperature.toFixed(2)} °C</span>
        </div>
        <div className="flex justify-between">
          <span>x</span>
          <span>{stats.quality.toFixed(3)}</span>
        </div>
        <div className="flex justify-between">
          <span>ṁ</span>
          <span>{stats.massFlow.toFixed(3)} kg/s</span>
        </div>
        <div className="flex justify-between">
          <span>Q̇</span>
          <span>{stats.heatDuty.toFixed(2)} kW</span>
        </div>
      </div>
    </div>
  );
};
