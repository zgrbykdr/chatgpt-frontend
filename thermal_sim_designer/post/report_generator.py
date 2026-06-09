from __future__ import annotations


def generate_text_report(project) -> str:
    lines = [f"Proje: {project.project_name}", "", "Parça Sonuçları:"]
    for part in project.parts:
        temp = "çözülmedi" if part.temperature_result is None else f"{part.temperature_result:.2f} °C"
        lines.append(f"- {part.name}: {temp}, Q={part.heat_power:.3f} W")
    if project.results:
        lines.extend([
            "",
            f"Toplam Isı Girişi: {project.results.get('energy_in', 0):.3f} W",
            f"Toplam Isı Çıkışı: {project.results.get('energy_out', 0):.3f} W",
            f"Enerji Hatası: {project.results.get('energy_error_percent', 0):.3f} %",
        ])
    return "\n".join(lines)
