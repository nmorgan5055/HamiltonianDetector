from __future__ import annotations

import math
from typing import Optional

from PySide6.QtCore import Qt, QPoint, QPointF, Signal
from PySide6.QtGui import (
    QBrush, QColor, QFont, QFontMetrics, QPainter, QPen, QPolygonF,
)
from PySide6.QtWidgets import (
    QColorDialog, QComboBox, QDialog, QDialogButtonBox, QHBoxLayout,
    QLabel, QLineEdit, QMenu, QPushButton, QVBoxLayout, QWidget,
)

from classes import Edge, Node


# ---------------------------------------------------------------------------
# Node edit dialog
# ---------------------------------------------------------------------------

class NodeDialog(QDialog):
    """Modal dialog for editing a node's name and colours."""

    def __init__(self, node: Node, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.node = node
        self.setWindowTitle("Edit Node")
        self._outline_color = QColor(node.outline_color)
        self._fill_color = QColor(node.fill_color)

        layout = QVBoxLayout(self)

        # Name
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit(node.name)
        name_row.addWidget(self.name_edit)
        layout.addLayout(name_row)

        # Outline colour
        outline_row = QHBoxLayout()
        outline_row.addWidget(QLabel("Outline colour:"))
        self.outline_btn = QPushButton()
        self._refresh_btn(self.outline_btn, self._outline_color)
        self.outline_btn.clicked.connect(self._pick_outline)
        outline_row.addWidget(self.outline_btn)
        layout.addLayout(outline_row)

        # Fill colour
        fill_row = QHBoxLayout()
        fill_row.addWidget(QLabel("Fill colour:"))
        self.fill_btn = QPushButton()
        self._refresh_btn(self.fill_btn, self._fill_color)
        self.fill_btn.clicked.connect(self._pick_fill)
        fill_row.addWidget(self.fill_btn)
        layout.addLayout(fill_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ------------------------------------------------------------------

    def _refresh_btn(self, btn: QPushButton, color: QColor) -> None:
        text_hex = "#000000" if color.lightnessF() > 0.5 else "#ffffff"
        btn.setText(color.name())
        btn.setStyleSheet(
            f"background-color: {color.name()}; color: {text_hex}; min-width: 90px;"
        )

    def _pick_outline(self) -> None:
        c = QColorDialog.getColor(self._outline_color, self)
        if c.isValid():
            self._outline_color = c
            self._refresh_btn(self.outline_btn, c)

    def _pick_fill(self) -> None:
        c = QColorDialog.getColor(self._fill_color, self)
        if c.isValid():
            self._fill_color = c
            self._refresh_btn(self.fill_btn, c)

    def apply(self) -> None:
        """Write validated dialog values back to the node."""
        text = self.name_edit.text().strip()
        if text:
            self.node.name = text
        self.node.outline_color = self._outline_color
        self.node.fill_color = self._fill_color


# ---------------------------------------------------------------------------
# Edge edit dialog
# ---------------------------------------------------------------------------

class EdgeDialog(QDialog):
    """Modal dialog for editing an edge's name, colour, endpoints and direction."""

    def __init__(
        self,
        edge: Edge,
        all_nodes: list[Node],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.edge = edge
        self.all_nodes = all_nodes
        self.setWindowTitle("Edit Edge")
        self._color = QColor(edge.color)

        layout = QVBoxLayout(self)

        # Name
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit(edge.name)
        name_row.addWidget(self.name_edit)
        layout.addLayout(name_row)

        # Colour
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Colour:"))
        self.color_btn = QPushButton()
        self._refresh_btn(self.color_btn, self._color)
        self.color_btn.clicked.connect(self._pick_color)
        color_row.addWidget(self.color_btn)
        layout.addLayout(color_row)

        # Source node
        src_row = QHBoxLayout()
        src_row.addWidget(QLabel("From:"))
        self.src_combo = QComboBox()
        for n in all_nodes:
            self.src_combo.addItem(n.name, n)
        self.src_combo.setCurrentIndex(all_nodes.index(edge.source))
        src_row.addWidget(self.src_combo)
        layout.addLayout(src_row)

        # Target node
        tgt_row = QHBoxLayout()
        tgt_row.addWidget(QLabel("To:"))
        self.tgt_combo = QComboBox()
        for n in all_nodes:
            self.tgt_combo.addItem(n.name, n)
        self.tgt_combo.setCurrentIndex(all_nodes.index(edge.target))
        tgt_row.addWidget(self.tgt_combo)
        layout.addLayout(tgt_row)

        # Direction override
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("Direction:"))
        self.dir_combo = QComboBox()
        self.dir_combo.addItem("Follow global", None)
        self.dir_combo.addItem("Force directed", True)
        self.dir_combo.addItem("Force undirected", False)
        if edge.directed_override is None:
            self.dir_combo.setCurrentIndex(0)
        elif edge.directed_override:
            self.dir_combo.setCurrentIndex(1)
        else:
            self.dir_combo.setCurrentIndex(2)
        dir_row.addWidget(self.dir_combo)
        layout.addLayout(dir_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ------------------------------------------------------------------

    def _refresh_btn(self, btn: QPushButton, color: QColor) -> None:
        text_hex = "#000000" if color.lightnessF() > 0.5 else "#ffffff"
        btn.setText(color.name())
        btn.setStyleSheet(
            f"background-color: {color.name()}; color: {text_hex}; min-width: 90px;"
        )

    def _pick_color(self) -> None:
        c = QColorDialog.getColor(self._color, self)
        if c.isValid():
            self._color = c
            self._refresh_btn(self.color_btn, c)

    def apply(self) -> None:
        """Write validated dialog values back to the edge."""
        self.edge.name = self.name_edit.text().strip()
        self.edge.color = self._color
        self.edge.source = self.src_combo.currentData()
        self.edge.target = self.tgt_combo.currentData()
        self.edge.directed_override = self.dir_combo.currentData()


# ---------------------------------------------------------------------------
# Graph canvas
# ---------------------------------------------------------------------------

class GraphCanvas(QWidget):
    """
    Interactive canvas for building and editing a graph.

    Modes
    -----
    node  — left-click empty canvas space to place a node
    edge  — left-click-drag from one node to another to create an edge;
            releasing on empty space silently cancels the drag
    move  — left-click-drag a node to reposition it; edges follow

    Right-clicking a node or edge opens a context menu to edit or delete it.
    """

    # Emitted whenever the set of edges or their overrides changes so that
    # MainWindow can refresh the direction controls.
    directionality_changed = Signal()

    # Arrowhead geometry constants
    _ARROW_LEN: int = 14
    _ARROW_HALF_ANGLE: float = math.radians(25)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.nodes: list[Node] = []
        self.edges: list[Edge] = []

        self.mode: str = "node"
        self.dark_mode: bool = False
        self.global_directed: bool = False

        # Edge-creation drag state
        self._drag_source: Optional[Node] = None
        self._drag_pos: Optional[QPointF] = None

        # Node-move drag state
        self._moving_node: Optional[Node] = None
        self._move_offset: QPointF = QPointF(0.0, 0.0)

        self._font = QFont("Arial", 10)

        self.setMinimumSize(640, 480)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    # ------------------------------------------------------------------
    # Public API (called by MainWindow)
    # ------------------------------------------------------------------

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        # Clear any in-progress interaction
        self._drag_source = None
        self._drag_pos = None
        self._moving_node = None
        self.update()

    def set_dark_mode(self, enabled: bool) -> None:
        self.dark_mode = enabled
        self.update()

    def set_global_directed(self, directed: bool) -> None:
        self.global_directed = directed
        self.update()

    def force_all_directed(self, directed: bool) -> None:
        """Clear all per-edge overrides and set the global flag uniformly."""
        for edge in self.edges:
            edge.directed_override = None
        self.global_directed = directed
        self.directionality_changed.emit()
        self.update()

    def has_mixed_directionality(self) -> bool:
        """
        Return True when at least two edges have different effective
        directionality (i.e. the graph is a mix of directed and undirected
        edges after applying per-edge overrides).
        """
        if not self.edges:
            return False
        effective = {self._edge_is_directed(e) for e in self.edges}
        return len(effective) > 1

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fm(self) -> QFontMetrics:
        return QFontMetrics(self._font)

    def _edge_is_directed(self, edge: Edge) -> bool:
        if edge.directed_override is not None:
            return edge.directed_override
        return self.global_directed

    def _node_at(self, x: float, y: float) -> Optional[Node]:
        """Return the topmost node whose circle contains (x, y), or None."""
        fm = self._fm()
        for node in reversed(self.nodes):
            if node.contains(x, y, fm):
                return node
        return None

    def _edge_at(self, x: float, y: float) -> Optional[Edge]:
        """
        Return the topmost edge whose line segment is within click threshold
        of (x, y).  Returns None if a node is under the cursor.
        """
        if self._node_at(x, y):
            return None
        for edge in reversed(self.edges):
            if edge.contains_point(x, y):
                return edge
        return None

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        bg = QColor("#1e1e2e") if self.dark_mode else QColor("#ffffff")
        painter.fillRect(self.rect(), bg)

        painter.setFont(self._font)
        fm = self._fm()

        # Draw edges beneath nodes
        for edge in self.edges:
            self._draw_edge(painter, edge, fm)

        # Drag-preview line while creating an edge
        if self._drag_source and self._drag_pos:
            drag_color = QColor("#aaaaaa") if self.dark_mode else QColor("#000000")
            pen = QPen(drag_color, 1.5, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawLine(
                QPointF(self._drag_source.x, self._drag_source.y),
                self._drag_pos,
            )

        # Draw nodes on top
        for node in self.nodes:
            self._draw_node(painter, node, fm)

    def _draw_node(self, painter: QPainter, node: Node, fm: QFontMetrics) -> None:
        r = node.radius(fm)

        painter.setBrush(QBrush(node.fill_color))
        painter.setPen(QPen(node.outline_color, 2))
        painter.drawEllipse(QPointF(node.x, node.y), r, r)

        painter.setPen(QPen(node.text_color()))
        tw = fm.horizontalAdvance(node.name)
        # Centre text vertically: shift down by half of (ascent - descent)
        ty = node.y + (fm.ascent() - fm.descent()) / 2
        painter.drawText(QPointF(node.x - tw / 2, ty), node.name)

    def _draw_edge(self, painter: QPainter, edge: Edge, fm: QFontMetrics) -> None:
        x1, y1 = edge.source.x, edge.source.y
        x2, y2 = edge.target.x, edge.target.y

        # Skip degenerate edges (nodes at identical position)
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist < 1:
            return

        angle = math.atan2(y2 - y1, x2 - x1)
        r1 = edge.source.radius(fm)
        r2 = edge.target.radius(fm)

        # Offset start/end to node boundaries so lines don't overlap circles
        sx = x1 + r1 * math.cos(angle)
        sy = y1 + r1 * math.sin(angle)
        ex = x2 - r2 * math.cos(angle)
        ey = y2 - r2 * math.sin(angle)

        painter.setPen(QPen(edge.color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(QPointF(sx, sy), QPointF(ex, ey))

        if self._edge_is_directed(edge):
            self._draw_arrowhead(painter, ex, ey, angle, edge.color)

        # Label slightly above the midpoint
        if edge.name:
            mx, my = edge.midpoint()
            label_color = QColor("#ffffff") if self.dark_mode else QColor("#000000")
            painter.setPen(QPen(label_color))
            tw = fm.horizontalAdvance(edge.name)
            painter.drawText(QPointF(mx - tw / 2, my - 6), edge.name)

    def _draw_arrowhead(
        self,
        painter: QPainter,
        tip_x: float,
        tip_y: float,
        angle: float,
        color: QColor,
    ) -> None:
        """Draw a filled triangular arrowhead at (tip_x, tip_y)."""
        base_angle_l = angle + math.pi - self._ARROW_HALF_ANGLE
        base_angle_r = angle + math.pi + self._ARROW_HALF_ANGLE

        tip = QPointF(tip_x, tip_y)
        left = QPointF(
            tip_x + self._ARROW_LEN * math.cos(base_angle_l),
            tip_y + self._ARROW_LEN * math.sin(base_angle_l),
        )
        right = QPointF(
            tip_x + self._ARROW_LEN * math.cos(base_angle_r),
            tip_y + self._ARROW_LEN * math.sin(base_angle_r),
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawPolygon(QPolygonF([tip, left, right]))

    # ------------------------------------------------------------------
    # Mouse events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        pos = event.position()
        x, y = pos.x(), pos.y()

        if event.button() == Qt.LeftButton:
            if self.mode == "node":
                if not self._node_at(x, y):
                    node = Node(x, y)
                    if self.dark_mode:
                        node.apply_dark_defaults()
                    self.nodes.append(node)
                    self.update()

            elif self.mode == "edge":
                hit = self._node_at(x, y)
                if hit:
                    self._drag_source = hit
                    self._drag_pos = pos

            elif self.mode == "move":
                hit = self._node_at(x, y)
                if hit:
                    self._moving_node = hit
                    self._move_offset = QPointF(x - hit.x, y - hit.y)

        elif event.button() == Qt.RightButton:
            self._show_context_menu(x, y, event.globalPosition().toPoint())

    def mouseMoveEvent(self, event) -> None:
        pos = event.position()
        x, y = pos.x(), pos.y()

        if self.mode == "edge" and self._drag_source:
            self._drag_pos = pos
            self.update()

        elif self.mode == "move" and self._moving_node:
            self._moving_node.x = x - self._move_offset.x()
            self._moving_node.y = y - self._move_offset.y()
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        x, y = event.position().x(), event.position().y()

        if event.button() == Qt.LeftButton:
            if self.mode == "edge" and self._drag_source:
                target = self._node_at(x, y)
                if target and target is not self._drag_source:
                    self.edges.append(Edge(self._drag_source, target))
                    self.directionality_changed.emit()
                # Cancel the drag regardless of whether an edge was created
                self._drag_source = None
                self._drag_pos = None
                self.update()

            elif self.mode == "move":
                self._moving_node = None

    # ------------------------------------------------------------------
    # Context menu
    # ------------------------------------------------------------------

    def _show_context_menu(self, x: float, y: float, global_pos: QPoint) -> None:
        node = self._node_at(x, y)
        edge = None if node else self._edge_at(x, y)

        menu = QMenu(self)

        if node:
            edit_action = menu.addAction("Edit node…")
            menu.addSeparator()
            delete_action = menu.addAction("Delete node")
            chosen = menu.exec(global_pos)

            if chosen == edit_action:
                dlg = NodeDialog(node, self)
                if dlg.exec():
                    dlg.apply()
                    self.update()

            elif chosen == delete_action:
                # Remove all edges connected to this node
                self.edges = [
                    e for e in self.edges
                    if e.source is not node and e.target is not node
                ]
                self.nodes.remove(node)
                self.directionality_changed.emit()
                self.update()

        elif edge:
            edit_action = menu.addAction("Edit edge…")
            menu.addSeparator()
            delete_action = menu.addAction("Delete edge")
            chosen = menu.exec(global_pos)

            if chosen == edit_action:
                dlg = EdgeDialog(edge, self.nodes, self)
                if dlg.exec():
                    dlg.apply()
                    self.directionality_changed.emit()
                    self.update()

            elif chosen == delete_action:
                self.edges.remove(edge)
                self.directionality_changed.emit()
                self.update()
