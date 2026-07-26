from __future__ import annotations

import math
from typing import Optional

from PySide6.QtGui import QColor, QFontMetrics


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------

class Node:
    """Represents a graph vertex drawn as a labelled circle on the canvas."""

    _id_counter: int = 0

    def __init__(self, x: float, y: float, name: str = "") -> None:
        Node._id_counter += 1
        self.id: int = Node._id_counter
        self.name: str = name if name else f"n{self.id}"
        self.x: float = x
        self.y: float = y
        self.outline_color: QColor = QColor("#000000")
        self.fill_color: QColor = QColor("#ffffff")

    # ------------------------------------------------------------------
    # Geometry
    # ------------------------------------------------------------------

    MIN_RADIUS: int = 30
    PADDING: int = 12  # extra space around text inside circle

    def radius(self, fm: QFontMetrics) -> int:
        """
        Compute the smallest circle radius that fully contains the node label.
        The circle must enclose a rectangle of (text_width x text_height), so
        the minimum enclosing radius is half the diagonal, plus padding.
        """
        tw = fm.horizontalAdvance(self.name)
        th = fm.height()
        half_diag = math.ceil(math.hypot(tw / 2, th / 2))
        return max(self.MIN_RADIUS, half_diag + self.PADDING)

    def contains(self, x: float, y: float, fm: QFontMetrics) -> bool:
        """Return True if the point (x, y) falls inside this node's circle."""
        return math.hypot(x - self.x, y - self.y) <= self.radius(fm)

    # ------------------------------------------------------------------
    # Colour helpers
    # ------------------------------------------------------------------

    def text_color(self) -> QColor:
        """
        Return black or white for the label, chosen by the perceived luminance
        of the node fill so that text is always legible (WCAG relative formula).
        """
        r = self.fill_color.red()
        g = self.fill_color.green()
        b = self.fill_color.blue()
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return QColor("#000000") if luminance > 128 else QColor("#ffffff")

    # ------------------------------------------------------------------
    # Dark-mode defaults (applied when the node is first placed)
    # ------------------------------------------------------------------

    def apply_dark_defaults(self) -> None:
        self.fill_color = QColor("#2b2b3b")
        self.outline_color = QColor("#aaaaaa")

    def apply_light_defaults(self) -> None:
        self.fill_color = QColor("#ffffff")
        self.outline_color = QColor("#000000")

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Node(id={self.id}, name={self.name!r}, x={self.x:.1f}, y={self.y:.1f})"


# ---------------------------------------------------------------------------
# Edge
# ---------------------------------------------------------------------------

class Edge:
    """Represents a graph edge (optionally directed) between two Node objects."""

    _id_counter: int = 0

    def __init__(self, source: Node, target: Node) -> None:
        Edge._id_counter += 1
        self.id: int = Edge._id_counter
        self.source: Node = source
        self.target: Node = target
        self.name: str = ""
        self.color: QColor = QColor("#000000")
        # None  → follow the canvas-level global setting
        # True  → always directed, regardless of global setting
        # False → always undirected, regardless of global setting
        self.directed_override: Optional[bool] = None

    # ------------------------------------------------------------------
    # Geometry
    # ------------------------------------------------------------------

    def midpoint(self) -> tuple[float, float]:
        """Return the midpoint of the straight line between source and target."""
        return (
            (self.source.x + self.target.x) / 2,
            (self.source.y + self.target.y) / 2,
        )

    def contains_point(
        self, x: float, y: float, threshold: float = 8.0
    ) -> bool:
        """
        Return True if (x, y) is within *threshold* pixels of the edge line
        segment.  Uses the standard point-to-segment distance formula.
        """
        x1, y1 = self.source.x, self.source.y
        x2, y2 = self.target.x, self.target.y

        dx, dy = x2 - x1, y2 - y1
        length_sq = dx * dx + dy * dy

        if length_sq == 0:
            # Degenerate edge (source == target position)
            return math.hypot(x - x1, y - y1) <= threshold

        # Project (x, y) onto the segment, clamped to [0, 1]
        t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / length_sq))
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy
        return math.hypot(x - nearest_x, y - nearest_y) <= threshold

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        arrow = "->" if self.directed_override else "--"
        return (
            f"Edge(id={self.id}, {self.source.name!r} {arrow} {self.target.name!r},"
            f" name={self.name!r})"
        )
