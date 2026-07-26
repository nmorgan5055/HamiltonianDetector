from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QComboBox, QVBoxLayout, QWidget,
)

from canvas import GraphCanvas


# ---------------------------------------------------------------------------
# Stylesheet constants
# ---------------------------------------------------------------------------

_LIGHT_STYLE = """
QMainWindow, QWidget {
    background-color: #f0f0f0;
    color: #1a1a1a;
}
QFrame#toolbar {
    background-color: #e4e4e4;
    border-bottom: 1px solid #c0c0c0;
}
QPushButton {
    background-color: #dcdcdc;
    border: 1px solid #b0b0b0;
    border-radius: 4px;
    padding: 4px 12px;
    color: #1a1a1a;
}
QPushButton:hover {
    background-color: #c8c8c8;
}
QPushButton:checked {
    background-color: #4a90d9;
    border-color: #2a6cb0;
    color: #ffffff;
}
QPushButton:checked:hover {
    background-color: #3a7fc8;
}
QPushButton:disabled {
    color: #999999;
}
QComboBox {
    background-color: #ffffff;
    border: 1px solid #b0b0b0;
    border-radius: 4px;
    padding: 3px 8px;
    color: #1a1a1a;
    min-width: 110px;
}
QComboBox:disabled {
    background-color: #e0e0e0;
    color: #888888;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1a1a1a;
    selection-background-color: #4a90d9;
    selection-color: #ffffff;
}
QLabel {
    color: #1a1a1a;
}
"""

_DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QFrame#toolbar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
}
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 12px;
    color: #cdd6f4;
}
QPushButton:hover {
    background-color: #45475a;
}
QPushButton:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
    color: #1e1e2e;
}
QPushButton:checked:hover {
    background-color: #74a8f0;
}
QPushButton:disabled {
    color: #585b70;
}
QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 3px 8px;
    color: #cdd6f4;
    min-width: 110px;
}
QComboBox:disabled {
    background-color: #24243e;
    color: #585b70;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}
QLabel {
    color: #cdd6f4;
}
"""


# ---------------------------------------------------------------------------
# Vertical separator helper
# ---------------------------------------------------------------------------

def _vsep() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.VLine)
    sep.setFrameShadow(QFrame.Sunken)
    return sep


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Hamiltonian Cycle Detector")
        self.resize(960, 680)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Toolbar
        toolbar = self._build_toolbar()
        root.addWidget(toolbar)

        # Canvas
        self.canvas = GraphCanvas()
        self.canvas.directionality_changed.connect(self._sync_direction_controls)
        root.addWidget(self.canvas, stretch=1)

        self._apply_theme(dark=False)

    # ------------------------------------------------------------------
    # Toolbar construction
    # ------------------------------------------------------------------

    def _build_toolbar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("toolbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(6)

        # ── Mode buttons ────────────────────────────────────────────────
        layout.addWidget(QLabel("Mode:"))

        self.btn_node = QPushButton("Node")
        self.btn_edge = QPushButton("Edge")
        self.btn_move = QPushButton("Move")

        for btn, mode in (
            (self.btn_node, "node"),
            (self.btn_edge, "edge"),
            (self.btn_move, "move"),
        ):
            btn.setCheckable(True)
            btn.setMinimumWidth(58)
            btn.clicked.connect(lambda _checked, m=mode: self._set_mode(m))
            layout.addWidget(btn)

        self.btn_node.setChecked(True)

        layout.addWidget(_vsep())

        # ── Edge direction controls ──────────────────────────────────────
        layout.addWidget(QLabel("Edges:"))

        self.dir_combo = QComboBox()
        self.dir_combo.addItem("Undirected", False)
        self.dir_combo.addItem("Directed", True)
        self.dir_combo.currentIndexChanged.connect(self._on_direction_combo_changed)
        layout.addWidget(self.dir_combo)

        # These appear only when edge overrides are mixed
        self.btn_all_directed = QPushButton("Make All Directed")
        self.btn_all_undirected = QPushButton("Make All Undirected")
        self.btn_all_directed.setVisible(False)
        self.btn_all_undirected.setVisible(False)
        self.btn_all_directed.clicked.connect(lambda: self._force_all(True))
        self.btn_all_undirected.clicked.connect(lambda: self._force_all(False))
        layout.addWidget(self.btn_all_directed)
        layout.addWidget(self.btn_all_undirected)

        layout.addWidget(_vsep())

        # ── Dark mode ────────────────────────────────────────────────────
        self.btn_dark = QPushButton("Dark Mode")
        self.btn_dark.setCheckable(True)
        self.btn_dark.clicked.connect(self._toggle_dark_mode)
        layout.addWidget(self.btn_dark)

        layout.addStretch()
        return bar

    # ------------------------------------------------------------------
    # Slot: mode buttons
    # ------------------------------------------------------------------

    def _set_mode(self, mode: str) -> None:
        self.btn_node.setChecked(mode == "node")
        self.btn_edge.setChecked(mode == "edge")
        self.btn_move.setChecked(mode == "move")
        self.canvas.set_mode(mode)

    # ------------------------------------------------------------------
    # Slots: direction controls
    # ------------------------------------------------------------------

    def _on_direction_combo_changed(self, index: int) -> None:
        directed: bool = self.dir_combo.itemData(index)
        self.canvas.set_global_directed(directed)

    def _sync_direction_controls(self) -> None:
        """Called whenever edges are added/removed or overrides change."""
        mixed = self.canvas.has_mixed_directionality()
        self.dir_combo.setEnabled(not mixed)
        self.btn_all_directed.setVisible(mixed)
        self.btn_all_undirected.setVisible(mixed)

    def _force_all(self, directed: bool) -> None:
        """Resolve a mixed state by forcing every edge to one direction."""
        self.canvas.force_all_directed(directed)
        # Sync the combo without triggering the signal again
        self.dir_combo.blockSignals(True)
        self.dir_combo.setCurrentIndex(1 if directed else 0)
        self.dir_combo.blockSignals(False)
        self.dir_combo.setEnabled(True)
        self.btn_all_directed.setVisible(False)
        self.btn_all_undirected.setVisible(False)

    # ------------------------------------------------------------------
    # Slot: dark mode
    # ------------------------------------------------------------------

    def _toggle_dark_mode(self, checked: bool) -> None:
        self._apply_theme(dark=checked)
        self.canvas.set_dark_mode(checked)

    def _apply_theme(self, dark: bool) -> None:
        self.setStyleSheet(_DARK_STYLE if dark else _LIGHT_STYLE)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
