"""
Desktop launcher for Ghosted.

Runs the FastAPI server in-process and opens the dashboard — in a native window
(pywebview) if available, otherwise the default browser. This is the entry point
to bundle into a downloadable .app / .exe with PyInstaller:

    pip install pyinstaller pywebview
    pyinstaller --noconfirm --windowed --name Ghosted \
        --add-data "static:static" \
        --collect-all instagrapi \
        desktop.py

The bundled app needs to write sessions/cache somewhere; see DATA_DIR handling in
ig_client.py (it uses a folder next to the code, which PyInstaller maps into the
bundle — for a real release point it at the user's home dir).
"""
from __future__ import annotations

import socket
import threading
import time
import urllib.request

import uvicorn

from server import app

HOST = "127.0.0.1"


def _free_port(preferred: int = 8001) -> int:
    """Use the preferred port if open, else let the OS pick a free one."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, preferred))
            return preferred
        except OSError:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                s2.bind((HOST, 0))
                return s2.getsockname()[1]


def _serve(port: int) -> None:
    uvicorn.run(app, host=HOST, port=port, log_level="warning")


def _wait_until_up(url: str, timeout: float = 20.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except Exception:
            time.sleep(0.2)


def main() -> None:
    port = _free_port()
    url = f"http://{HOST}:{port}/"

    threading.Thread(target=_serve, args=(port,), daemon=True).start()
    _wait_until_up(url)

    # Prefer a native desktop window; fall back to the browser.
    try:
        import webview  # pywebview
        webview.create_window("Ghosted", url, width=1180, height=820, min_size=(900, 600))
        webview.start()
    except Exception:
        import webbrowser
        webbrowser.open(url)
        print(f"Ghosted running at {url}  (Ctrl+C to quit)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
