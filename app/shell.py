"""PyQt6 desktop shell hosting the pod UI.

The UI is loaded from disk and talks to Python over QWebChannel, so the app
runs no web server and opens no port.
"""

import os
import sys
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QUrl
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow

from .bridge import Bridge

UI_DIR = Path(__file__).resolve().parent / "ui"


class JarvisWindow(QMainWindow):
    def __init__(self, agent: Any):
        super().__init__()
        self.setWindowTitle("JARVIS")
        self.resize(1280, 820)

        self._view = QWebEngineView(self)
        self._bridge = Bridge(agent, self)

        self._channel = QWebChannel(self._view.page())
        self._channel.registerObject("jarvisBridge", self._bridge)
        self._view.page().setWebChannel(self._channel)

        self._view.load(QUrl.fromLocalFile(str(UI_DIR / "index.html")))
        self.setCentralWidget(self._view)


def run(agent: Any) -> int:
    # Attach Chrome DevTools at http://localhost:9222 when debugging the UI.
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")

    app = QApplication(sys.argv)
    window = JarvisWindow(agent)
    window.show()
    return app.exec()
