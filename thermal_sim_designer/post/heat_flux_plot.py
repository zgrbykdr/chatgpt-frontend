from __future__ import annotations

from matplotlib.figure import Figure


def create_heat_flux_figure(project):
    flows = project.results.get("heat_flows", []) if project.results else []
    if not flows:
        raise ValueError("Isı akısı/ısı geçişi sonucu yok. Önce solver çalıştırın.")
    labels = [item.get("label", "flow") for item in flows]
    values = [item.get("heat_flow_w", 0.0) for item in flows]
    figure = Figure(figsize=(6, 4))
    axis = figure.add_subplot(111)
    axis.bar(labels, values, color="#44bb99")
    axis.set_ylabel("Isı Geçişi [W]")
    axis.set_title("Boundary ve Interface Isı Geçişleri")
    axis.tick_params(axis="x", rotation=30)
    figure.tight_layout()
    return figure
