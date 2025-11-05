import { JSONSchemaType } from 'ajv';

export interface GraphPort {
  name: string;
  direction: 'in' | 'out';
  medium: 'refrigerant' | 'liquid' | 'heat' | 'signal' | 'power';
}

export interface GraphNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  params: Record<string, any> & { modeling?: 'MB' | 'FVM' | 'LUMPED' };
  ports: GraphPort[];
}

export interface GraphEdge {
  id: string;
  from: { id: string; port: string };
  to: { id: string; port: string };
  type: 'fluid' | 'heat' | 'signal' | 'power';
}

export interface SimulationConfig {
  start: number;
  stop: number;
  integrator: 'BDF2' | 'TRAP';
  scenario: string | null;
  tolerances: {
    absolute: number;
    relative: number;
  };
}

export interface ValidationSummary {
  energyResidual: number;
  jacobianCondition: number;
  warnings: string[];
}

export interface ProjectGraph {
  version: string;
  fluids: Array<{ name: string; role: 'primary' | 'secondary'; options?: Record<string, any> } | string>;
  components: Array<
    {
      id: string;
      type: string;
      modeling: 'MB' | 'FVM' | 'LUMPED';
      params: Record<string, any>;
      ports: GraphPort[];
      ui?: { position?: { x: number; y: number } };
    }
  >;
  connections: GraphEdge[];
  simulation: SimulationConfig;
  metadata?: {
    validation?: ValidationSummary;
    generatedAt?: string;
  };
  units: {
    temperature: 'C' | 'K';
    pressure: 'Pa' | 'bar';
    massFlow: 'kg/s' | 'g/s';
  };
}

export const graphSchema: JSONSchemaType<ProjectGraph> = {
  $id: 'https://heatpump-sim.io/schemas/project.json',
  type: 'object',
  required: ['version', 'fluids', 'components', 'connections', 'simulation', 'units'],
  properties: {
    version: { type: 'string' },
    fluids: {
      type: 'array',
      items: {
        anyOf: [
          { type: 'string' },
          {
            type: 'object',
            required: ['name', 'role'],
            properties: {
              name: { type: 'string' },
              role: { type: 'string', enum: ['primary', 'secondary'] },
              options: {
                type: 'object',
                nullable: true,
                additionalProperties: true,
              },
            },
            additionalProperties: false,
          },
        ],
      },
      minItems: 1,
    },
    components: {
      type: 'array',
      minItems: 1,
      items: {
        type: 'object',
        required: ['id', 'type', 'modeling', 'params', 'ports'],
        properties: {
          id: { type: 'string' },
          type: { type: 'string' },
          modeling: { type: 'string', enum: ['MB', 'FVM', 'LUMPED'] },
          params: { type: 'object', additionalProperties: true },
          ports: {
            type: 'array',
            items: {
              type: 'object',
              required: ['name', 'direction', 'medium'],
              properties: {
                name: { type: 'string' },
                direction: { type: 'string', enum: ['in', 'out'] },
                medium: { type: 'string', enum: ['refrigerant', 'liquid', 'heat', 'signal', 'power'] },
              },
              additionalProperties: false,
            },
          },
          ui: {
            type: 'object',
            nullable: true,
            properties: {
              position: {
                type: 'object',
                nullable: true,
                required: ['x', 'y'],
                properties: {
                  x: { type: 'number' },
                  y: { type: 'number' },
                },
                additionalProperties: false,
              },
            },
            additionalProperties: false,
          },
        },
        additionalProperties: false,
      },
    },
    connections: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'from', 'to', 'type'],
        properties: {
          id: { type: 'string' },
          from: {
            type: 'object',
            required: ['id', 'port'],
            properties: {
              id: { type: 'string' },
              port: { type: 'string' },
            },
            additionalProperties: false,
          },
          to: {
            type: 'object',
            required: ['id', 'port'],
            properties: {
              id: { type: 'string' },
              port: { type: 'string' },
            },
            additionalProperties: false,
          },
          type: { type: 'string', enum: ['fluid', 'heat', 'signal', 'power'] },
        },
        additionalProperties: false,
      },
    },
    simulation: {
      type: 'object',
      required: ['start', 'stop', 'integrator', 'scenario', 'tolerances'],
      properties: {
        start: { type: 'number' },
        stop: { type: 'number' },
        integrator: { type: 'string', enum: ['BDF2', 'TRAP'] },
        scenario: { type: 'string', nullable: true },
        tolerances: {
          type: 'object',
          required: ['absolute', 'relative'],
          properties: {
            absolute: { type: 'number' },
            relative: { type: 'number' },
          },
          additionalProperties: false,
        },
      },
      additionalProperties: false,
    },
    metadata: {
      type: 'object',
      nullable: true,
      properties: {
        validation: {
          type: 'object',
          nullable: true,
          required: ['energyResidual', 'jacobianCondition', 'warnings'],
          properties: {
            energyResidual: { type: 'number' },
            jacobianCondition: { type: 'number' },
            warnings: { type: 'array', items: { type: 'string' } },
          },
          additionalProperties: false,
        },
        generatedAt: { type: 'string', nullable: true },
      },
      additionalProperties: false,
    },
    units: {
      type: 'object',
      required: ['temperature', 'pressure', 'massFlow'],
      properties: {
        temperature: { type: 'string', enum: ['C', 'K'] },
        pressure: { type: 'string', enum: ['Pa', 'bar'] },
        massFlow: { type: 'string', enum: ['kg/s', 'g/s'] },
      },
      additionalProperties: false,
    },
  },
  additionalProperties: false,
};
