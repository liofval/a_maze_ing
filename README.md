**[English](README.md)** | **[日本語](README.ja.md)**

*This project has been created as part of the 42 curriculum by kaztakam,monoda.*

## Description

A-Maze-ing is a maze generator written in Python that creates random mazes with visual display. It supports multiple generation algorithms, seed-based reproducibility, and outputs mazes in a hexadecimal wall-encoding format. The program also embeds a visible "42" pattern into the maze using fully closed cells.

### Features

- Perfect maze generation (exactly one path between any two points)
- Imperfect maze generation (multiple paths with loops)
- Two generation algorithms: Recursive Backtracker and Kruskal's
- BFS shortest path solver
- ASCII terminal visualization with ANSI colors
- Interactive controls (regenerate, toggle path, change colors)
- Step-by-step maze generation animation in the terminal
- Reusable `mazegen` library installable via pip

## Instructions

### Requirements

- Python 3.10 or later
- No external dependencies for core functionality

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

### Running

```bash
python3 a_maze_ing.py config.txt
```

Or via Makefile:

```bash
make run
```

### Linting

```bash
make lint          # flake8 + mypy
make lint-strict   # flake8 + mypy --strict
```

### Testing

```bash
make test
```

### Building the mazegen package

```bash
make build
```

This produces `mazegen-1.0.0-py3-none-any.whl` and `mazegen-1.0.0.tar.gz` at the repository root.

## Configuration File

The configuration file uses `KEY=VALUE` format, one pair per line. Lines starting with `#` are comments.

### Required Keys

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width (number of cells) | `WIDTH=20` |
| `HEIGHT` | Maze height (number of cells) | `HEIGHT=15` |
| `ENTRY` | Entry coordinates (x,y) | `ENTRY=0,0` |
| `EXIT` | Exit coordinates (x,y) | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Perfect maze flag (True/False) | `PERFECT=True` |

### Optional Keys

| Key | Description | Default |
|-----|-------------|---------|
| `SEED` | Random seed for reproducibility | Random |
| `ALGORITHM` | Generation algorithm | `recursive_backtracker` |

### Available Algorithms

- `recursive_backtracker` — Iterative DFS. Produces long, winding corridors.
- `kruskal` — Randomized Kruskal's with Union-Find. Produces shorter, branchy paths.

### Example

```
# A-Maze-ing default configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=recursive_backtracker
```

## Maze Generation Algorithm

### Primary: Recursive Backtracker (Iterative DFS)

The default algorithm uses depth-first search with an explicit stack (not Python recursion, to avoid stack overflow on large mazes). It starts from the entry cell and carves passages by randomly choosing unvisited neighbors. When no unvisited neighbors remain, it backtracks. This naturally produces a perfect maze (spanning tree).

### Why this algorithm

- Simple to understand and implement — good learning value
- Produces aesthetically pleasing mazes with long corridors
- Naturally generates perfect mazes without additional processing
- Iterative stack avoids Python's recursion limit

### Secondary: Kruskal's Algorithm

Uses a Union-Find (disjoint set) data structure. All internal walls are shuffled randomly, then each wall is removed if it connects two separate components. This approach demonstrates a fundamentally different strategy and produces mazes with shorter dead-ends and more branching.

## Reusable Code — mazegen Library

The `mazegen/` package is a standalone maze generation library that can be installed via pip and imported in other projects. It contains no application-specific code (no config parsing, no file I/O, no display).

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic Usage

```python
from mazegen import MazeGenerator

gen = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_=(19, 14),
    seed=42,
)
maze = gen.generate()
path = gen.solve()
```

### Custom Parameters

```python
gen = MazeGenerator(
    width=30,
    height=20,
    entry=(0, 0),
    exit_=(29, 19),
    perfect=False,           # allow loops
    seed=123,
    algorithm="kruskal",     # use Kruskal's algorithm
)
```

### Accessing the Structure

```python
maze = gen.get_maze()

# Iterate all cells
for cell in maze.iter_cells():
    print(f"({cell.x},{cell.y}) walls={cell.walls:#06b}")

# Check a specific wall
from mazegen import Direction
if maze.has_wall(5, 3, Direction.E):
    print("East wall is closed at (5,3)")

# Get the solution path
path = gen.solve()
if path:
    for step in path:
        print(step.to_char(), end="")
```

### Animated Generation

```python
# Step-by-step generation using a generator
for maze, x, y in gen.generate_animated():
    print(f"Carved cell ({x}, {y})")
# maze is now fully generated
```

### Extending with a New Algorithm

```python
from mazegen.algorithms.base import MazeAlgorithm
from mazegen.maze import Maze
import random

class MyAlgorithm(MazeAlgorithm):
    def generate(self, maze: Maze, rng: random.Random) -> None:
        # Carve passages by calling maze.remove_wall()
        ...
```

Register it in `mazegen/algorithms/__init__.py`:

