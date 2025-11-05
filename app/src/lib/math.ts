export const clamp = (value: number, min: number, max: number) => {
  return Math.min(max, Math.max(min, value));
};

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const smoothLimit = (value: number, min: number, max: number, softness = 1e-3) => {
  const range = max - min;
  const normalized = (value - min) / range;
  const limited = 1 / (1 + Math.exp(-softness * (normalized - 0.5)));
  return min + limited * range;
};

export const magnitude = (x: number, y: number) => Math.sqrt(x * x + y * y);

export const distance = (a: { x: number; y: number }, b: { x: number; y: number }) => {
  return magnitude(a.x - b.x, a.y - b.y);
};
