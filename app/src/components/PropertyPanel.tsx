import React, { useMemo } from 'react';
import { useSimulationStore } from '../state/simulationStore';

const tabs = ['Geometry', 'Thermo', 'Correlations', 'Controls', 'Initial Conditions', 'Limits'] as const;

type Tab = typeof tabs[number];

export const PropertyPanel: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<Tab>('Geometry');
  const { nodes, selection, updateNode } = useSimulationStore((state) => ({
    nodes: state.nodes,
    selection: state.selection,
    updateNode: state.updateNode,
  }));

  const selectedNode = useMemo(() => nodes.find((node) => selection.includes(node.id)), [nodes, selection]);

  const handleChange = (key: string, value: string | number) => {
    if (!selectedNode) return;
    updateNode(selectedNode.id, (node) => {
      node.params[key] = value;
    });
  };

  return (
    <div className="w-80 border-l border-slate-800 bg-slate-900/70 p-4 backdrop-blur">
      <h2 className="text-lg font-semibold text-slate-100">Properties</h2>
      {selectedNode ? (
        <div className="mt-3 space-y-4">
          <div>
            <p className="text-sm text-slate-400">Component</p>
            <p className="text-base font-medium text-slate-100">{selectedNode.type}</p>
            <p className="text-xs text-slate-500">{selectedNode.id}</p>
          </div>
          <div className="flex space-x-2 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab}
                className={`rounded px-3 py-1 text-xs ${activeTab === tab ? 'bg-slate-500 text-white' : 'bg-slate-800 text-slate-300'}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>
          <div className="space-y-2 text-sm">
            {Object.entries(selectedNode.params).map(([key, value]) => (
              <label key={key} className="block">
                <span className="text-xs uppercase text-slate-400">{key}</span>
                <input
                  className="mt-1 w-full rounded border border-slate-700 bg-slate-800 px-2 py-1 text-slate-100 focus:border-slate-500 focus:outline-none"
                  value={value}
                  onChange={(event) => handleChange(key, event.target.value)}
                />
              </label>
            ))}
          </div>
        </div>
      ) : (
        <p className="mt-4 text-sm text-slate-500">Select a component to edit its parameters.</p>
      )}
    </div>
  );
};