```python
ALGORITHMS["my_algorithm"] = MyAlgorithm
```

## Architecture

```
a_maze_ing.py          Entry point
├── app/               Application layer
│   ├── config.py      Config parser (KEY=VALUE)
│   ├── formatter.py   Hex output writer
│   ├── controller.py  Interactive menu loop (with animation)
│   └── display/       Visualization
│       ├── base.py    MazeDisplay ABC
│       ├── terminal.py ASCII renderer
│       └── colors.py  ANSI color schemes
└── mazegen/           Reusable library (pip-installable)
    ├── maze.py        Direction, Cell, Maze data model
    ├── generator.py   MazeGenerator facade
    ├── solver.py      BFS shortest path
    ├── pattern.py     "42" pattern stamper
    ├── validator.py   Maze validation
    └── algorithms/    Strategy pattern
        ├── base.py    MazeAlgorithm ABC
        ├── recursive_backtracker.py
        └── kruskal.py
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `Direction(IntFlag)` with N=1,E=2,S=4,W=8 | Bit values match the output spec exactly — `format(walls, 'X')` produces correct hex with zero conversion |
| `Maze.remove_wall()` updates both sides | Wall coherence enforced structurally, not by discipline |
| Strategy pattern for algorithms | New algorithms added by implementing one method + registering in a dict |
| `mazegen/` separated from `app/` | Library has no app dependencies, installable standalone |
| Iterative DFS (not recursive) | Python recursion limit is 1000; a 100x100 maze has 10,000 cells |
| 42 pattern stamped before generation | Algorithm routes around frozen cells naturally |
| Generator-based animation (`yield`) | Algorithms expose intermediate states without coupling to display logic |

## Documentation

Detailed documentation is available in [`.docs/`](.docs/README.md):

| Document | Content |
|----------|---------|
| [Architecture](.docs/01-architecture.md) | Project structure and separation of concerns |
| [Data Model](.docs/02-data-model.md) | Direction, Cell, Maze internals |
| [Algorithms](.docs/03-algorithms.md) | How maze generation works |
| [Hex Encoding](.docs/04-hex-encoding.md) | Wall encoding format explained |
| [Design Patterns](.docs/05-design-patterns.md) | Strategy, Facade, Registry patterns |
| [42 Pattern](.docs/06-42-pattern.md) | How the "42" stamp is placed |
| [Solver](.docs/07-solver.md) | BFS shortest path algorithm |
| [Testing](.docs/08-testing.md) | Test strategy and writing tests |

## Team and Project Management

### Team Roles

| Member | Role |
|--------|------|
| kaztakam | Config parser, output formatter, validation logic, testing |
| monoda | Maze generation algorithms, visual display, animation, project integration |

### Planning and Evolution

**Initial plan:**

1. Define data model (Direction, Cell, Maze)
2. Implement Recursive Backtracker algorithm
3. Build config parser and output formatter
4. Add terminal visualization with interactive menu
5. Package as reusable `mazegen` library

**How it evolved:**

- Kruskal's algorithm was added as a second generation method to demonstrate extensibility of the Strategy pattern
- Animation feature was added using Python generators (`yield`), which required refactoring algorithms to expose intermediate steps via `generate_steps()`
- Input validation was strengthened after testing edge cases (1x1 mazes, oversized mazes, out-of-bounds coordinates)

### What Worked Well

- Separating `mazegen/` (library) from `app/` (application) early made the codebase clean and the packaging straightforward
- The Strategy pattern made adding Kruskal's trivial — one new file and one dict entry
- Wall coherence enforced at the `Maze.remove_wall()` level eliminated an entire class of bugs
- Using `IntFlag` for directions meant hex output required zero conversion logic

### What Could Be Improved

- The terminal renderer uses raw ANSI escape codes; a library like `curses` or `blessed` would be more robust across terminal types
- Test coverage could be expanded to include more edge cases for imperfect maze generation
- The animation speed is hardcoded; making it configurable via the config file would improve usability

### Tools Used

| Tool | Purpose |
|------|---------|
| Python 3.14 | Development language |
| flake8 | Linting |
| mypy (--strict) | Static type checking |
| pytest | Unit testing |
| setuptools + build | Package building (.whl, .tar.gz) |
| Claude (AI) | Architecture design, code generation, documentation |
| Git + GitHub | Version control and collaboration |

## Resources

- [Maze generation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracker](https://en.wikipedia.org/wiki/Maze_generation_algorithm#Randomized_depth-first_search)
- [Kruskal's Algorithm](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Union-Find data structure](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)

### AI Usage

AI (Claude) was used for:
- Initial project architecture design and file structure planning
- Code generation for all modules, with review and corrections applied
- Translation of the project subject PDF to Japanese
- Animation feature implementation (generator pattern, ANSI terminal control)

All generated code was reviewed, tested, and validated with `flake8`, `mypy --strict`, and `pytest`.
