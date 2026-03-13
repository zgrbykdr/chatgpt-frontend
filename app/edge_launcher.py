from __future__ import annotations

import shlex
import subprocess
from pathlib import Path


class EdgeLaunchError(Exception):
    """Edge başlatma süreçlerinde fırlatılan hata."""


def open_url_in_edge(
    url: str,
    edge_path: str,
    profile_path: str,
    profile_name: str = "Default",
    extra_args: str = "",
) -> None:
    if not edge_path or not Path(edge_path).exists():
        raise EdgeLaunchError("Microsoft Edge yolu bulunamadı. Ayarlardan doğru yolu seçin.")

    command = [edge_path, "--new-tab", url]

    if profile_path:
        if not Path(profile_path).exists():
            raise EdgeLaunchError("Edge profil klasörü bulunamadı. Ayarlardan kontrol edin.")
        command.insert(1, f"--user-data-dir={profile_path}")

    if profile_name:
        command.insert(1, f"--profile-directory={profile_name}")

    if extra_args.strip():
        command[1:1] = shlex.split(extra_args)

    try:
        subprocess.Popen(command, shell=False)
    except OSError as exc:
        raise EdgeLaunchError(f"Edge başlatılamadı: {exc}") from exc
