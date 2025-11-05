import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RunControls } from '../components/RunControls';
import { apiClient } from '../lib/apiClient';
import { resetStore } from './utils';

jest.mock('../lib/apiClient');
const mockedClient = apiClient as jest.Mocked<typeof apiClient>;

beforeEach(() => {
  resetStore();
  mockedClient.getFluids.mockResolvedValue(['R134a']);
  mockedClient.loadGraph.mockResolvedValue({ status: 'ok' });
  mockedClient.runSimulation.mockResolvedValue({ status: 'started' });
  mockedClient.pauseSimulation.mockResolvedValue({ status: 'paused' });
  mockedClient.resetSimulation.mockResolvedValue({ status: 'reset' });
});

test('run button triggers load and run', async () => {
  render(<RunControls />);
  fireEvent.click(screen.getByText('Run'));
  await waitFor(() => expect(mockedClient.loadGraph).toHaveBeenCalled());
  expect(mockedClient.runSimulation).toHaveBeenCalled();
});

test('pause button disables when not running', () => {
  render(<RunControls />);
  expect(screen.getByText('Pause')).toBeDisabled();
});

test('scenario button toggles', () => {
  render(<RunControls />);
  const btn = screen.getByText('Load EN14511');
  fireEvent.click(btn);
  expect(btn.textContent).toContain('Scenario');
});
