from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional
import json
from jsonschema import Draft202012Validator


@dataclass
class Port:
  name: str
  direction: Literal['in', 'out']
  medium: Literal['refrigerant', 'liquid', 'heat', 'signal', 'power']


@dataclass
class Component:
  id: str
  type: str
  modeling: Literal['MB', 'FVM', 'LUMPED']
  params: Dict[str, Any]
  ports: List[Port]
  ui: Optional[Dict[str, Any]] = None


@dataclass
class ConnectionEnd:
  id: str
  port: str


@dataclass
class Connection:
  id: str
  from_: ConnectionEnd
  to: ConnectionEnd
  type: Literal['fluid', 'heat', 'signal', 'power']


@dataclass
class SimulationConfig:
  start: float
  stop: float
  integrator: Literal['BDF2', 'TRAP']
  scenario: Optional[str]
  tolerances: Dict[str, float]


@dataclass
class Units:
  temperature: Literal['C', 'K']
  pressure: Literal['Pa', 'bar']
  massFlow: Literal['kg/s', 'g/s']


@dataclass
class ProjectGraph:
  version: str
  fluids: List[Any]
  components: List[Component]
  connections: List[Connection]
  simulation: SimulationConfig
  units: Units
  metadata: Optional[Dict[str, Any]] = None


PROJECT_SCHEMA: Dict[str, Any] = json.loads(
  """
  {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://heatpump-sim.io/schemas/project.json",
    "type": "object",
    "required": ["version", "fluids", "components", "connections", "simulation", "units"],
    "properties": {
      "version": { "type": "string" },
      "fluids": {
        "type": "array",
        "minItems": 1,
        "items": {
          "anyOf": [
            { "type": "string" },
            {
              "type": "object",
              "required": ["name", "role"],
              "properties": {
                "name": { "type": "string" },
                "role": { "type": "string", "enum": ["primary", "secondary"] },
                "options": { "type": "object", "nullable": true, "additionalProperties": true }
              },
              "additionalProperties": false
            }
          ]
        }
      },
      "components": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": ["id", "type", "modeling", "params", "ports"],
          "properties": {
            "id": { "type": "string" },
            "type": { "type": "string" },
            "modeling": { "type": "string", "enum": ["MB", "FVM", "LUMPED"] },
            "params": { "type": "object", "additionalProperties": true },
            "ports": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["name", "direction", "medium"],
                "properties": {
                  "name": { "type": "string" },
                  "direction": { "type": "string", "enum": ["in", "out"] },
                  "medium": { "type": "string", "enum": ["refrigerant", "liquid", "heat", "signal", "power"] }
                },
                "additionalProperties": false
              }
            },
            "ui": {
              "type": "object",
              "nullable": true,
              "properties": {
                "position": {
                  "type": "object",
                  "nullable": true,
                  "required": ["x", "y"],
                  "properties": {
                    "x": { "type": "number" },
                    "y": { "type": "number" }
                  },
                  "additionalProperties": false
                }
              },
              "additionalProperties": false
            }
          },
          "additionalProperties": false
        }
      },
      "connections": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["id", "from", "to", "type"],
          "properties": {
            "id": { "type": "string" },
            "from": {
              "type": "object",
              "required": ["id", "port"],
              "properties": {
                "id": { "type": "string" },
                "port": { "type": "string" }
              },
              "additionalProperties": false
            },
            "to": {
              "type": "object",
              "required": ["id", "port"],
              "properties": {
                "id": { "type": "string" },
                "port": { "type": "string" }
              },
              "additionalProperties": false
            },
            "type": { "type": "string", "enum": ["fluid", "heat", "signal", "power"] }
          },
          "additionalProperties": false
        }
      },
      "simulation": {
        "type": "object",
        "required": ["start", "stop", "integrator", "scenario", "tolerances"],
        "properties": {
          "start": { "type": "number" },
          "stop": { "type": "number" },
          "integrator": { "type": "string", "enum": ["BDF2", "TRAP"] },
          "scenario": { "type": ["string", "null"] },
          "tolerances": {
            "type": "object",
            "required": ["absolute", "relative"],
            "properties": {
              "absolute": { "type": "number" },
              "relative": { "type": "number" }
            },
            "additionalProperties": false
          }
        },
        "additionalProperties": false
      },
      "units": {
        "type": "object",
        "required": ["temperature", "pressure", "massFlow"],
        "properties": {
          "temperature": { "type": "string", "enum": ["C", "K"] },
          "pressure": { "type": "string", "enum": ["Pa", "bar"] },
          "massFlow": { "type": "string", "enum": ["kg/s", "g/s"] }
        },
        "additionalProperties": false
      },
      "metadata": { "type": ["object", "null"], "additionalProperties": true }
    },
    "additionalProperties": false
  }
  """
)

_validator = Draft202012Validator(PROJECT_SCHEMA)


def validate_project(data: Dict[str, Any]) -> None:
  errors = sorted(_validator.iter_errors(data), key=lambda e: e.path)
  if errors:
    messages = [f"{'/'.join(map(str, error.path)) or '/'}: {error.message}" for error in errors]
    raise ValueError('Project validation failed: ' + '; '.join(messages))


def parse_project(data: Dict[str, Any]) -> ProjectGraph:
  validate_project(data)
  components = [
    Component(
      id=item['id'],
      type=item['type'],
      modeling=item['modeling'],
      params=item.get('params', {}),
      ports=[Port(**port) for port in item.get('ports', [])],
      ui=item.get('ui'),
    )
    for item in data['components']
  ]
  connections = [
    Connection(
      id=item['id'],
      from_=ConnectionEnd(**item['from']),
      to=ConnectionEnd(**item['to']),
      type=item['type'],
    )
    for item in data['connections']
  ]
  project = ProjectGraph(
    version=data['version'],
    fluids=data['fluids'],
    components=components,
    connections=connections,
    simulation=SimulationConfig(**data['simulation']),
    units=Units(**data['units']),
    metadata=data.get('metadata'),
  )
  return project
