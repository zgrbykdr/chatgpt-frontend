from __future__ import annotations

from matplotlib.figure import Figure


def create_temperature_figure(project):
    parts = [p for p in project.parts if p.temperature_result is not None]
    if not parts:
        raise ValueError("Sıcaklık sonucu yok. Önce solver çalıştırın.")
    figure = Figure(figsize=(6, 4))
    axis = figure.add_subplot(111)
    axis.bar([p.name for p in parts], [p.temperature_result for p in parts], color="#ee8866")
    axis.set_ylabel("Sıcaklık [°C]")
    axis.set_title("Parça Sıcaklıkları")
    axis.tick_params(axis="x", rotation=30)
    figure.tight_layout()
    return figure
