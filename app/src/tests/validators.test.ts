import { validateProject, ValidationError } from '../lib/validators';
import type { ProjectGraph } from '../lib/schemas';

const project: ProjectGraph = {
  version: '1.0.0',
  fluids: ['Water'],
  components: [
    {
      id: 'comp',
      type: 'Compressor',
      modeling: 'LUMPED',
      params: {},
      ports: [
        { name: 'in', direction: 'in', medium: 'refrigerant' },
        { name: 'out', direction: 'out', medium: 'refrigerant' },
      ],
      ui: { position: { x: 0, y: 0 } },
    },
  ],
  connections: [],
  simulation: { start: 0, stop: 10, integrator: 'BDF2', scenario: null, tolerances: { absolute: 1e-5, relative: 1e-4 } },
  units: { temperature: 'C', pressure: 'bar', massFlow: 'kg/s' },
};

test('validateProject accepts valid graph', () => {
  expect(() => validateProject(project)).not.toThrow();
});

test('validateProject rejects missing component', () => {
  const invalid = { ...project, components: [] } as unknown as ProjectGraph;
  expect(() => validateProject(invalid)).toThrow(ValidationError);
});
