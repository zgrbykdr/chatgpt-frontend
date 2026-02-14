from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image


class LayerType(str, Enum):
    HEIGHTMAP = "heightmap"
    BIOME = "biome"
    RIVERS = "rivers"
    LIGHTING = "lighting"
    POLITICAL = "political"
    WEATHER = "weather"


@dataclass
class MapLayer:
    name: str
    layer_type: LayerType
    opacity: float = 1.0
    visible: bool = True
    blend_mode: str = "normal"
    data: np.ndarray | None = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class MapProject:
    width: int
    height: int
    layers: List[MapLayer] = field(default_factory=list)
    lore_index: Dict[str, Dict[str, str]] = field(default_factory=dict)


class MapEngine:
    """
    Hybrid vector/raster generation backend tailored for large fantasy map workflows.
    - Resolution scales to 16K+ through tiled arrays.
    - Core systems include tectonics, erosion, rivers, and climate-driven biome synthesis.
    """

    TERRAIN_PRESET_COUNT = 512

    def __init__(self, seed: int = 42) -> None:
        self.rng = np.random.default_rng(seed)
        self.palette = self._build_palette(self.TERRAIN_PRESET_COUNT)

    def create_project(self, width: int = 4096, height: int = 4096) -> MapProject:
        project = MapProject(width=width, height=height)
        project.layers.extend(
            [
                MapLayer("Heightmap", LayerType.HEIGHTMAP),
                MapLayer("Biome", LayerType.BIOME),
                MapLayer("Rivers", LayerType.RIVERS, opacity=0.85),
                MapLayer("Lighting", LayerType.LIGHTING, opacity=0.7),
                MapLayer("Political", LayerType.POLITICAL, opacity=0.6),
                MapLayer("Weather", LayerType.WEATHER, opacity=0.5),
            ]
        )
        return project

    def generate_tectonic_heightmap(
        self,
        width: int,
        height: int,
        plates: int = 18,
        roughness: float = 1.4,
    ) -> np.ndarray:
        y, x = np.indices((height, width))
        field = np.zeros((height, width), dtype=np.float32)

        for _ in range(plates):
            cx = self.rng.integers(0, width)
            cy = self.rng.integers(0, height)
            amp = self.rng.uniform(0.2, 1.0)
            sigma = self.rng.uniform(width * 0.05, width * 0.22)
            field += amp * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sigma**2))

        field += self._fractal_noise(width, height, octaves=7, persistence=0.55) * roughness
        field = (field - field.min()) / (field.max() - field.min() + 1e-8)
        return field

    def erode(self, heightmap: np.ndarray, iterations: int = 45, talus: float = 0.02) -> np.ndarray:
        hm = heightmap.copy()
        for _ in range(iterations):
            north = np.roll(hm, -1, axis=0)
            south = np.roll(hm, 1, axis=0)
            east = np.roll(hm, -1, axis=1)
            west = np.roll(hm, 1, axis=1)

            diffs = np.stack([hm - north, hm - south, hm - east, hm - west])
            transport = np.maximum(diffs - talus, 0) * 0.08
            hm -= transport.sum(axis=0)
            hm += np.roll(transport[0], 1, axis=0)
            hm += np.roll(transport[1], -1, axis=0)
            hm += np.roll(transport[2], 1, axis=1)
            hm += np.roll(transport[3], -1, axis=1)

            rain = self.rng.normal(0.0015, 0.0003, hm.shape)
            hm -= np.clip(rain, 0, None) * np.clip(1 - hm, 0, 1)
            hm = np.clip(hm, 0, 1)
        return hm

    def generate_climate(self, heightmap: np.ndarray) -> Dict[str, np.ndarray]:
        h, w = heightmap.shape
        lat = np.linspace(-1, 1, h).reshape(-1, 1)
        temperature = (1 - np.abs(lat)) * (1 - 0.45 * heightmap)
        wind = np.sin(np.linspace(0, np.pi * 6, w))[None, :] * (0.5 + 0.5 * (1 - np.abs(lat)))
        humidity = np.clip((1 - heightmap) * 0.65 + np.abs(wind) * 0.35, 0, 1)
        return {
            "temperature": temperature,
            "wind": wind,
            "humidity": humidity,
        }

    def generate_rivers(self, heightmap: np.ndarray, count: int = 120) -> np.ndarray:
        h, w = heightmap.shape
        rivers = np.zeros_like(heightmap)

        peaks = np.argwhere(heightmap > np.quantile(heightmap, 0.82))
        if len(peaks) == 0:
            return rivers

        for _ in range(min(count, len(peaks))):
            y, x = peaks[self.rng.integers(0, len(peaks))]
            for _ in range(1200):
                rivers[y, x] = 1
                neighbors = [
                    ((y - 1) % h, x),
                    ((y + 1) % h, x),
                    (y, (x - 1) % w),
                    (y, (x + 1) % w),
                ]
                slopes = [heightmap[y, x] - heightmap[ny, nx] for ny, nx in neighbors]
                idx = int(np.argmax(slopes))
                if slopes[idx] <= 0:
                    break
                y, x = neighbors[idx]
                if heightmap[y, x] < 0.22:
                    break
        return rivers

    def biome_map(self, heightmap: np.ndarray, climate: Dict[str, np.ndarray]) -> np.ndarray:
        temp = climate["temperature"]
        hum = climate["humidity"]
        biome = np.zeros((*heightmap.shape, 3), dtype=np.uint8)

        ocean = heightmap < 0.22
        coast = (heightmap >= 0.22) & (heightmap < 0.28)
        desert = (heightmap > 0.28) & (temp > 0.68) & (hum < 0.38)
        forest = (heightmap > 0.28) & (hum > 0.62) & (temp > 0.35)
        tundra = (temp < 0.26) & (heightmap > 0.28)
        mountain = heightmap > 0.75
        swamp = (heightmap > 0.28) & (heightmap < 0.42) & (hum > 0.72)
        volcanic = mountain & (temp > 0.6) & (hum < 0.4)

        biome[ocean] = (16, 48, 120)
        biome[coast] = (210, 200, 150)
        biome[desert] = (208, 176, 94)
        biome[forest] = (42, 108, 53)
        biome[tundra] = (214, 230, 235)
        biome[mountain] = (110, 104, 106)
        biome[swamp] = (58, 87, 60)
        biome[volcanic] = (71, 36, 30)

        untouched = np.where((biome == 0).all(axis=2))
        biome[untouched] = (126, 170, 95)
        return biome

    def render_composite(self, biome: np.ndarray, rivers: np.ndarray, lighting_strength: float = 0.4) -> np.ndarray:
        image = biome.astype(np.float32)
        river_mask = rivers > 0
        image[river_mask] = image[river_mask] * 0.25 + np.array([70, 130, 200]) * 0.75

        shade = self._hillshade_from_rgb(image)
        image *= (1 - lighting_strength) + shade[..., None] * lighting_strength
        return np.clip(image, 0, 255).astype(np.uint8)

    def export_png(self, image: np.ndarray, path: str | Path) -> None:
        Image.fromarray(image).save(path)

    def export_heightmap(self, heightmap: np.ndarray, path: str | Path) -> None:
        gray = np.clip(heightmap * 65535, 0, 65535).astype(np.uint16)
        Image.fromarray(gray, mode="I;16").save(path)

    def _fractal_noise(self, width: int, height: int, octaves: int = 6, persistence: float = 0.5) -> np.ndarray:
        noise = np.zeros((height, width), dtype=np.float32)
        frequency = 1.0
        amplitude = 1.0
        total_amp = 0.0
        for _ in range(octaves):
            phase_x = self.rng.uniform(0, 2 * np.pi)
            phase_y = self.rng.uniform(0, 2 * np.pi)
            xs = np.linspace(0, frequency * 2 * np.pi, width)
            ys = np.linspace(0, frequency * 2 * np.pi, height)
            grid = np.outer(np.sin(ys + phase_y), np.cos(xs + phase_x))
            noise += grid * amplitude
            total_amp += amplitude
            frequency *= 2.0
            amplitude *= persistence
        return noise / max(total_amp, 1e-8)

    def _build_palette(self, n: int) -> List[Tuple[int, int, int]]:
        colors: List[Tuple[int, int, int]] = []
        for i in range(n):
            t = i / max(1, n - 1)
            r = int(20 + 200 * np.clip(np.sin(t * np.pi * 1.3) ** 2, 0, 1))
            g = int(30 + 180 * np.clip(np.sin(t * np.pi * 1.9 + 0.5) ** 2, 0, 1))
            b = int(25 + 180 * np.clip(np.sin(t * np.pi * 2.3 + 1.1) ** 2, 0, 1))
            colors.append((r, g, b))
        return colors

    def _hillshade_from_rgb(self, image: np.ndarray) -> np.ndarray:
        gray = (0.21 * image[..., 0] + 0.72 * image[..., 1] + 0.07 * image[..., 2]) / 255.0
        gx = np.gradient(gray, axis=1)
        gy = np.gradient(gray, axis=0)
        slope = np.pi / 2 - np.arctan(np.sqrt(gx * gx + gy * gy))
        aspect = np.arctan2(-gx, gy)
        azimuth = np.deg2rad(315)
        altitude = np.deg2rad(45)
        shade = np.sin(altitude) * np.sin(slope) + np.cos(altitude) * np.cos(slope) * np.cos(azimuth - aspect)
        return np.clip((shade + 1) / 2, 0, 1)
