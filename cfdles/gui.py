"""Desktop GUI for running demos and visualizing LES outputs."""

from __future__ import annotations

import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class CFDLESGUI(tk.Tk):
    """Simple Tk GUI for launching runs and visualizing snapshots."""

    def __init__(self) -> None:
        super().__init__()
        self.title("CFDLES GUI")
        self.geometry("1180x760")

        self.config_var = tk.StringVar(value="demos/cavity.json")
        self.output_var = tk.StringVar(value="outputs/cavity")
        self.status_var = tk.StringVar(value="Ready")
        self.slice_axis_var = tk.StringVar(value="z")
        self.slice_index_var = tk.IntVar(value=0)
        self.field_var = tk.StringVar(value="u")

        self.snapshot_files: list[Path] = []
        self.current_snapshot: dict[str, np.ndarray] | None = None

        self._build_layout()

    def _build_layout(self) -> None:
        controls = ttk.Frame(self)
        controls.pack(fill=tk.X, padx=8, pady=8)

        ttk.Label(controls, text="Config JSON").grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.config_var, width=35).grid(row=0, column=1, sticky="we", padx=6)
        ttk.Button(controls, text="Run Simulation", command=self.run_case).grid(row=0, column=2, padx=4)

        ttk.Label(controls, text="Output Folder").grid(row=1, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.output_var, width=35).grid(row=1, column=1, sticky="we", padx=6)
        ttk.Button(controls, text="Refresh Files", command=self.refresh_files).grid(row=1, column=2, padx=4)

        ttk.Label(controls, text="Field").grid(row=0, column=3, sticky="w", padx=(24, 0))
        field_cb = ttk.Combobox(controls, textvariable=self.field_var, values=["u", "v", "w", "p", "nu_t", "s_mag", "divergence"], width=11)
        field_cb.grid(row=0, column=4, padx=4)
        field_cb.bind("<<ComboboxSelected>>", lambda _e: self.plot_snapshot())

        ttk.Label(controls, text="Slice axis").grid(row=1, column=3, sticky="w", padx=(24, 0))
        axis_cb = ttk.Combobox(controls, textvariable=self.slice_axis_var, values=["x", "y", "z"], width=11)
        axis_cb.grid(row=1, column=4, padx=4)
        axis_cb.bind("<<ComboboxSelected>>", lambda _e: self.plot_snapshot())

        ttk.Label(controls, text="Slice index").grid(row=0, column=5, sticky="w")
        idx_spin = ttk.Spinbox(controls, from_=0, to=999, textvariable=self.slice_index_var, width=8, command=self.plot_snapshot)
        idx_spin.grid(row=0, column=6, padx=4)

        ttk.Label(controls, textvariable=self.status_var).grid(row=1, column=5, columnspan=2, sticky="w")
        controls.columnconfigure(1, weight=1)

        main = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        left = ttk.Frame(main)
        right = ttk.Frame(main)
        main.add(left, weight=1)
        main.add(right, weight=3)

        ttk.Label(left, text="Snapshots (.npz)").pack(anchor="w")
        self.file_list = tk.Listbox(left)
        self.file_list.pack(fill=tk.BOTH, expand=True, pady=6)
        self.file_list.bind("<<ListboxSelect>>", self.on_select_snapshot)

        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax_field = self.fig.add_subplot(2, 2, 1)
        self.ax_quiver = self.fig.add_subplot(2, 2, 2)
        self.ax_ke = self.fig.add_subplot(2, 1, 2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_case(self) -> None:
        cfg = Path(self.config_var.get())
        if not cfg.exists():
            messagebox.showerror("Missing config", f"Config not found: {cfg}")
            return

        def worker() -> None:
            self.status_var.set("Running simulation...")
            try:
                subprocess.run(["python", "run_demo.py", str(cfg)], check=True)
                self.status_var.set("Simulation complete")
                self.refresh_files()
            except subprocess.CalledProcessError as exc:
                self.status_var.set("Run failed")
                messagebox.showerror("Run failed", str(exc))

        threading.Thread(target=worker, daemon=True).start()

    def refresh_files(self) -> None:
        out = Path(self.output_var.get())
        out.mkdir(parents=True, exist_ok=True)
        self.snapshot_files = sorted(out.glob("*.npz"))
        self.file_list.delete(0, tk.END)
        for p in self.snapshot_files:
            self.file_list.insert(tk.END, p.name)
        if self.snapshot_files:
            self.file_list.selection_clear(0, tk.END)
            self.file_list.selection_set(tk.END)
            self.file_list.event_generate("<<ListboxSelect>>")

    def on_select_snapshot(self, _event: object) -> None:
        selection = self.file_list.curselection()
        if not selection:
            return
        snap = self.snapshot_files[selection[0]]
        with np.load(snap) as data:
            self.current_snapshot = {k: data[k] for k in data.files}
        self.status_var.set(f"Loaded {snap.name}")
        self.plot_snapshot()

    def _slice_field(self, arr: np.ndarray, axis: str, idx: int) -> np.ndarray:
        if axis == "x":
            idx = max(0, min(idx, arr.shape[0] - 1))
            return arr[idx, :, :]
        if axis == "y":
            idx = max(0, min(idx, arr.shape[1] - 1))
            return arr[:, idx, :]
        idx = max(0, min(idx, arr.shape[2] - 1))
        return arr[:, :, idx]

    def plot_snapshot(self) -> None:
        if self.current_snapshot is None:
            return

        field_name = self.field_var.get()
        axis = self.slice_axis_var.get()
        idx = int(self.slice_index_var.get())

        arr = self.current_snapshot[field_name]
        fld = self._slice_field(arr, axis, idx)

        self.ax_field.clear()
        im = self.ax_field.imshow(fld.T, origin="lower", aspect="auto", cmap="turbo")
        self.ax_field.set_title(f"{field_name} slice ({axis}={idx})")
        self.fig.colorbar(im, ax=self.ax_field, fraction=0.046, pad=0.04)

        u = self.current_snapshot["u"]
        v = self.current_snapshot["v"]
        w = self.current_snapshot["w"]
        self.ax_quiver.clear()
        if axis == "x":
            uu = self._slice_field(v, axis, idx)
            vv = self._slice_field(w, axis, idx)
        elif axis == "y":
            uu = self._slice_field(u, axis, idx)
            vv = self._slice_field(w, axis, idx)
        else:
            uu = self._slice_field(u, axis, idx)
            vv = self._slice_field(v, axis, idx)

        stride = max(1, min(uu.shape[0], uu.shape[1]) // 24)
        yy, xx = np.mgrid[0:uu.shape[0]:stride, 0:uu.shape[1]:stride]
        self.ax_quiver.quiver(xx, yy, uu[::stride, ::stride].T, vv[::stride, ::stride].T, scale=20)
        self.ax_quiver.set_title("In-plane velocity vectors")

        self.ax_ke.clear()
        out_dir = Path(self.output_var.get())
        csv_files = sorted(out_dir.glob("*_log.csv"))
        if csv_files:
            data = np.genfromtxt(csv_files[-1], delimiter=",", names=True)
            if data.size > 0:
                self.ax_ke.plot(data["time"], data["kinetic_energy"], label="KE")
                self.ax_ke.plot(data["time"], data["div_l2"], label="||div||")
                self.ax_ke.set_xlabel("time")
                self.ax_ke.legend()
                self.ax_ke.set_title("Run diagnostics")

        self.fig.tight_layout()
        self.canvas.draw_idle()


def main() -> None:
    app = CFDLESGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
