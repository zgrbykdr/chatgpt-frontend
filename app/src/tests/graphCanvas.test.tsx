import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { GraphCanvas } from '../components/GraphCanvas';
import { useSimulationStore } from '../state/simulationStore';
import { resetStore } from './utils';

beforeAll(() => {
  HTMLCanvasElement.prototype.getContext = jest.fn(() => ({
    canvas: { width: 1000, height: 600 },
    save: jest.fn(),
    restore: jest.fn(),
    scale: jest.fn(),
    clearRect: jest.fn(),
    fillRect: jest.fn(),
    translate: jest.fn(),
    beginPath: jest.fn(),
    moveTo: jest.fn(),
    lineTo: jest.fn(),
    bezierCurveTo: jest.fn(),
    stroke: jest.fn(),
    fill: jest.fn(),
    closePath: jest.fn(),
    strokeStyle: '',
    fillStyle: '',
    font: '',
    lineWidth: 1,
    roundRect: jest.fn(),
    fillText: jest.fn(),
  } as unknown as CanvasRenderingContext2D);
  Object.defineProperty(HTMLCanvasElement.prototype, 'getBoundingClientRect', {
    value: () => ({ left: 0, top: 0, width: 800, height: 600 }),
  });
});

beforeEach(() => {
  resetStore();
  const addNode = useSimulationStore.getState().addNode;
  addNode({
    type: 'Evaporator',
    params: { modeling: 'MB' },
    ports: [],
    position: { x: 0, y: 0 },
  });
});

test('graph canvas renders without crashing', () => {
  const { container } = render(<GraphCanvas />);
  expect(container.querySelector('canvas')).toBeInTheDocument();
});

test('graph canvas updates selection on click', () => {
  const { container } = render(<GraphCanvas />);
  const canvas = container.querySelector('canvas');
  if (!canvas) throw new Error('canvas missing');
  fireEvent.pointerDown(canvas, { clientX: 10, clientY: 10 });
  fireEvent.pointerUp(canvas, { clientX: 10, clientY: 10 });
  expect(useSimulationStore.getState().selection).toHaveLength(1);
});
