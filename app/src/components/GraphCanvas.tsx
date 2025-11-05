import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSimulationStore } from '../state/simulationStore';
import { distance } from '../lib/math';
import { LiveProbe } from './LiveProbe';

interface TransformState {
  scale: number;
  offset: { x: number; y: number };
}

export const GraphCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [transform, setTransform] = useState<TransformState>({
    scale: 1,
    offset: { x: 0, y: 0 },
  });
  const [hoverEdge, setHoverEdge] = useState<string | null>(null);
  const [hoverNode, setHoverNode] = useState<string | null>(null);

  const { nodes, edges, select, selection, updateNode } = useSimulationStore((state) => ({
    nodes: state.nodes,
    edges: state.edges,
    select: state.select,
    selection: state.selection,
    updateNode: state.updateNode,
  }));

  const devicePixelRatio = typeof window !== 'undefined' ? window.devicePixelRatio : 1;

  const draw = useCallback(
    (ctx: CanvasRenderingContext2D) => {
      const { width, height } = ctx.canvas;
      ctx.save();
      ctx.scale(devicePixelRatio, devicePixelRatio);
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, width, height);

      ctx.translate(transform.offset.x, transform.offset.y);
      ctx.scale(transform.scale, transform.scale);

      // Draw grid
      ctx.save();
      const gridSpacing = 50;
      ctx.strokeStyle = 'rgba(148,163,184,0.1)';
      ctx.lineWidth = 1 / transform.scale;
      for (let x = -2000; x <= 2000; x += gridSpacing) {
        ctx.beginPath();
        ctx.moveTo(x, -2000);
        ctx.lineTo(x, 2000);
        ctx.stroke();
      }
      for (let y = -2000; y <= 2000; y += gridSpacing) {
        ctx.beginPath();
        ctx.moveTo(-2000, y);
        ctx.lineTo(2000, y);
        ctx.stroke();
      }
      ctx.restore();

      // Draw edges
      edges.forEach((edge) => {
        const from = nodes.find((node) => node.id === edge.from.id);
        const to = nodes.find((node) => node.id === edge.to.id);
        if (!from || !to) return;
        const start = {
          x: from.position.x + 80,
          y: from.position.y + 40,
        };
        const end = {
          x: to.position.x,
          y: to.position.y + 40,
        };
        const isHovered = hoverEdge === edge.id;
        ctx.beginPath();
        ctx.moveTo(start.x, start.y);
        const midX = (start.x + end.x) / 2;
        ctx.bezierCurveTo(midX, start.y, midX, end.y, end.x, end.y);
        ctx.strokeStyle = isHovered ? '#f97316' : '#38bdf8';
        ctx.lineWidth = isHovered ? 3 / transform.scale : 2 / transform.scale;
        ctx.stroke();
        // Arrow
        const angle = Math.atan2(end.y - start.y, end.x - start.x);
        const arrowLength = 10 / transform.scale;
        ctx.beginPath();
        ctx.moveTo(end.x, end.y);
        ctx.lineTo(end.x - arrowLength * Math.cos(angle - 0.3), end.y - arrowLength * Math.sin(angle - 0.3));
        ctx.lineTo(end.x - arrowLength * Math.cos(angle + 0.3), end.y - arrowLength * Math.sin(angle + 0.3));
        ctx.closePath();
        ctx.fillStyle = isHovered ? '#f97316' : '#38bdf8';
        ctx.fill();
      });

      // Draw nodes
      nodes.forEach((node) => {
        const isSelected = selection.includes(node.id);
        const width = 160;
        const height = 80;
        ctx.beginPath();
        if (typeof ctx.roundRect === 'function') {
          ctx.roundRect(node.position.x, node.position.y, width, height, 8 / transform.scale);
        } else {
          ctx.rect(node.position.x, node.position.y, width, height);
        }
        ctx.fillStyle = isSelected ? '#1f2937' : '#111827';
        ctx.fill();
        ctx.lineWidth = isSelected ? 3 / transform.scale : 2 / transform.scale;
        ctx.strokeStyle = hoverNode === node.id ? '#f97316' : '#3b82f6';
        ctx.stroke();
        ctx.fillStyle = '#e2e8f0';
        ctx.font = `${14 / transform.scale}px Inter, sans-serif`;
        ctx.fillText(node.type, node.position.x + 12, node.position.y + 24);
        ctx.font = `${11 / transform.scale}px Inter, sans-serif`;
        ctx.fillText(node.id, node.position.x + 12, node.position.y + 48);
      });
      ctx.restore();
    },
    [devicePixelRatio, edges, nodes, selection, transform, hoverEdge, hoverNode],
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    draw(ctx);
  }, [draw, nodes, edges, transform]);

  useEffect(() => {
    const resize = () => {
      const container = containerRef.current;
      const canvas = canvasRef.current;
      if (!container || !canvas) return;
      const rect = container.getBoundingClientRect();
      canvas.width = rect.width * devicePixelRatio;
      canvas.height = rect.height * devicePixelRatio;
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        draw(ctx);
      }
    };
    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, [draw, devicePixelRatio]);

  const screenToWorld = useCallback(
    (point: { x: number; y: number }) => {
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return point;
      const x = (point.x - rect.left - transform.offset.x) / transform.scale;
      const y = (point.y - rect.top - transform.offset.y) / transform.scale;
      return { x, y };
    },
    [transform],
  );

  const onWheel = useCallback(
    (event: React.WheelEvent<HTMLCanvasElement>) => {
      event.preventDefault();
      const { deltaY } = event;
      setTransform((prev) => {
        const scale = deltaY < 0 ? prev.scale * 1.1 : prev.scale / 1.1;
        const clamped = Math.min(3, Math.max(0.2, scale));
        return { ...prev, scale: clamped };
      });
    },
    [],
  );

  const dragInfo = useRef<{ id: string; offset: { x: number; y: number } } | null>(null);
  const panning = useRef<boolean>(false);
  const lastPointer = useRef<{ x: number; y: number } | null>(null);

  const handlePointerDown = useCallback(
    (event: React.PointerEvent<HTMLCanvasElement>) => {
      const world = screenToWorld({ x: event.clientX, y: event.clientY });
      const node = nodes.find((n) => {
        return world.x >= n.position.x &&
          world.x <= n.position.x + 160 &&
          world.y >= n.position.y &&
          world.y <= n.position.y + 80;
      });
      if (node) {
        dragInfo.current = {
          id: node.id,
          offset: {
            x: world.x - node.position.x,
            y: world.y - node.position.y,
          },
        };
        select([node.id]);
      } else {
        panning.current = true;
        select([]);
      }
      lastPointer.current = { x: event.clientX, y: event.clientY };
    },
    [nodes, screenToWorld, select],
  );

  const handlePointerMove = useCallback(
    (event: React.PointerEvent<HTMLCanvasElement>) => {
      const pointer = { x: event.clientX, y: event.clientY };
      const world = screenToWorld(pointer);
      const hoveredNode = nodes.find((n) =>
        world.x >= n.position.x &&
        world.x <= n.position.x + 160 &&
        world.y >= n.position.y &&
        world.y <= n.position.y + 80,
      );
      setHoverNode(hoveredNode?.id ?? null);
      const hoveredEdge = edges.find((edge) => {
        const from = nodes.find((n) => n.id === edge.from.id);
        const to = nodes.find((n) => n.id === edge.to.id);
        if (!from || !to) return false;
        const start = {
          x: from.position.x + 80,
          y: from.position.y + 40,
        };
        const end = {
          x: to.position.x,
          y: to.position.y + 40,
        };
        const d =
          Math.abs((end.y - start.y) * world.x - (end.x - start.x) * world.y + end.x * start.y - end.y * start.x) /
          distance(start, end);
        return d < 8;
      });
      setHoverEdge(hoveredEdge?.id ?? null);

      if (dragInfo.current) {
        updateNode(dragInfo.current.id, (node) => {
          node.position.x = world.x - dragInfo.current!.offset.x;
          node.position.y = world.y - dragInfo.current!.offset.y;
        });
      } else if (panning.current && lastPointer.current) {
        const dx = pointer.x - lastPointer.current.x;
        const dy = pointer.y - lastPointer.current.y;
        setTransform((prev) => ({
          ...prev,
          offset: {
            x: prev.offset.x + dx,
            y: prev.offset.y + dy,
          },
        }));
      }
      lastPointer.current = pointer;
    },
    [edges, nodes, screenToWorld, updateNode],
  );

  const handlePointerUp = useCallback(() => {
    dragInfo.current = null;
    panning.current = false;
  }, []);

  const activeProbe = useMemo(() => {
    if (hoverNode) {
      return { type: 'node', id: hoverNode } as const;
    }
    if (hoverEdge) {
      return { type: 'edge', id: hoverEdge } as const;
    }
    return null;
  }, [hoverEdge, hoverNode]);

  return (
    <div ref={containerRef} className="relative flex-1">
      <canvas
        ref={canvasRef}
        className="h-full w-full cursor-crosshair"
        onWheel={onWheel}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
      />
      <LiveProbe probe={activeProbe} />
    </div>
  );
};
