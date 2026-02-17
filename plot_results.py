"""Simple plotting helpers for logged diagnostics and velocity slices."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from cfdles.mesh import generate_mesh
from cfdles.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Config used in simulation")
    args = parser.parse_args()

    cfg = load_config(args.config)
    log = Path(cfg.output.directory) / f"{cfg.output.prefix}_log.csv"
    data = np.genfromtxt(log, delimiter=",", names=True)

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    axs[0].plot(data["time"], data["kinetic_energy"])
    axs[0].set_title("Kinetic energy vs time")
    axs[0].set_xlabel("time")
    axs[0].set_ylabel("KE")

    axs[1].plot(data["time"], data["div_l2"])
    axs[1].set_title("Divergence L2 vs time")
    axs[1].set_xlabel("time")
    axs[1].set_ylabel("||div||")

    plt.tight_layout()
    out = Path(cfg.output.directory) / f"{cfg.output.prefix}_diagnostics.png"
    plt.savefig(out, dpi=140)

    mesh = generate_mesh(cfg)
    yc = mesh.yc
    centerline = 0.5 * (1.0 - np.abs(2.0 * yc / cfg.mesh.lengths[1] - 1.0))
    plt.figure(figsize=(4, 4))
    plt.plot(centerline, yc)
    plt.xlabel("u (qualitative profile)")
    plt.ylabel("y")
    plt.title("Centerline velocity template")
    plt.tight_layout()
    plt.savefig(Path(cfg.output.directory) / f"{cfg.output.prefix}_centerline_template.png", dpi=140)


if __name__ == "__main__":
    main()
