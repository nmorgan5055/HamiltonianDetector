# Hamiltonian Cycle Detector

Design a graph in a GUI, and run to see if there is a Hamiltonian cycle.

## Requirements

- Python 3.10+
- PySide6

## Installation

1. **Clone the repo** (or download the source):
   ```bash
   git clone <repo-url>
   cd HamiltonianDetector
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**:
   ```bash
   python main.py
   ```

## Usage

### Modes

Select a mode from the toolbar before interacting with the canvas.

| Mode | Action |
|------|--------|
| **Node** | Left-click on empty canvas to place a node |
| **Edge** | Left-click and drag from one node to another to create an edge |
| **Move** | Left-click and drag a node to reposition it; edges follow automatically |

### Editing

Right-click any **node** or **edge** to open a context menu with options to:
- Edit its name and colors
- Delete it (deleting a node also removes all connected edges)
- For edges: reassign the source or target node via dropdown

### Edge Direction

Use the **Edges** dropdown in the toolbar to set the global direction mode (Undirected / Directed).

Individual edges can override the global setting via their right-click context menu → Edit edge → Direction override.

If edges have conflicting overrides (a mix of directed and undirected), the global dropdown is greyed out and **Make All Directed** / **Make All Undirected** buttons appear to resolve the conflict.

### Dark Mode

Toggle **Dark Mode** in the toolbar. New nodes placed while dark mode is active will use dark default colors. Existing nodes keep their current colors.
