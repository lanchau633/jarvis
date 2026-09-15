"""QWebChannel bridge: the only object the web UI can reach in Python.

Agent calls are slow local inference, so they run on a worker thread and
return via signal. Anything invoked straight from a pyqtSlot would block
the Qt event loop and freeze the window mid-reply.
"""

from typing import Any

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot


class _AgentCall(QRunnable):
    def __init__(self, agent: Any, text: str, on_reply, on_error):
        super().__init__()
        self._agent = agent
        self._text = text
        self._on_reply = on_reply
        self._on_error = on_error

    def run(self) -> None:
        try:
            reply = self._agent.run(self._text)
        except Exception as exc:
            self._on_error(f"{type(exc).__name__}: {exc}")
            return
        self._on_reply(reply or "")


class Bridge(QObject):
    """Exposed to JavaScript as `window.jarvis`."""

    replyReady = pyqtSignal(str)
    agentFailed = pyqtSignal(str)
    busyChanged = pyqtSignal(bool)

    def __init__(self, agent: Any, parent: QObject | None = None):
        super().__init__(parent)
        self._agent = agent
        self._pool = QThreadPool(self)
        # Serialise agent calls; concurrent local inference would just
        # contend for the same CPU cores and make every reply slower.
        self._pool.setMaxThreadCount(1)

    @pyqtSlot(str)
    def sendMessage(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        self.busyChanged.emit(True)
        self._pool.start(_AgentCall(self._agent, text, self._emit_reply, self._emit_error))

    def _emit_reply(self, reply: str) -> None:
        self.busyChanged.emit(False)
        self.replyReady.emit(reply)

    def _emit_error(self, message: str) -> None:
        self.busyChanged.emit(False)
        self.agentFailed.emit(message)
