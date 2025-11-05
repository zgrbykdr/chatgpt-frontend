import create from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { nanoid } from 'nanoid';
import { clamp } from '../lib/math';
import { validateProject } from '../lib/validators';
import type { ProjectGraph, GraphNode, GraphEdge, ValidationSummary } from '../lib/schemas';

export interface SimulationState {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selection: string[];
  validation: ValidationSummary;
  activeScenario: string | null;
  graphVersion: number;
  addNode: (node: Omit<GraphNode, 'id'> & { id?: string }) => string;
  updateNode: (id: string, updater: (node: GraphNode) => void) => void;
  removeNode: (id: string) => void;
  addEdge: (edge: GraphEdge) => void;
  removeEdge: (id: string) => void;
  select: (ids: string[]) => void;
  loadProject: (project: ProjectGraph) => void;
  exportProject: () => ProjectGraph;
  setValidation: (summary: ValidationSummary) => void;
  toggleScenario: (scenario: string | null) => void;
}

const defaultValidation: ValidationSummary = {
  energyResidual: 0,
  jacobianCondition: 1,
  warnings: [],
};

export const useSimulationStore = create<SimulationState>()(
  immer((set, get) => ({
    nodes: [],
    edges: [],
    selection: [],
    validation: defaultValidation,
    activeScenario: null,
    graphVersion: 0,
    addNode: (node) => {
      const id = node.id ?? nanoid();
      set((state) => {
        state.nodes.push({ ...node, id });
        state.graphVersion += 1;
      });
      return id;
    },
    updateNode: (id, updater) => {
      set((state) => {
        const target = state.nodes.find((n) => n.id === id);
        if (target) {
          updater(target);
          state.graphVersion += 1;
        }
      });
    },
    removeNode: (id) => {
      set((state) => {
        state.nodes = state.nodes.filter((n) => n.id !== id);
        state.edges = state.edges.filter((e) => e.from.id !== id && e.to.id !== id);
        state.selection = state.selection.filter((sid) => sid !== id);
        state.graphVersion += 1;
      });
    },
    addEdge: (edge) => {
      set((state) => {
        state.edges.push(edge);
        state.graphVersion += 1;
      });
    },
    removeEdge: (id) => {
      set((state) => {
        state.edges = state.edges.filter((e) => e.id !== id);
        state.graphVersion += 1;
      });
    },
    select: (ids) => {
      set((state) => {
        state.selection = ids;
      });
    },
    loadProject: (project) => {
      validateProject(project);
      set(() => ({
        nodes: project.components.map((component) => ({
          id: component.id,
          type: component.type,
          position: component.ui?.position ?? { x: 0, y: 0 },
          params: component.params,
          ports: component.ports,
        })),
        edges: project.connections.map((connection) => ({
          id: connection.id ?? nanoid(),
          from: connection.from,
          to: connection.to,
          type: connection.type,
        })),
        validation: project.metadata?.validation ?? defaultValidation,
        activeScenario: project.simulation.scenario ?? null,
        selection: [],
        graphVersion: Date.now(),
      }));
    },
    exportProject: () => {
      const state = get();
      const project: ProjectGraph = {
        version: '1.0.0',
        fluids: state.nodes
          .filter((node) => node.type === 'fluid')
          .map((node) => node.params.fluid),
        components: state.nodes.map((node) => ({
          id: node.id,
          type: node.type,
          modeling: node.params.modeling ?? 'MB',
          params: node.params,
          ports: node.ports,
          ui: {
            position: node.position,
          },
        })),
        connections: state.edges,
        simulation: {
          start: 0,
          stop: 100,
          integrator: 'BDF2',
          scenario: state.activeScenario,
          tolerances: {
            absolute: 1e-5,
            relative: 1e-4,
          },
        },
        metadata: {
          validation: state.validation,
          generatedAt: new Date().toISOString(),
        },
        units: {
          temperature: 'C',
          pressure: 'bar',
          massFlow: 'kg/s',
        },
      };
      validateProject(project);
      return project;
    },
    setValidation: (summary) => {
      set(() => ({ validation: summary }));
    },
    toggleScenario: (scenario) => {
      set(() => ({ activeScenario: scenario }));
    },
  })),
);

export const createPort = (name: string, direction: 'in' | 'out', medium: string) => ({
  name,
  direction,
  medium,
});

export const clampQuality = (value: number) => clamp(value, 0, 1);
