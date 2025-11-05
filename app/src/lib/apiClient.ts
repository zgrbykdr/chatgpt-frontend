import type { ProjectGraph } from './schemas';

type RunRequest = {
  mode: 'continuous' | 'step';
  step?: number;
};

class ApiClient {
  private baseUrl = 'http://127.0.0.1:8000';

  async loadGraph(graph: ProjectGraph) {
    const response = await fetch(`${this.baseUrl}/sim/load`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(graph),
    });
    if (!response.ok) {
      throw new Error('Failed to load graph');
    }
    return response.json();
  }

  async runSimulation(payload: RunRequest) {
    const response = await fetch(`${this.baseUrl}/sim/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error('Failed to start simulation');
    }
    return response.json();
  }

  async pauseSimulation() {
    await fetch(`${this.baseUrl}/sim/pause`, { method: 'POST' });
  }

  async resetSimulation() {
    await fetch(`${this.baseUrl}/sim/reset`, { method: 'POST' });
  }

  async getFluids(): Promise<string[]> {
    const response = await fetch(`${this.baseUrl}/props/list_fluids`);
    if (!response.ok) {
      return [];
    }
    return response.json();
  }
}

export const apiClient = new ApiClient();
