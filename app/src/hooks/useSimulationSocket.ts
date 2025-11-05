import { useEffect, useRef } from 'react';
import { useSimulationStore } from '../state/simulationStore';

interface SimulationMessage {
  type: 'state' | 'validation';
  payload: any;
}

export const useSimulationSocket = () => {
  const setValidation = useSimulationStore((state) => state.setValidation);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const socket = new WebSocket('ws://127.0.0.1:8000/ws/sim');
    socketRef.current = socket;
    socket.onmessage = (event) => {
      const message: SimulationMessage = JSON.parse(event.data);
      if (message.type === 'validation') {
        setValidation(message.payload);
      }
    };
    socket.onclose = () => {
      socketRef.current = null;
    };
    return () => {
      socket.close();
    };
  }, [setValidation]);

  return socketRef;
};
