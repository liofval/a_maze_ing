# アーキテクチャ

## 全体構成

このプロジェクトは**ライブラリ層**と**アプリケーション層**の2層に分離されています。

```mermaid
graph TB
    subgraph "エントリーポイント"
        A[a_maze_ing.py]
    end

    subgraph "app/ — アプリケーション層"
        B[config.py<br/>設定パーサー]
        C[formatter.py<br/>出力ファイル]
        D[controller.py<br/>ユーザー操作]
        E[display/<br/>ビジュアル表示]
    end

    subgraph "mazegen/ — ライブラリ層"
        F[generator.py<br/>MazeGenerator]
        G[maze.py<br/>データモデル]
        H[algorithms/<br/>生成アルゴリズム]
        I[solver.py<br/>BFS経路探索]
        J[pattern.py<br/>42パターン]
        K[validator.py<br/>バリデーション]
    end

    A --> B
    A --> C
    A --> D
    A --> F
    D --> E
    D --> F
    C --> F
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    H --> G
    I --> G
    J --> G
    K --> G

    style A fill:#f9f,stroke:#333
    style F fill:#bbf,stroke:#333
    style G fill:#bfb,stroke:#333
```

## なぜ2層に分けるのか？

```
mazegen/  →  純粋なロジックだけ。ファイルI/O・表示・設定なし。
app/      →  mazegen を使うアプリケーション固有のコード。
```

この分離により:

- `mazegen` は **pip でインストール**して他プロジェクトから使える
- `app` は `mazegen` に依存するが、**逆方向の依存はない**
- テストが書きやすい（ライブラリ単体でテスト可能）

```mermaid
graph LR
    APP["app/"] -->|依存| LIB["mazegen/"]
    LIB -.->|依存しない| APP
```

## 実行フロー

プログラム実行時のデータの流れ:

```mermaid
sequenceDiagram
    participant User
    participant Main as a_maze_ing.py
    participant Config as config.py
    participant Gen as MazeGenerator
    participant Algo as Algorithm
    participant Pattern as pattern.py
    participant Solver as solver.py
    participant Fmt as formatter.py
    participant Disp as TerminalDisplay
    participant Ctrl as Controller

    User->>Main: python3 a_maze_ing.py config.txt
    Main->>Config: parse_config("config.txt")
    Config-->>Main: MazeConfig

    Main->>Gen: MazeGenerator(params)
    Main->>Gen: generate()
    Gen->>Pattern: stamp_42(maze, rng)
    Pattern-->>Gen: パターンセルをマーク
    Gen->>Algo: algorithm.generate(maze, rng)
    Algo-->>Gen: 迷路が掘られた
    Gen-->>Main: Maze

    Main->>Gen: solve()
    Gen->>Solver: solve_bfs(maze)
    Solver-->>Main: [Direction, ...]

    Main->>Fmt: write_maze_file(maze, path, "maze.txt")

    Main->>Disp: TerminalDisplay()
    Main->>Ctrl: MazeController(gen, display)
    Ctrl->>Disp: render(maze)
    Disp-->>User: 迷路が表示される

    loop インタラクティブループ
        User->>Ctrl: 1: 再生成 / 2: アニメーション再生成 / 3: パス表示 / 4: 色変更 / 5: 終了
        alt アニメーション再生成
            Ctrl->>Gen: generate_animated()
            loop 各ステップ
                Gen-->>Ctrl: (maze, x, y)
                Ctrl->>Disp: render_animated() — ANSIで上書き描画
            end
        else 通常操作
            Ctrl->>Disp: render(maze)
        end
        Disp-->>User: 更新された表示
    end
```

## ディレクトリ構成

```
a_maze_ing/
├── a_maze_ing.py            # エントリーポイント（ここだけが main() を持つ）
├── config.txt               # デフォルト設定ファイル
├── Makefile                 # ビルド・実行の自動化
├── pyproject.toml           # パッケージビルド設定
│
├── mazegen/                 # ライブラリ（pip installable）
│   ├── __init__.py          # 公開 API のエクスポート
│   ├── maze.py              # ★ 全ての基盤: Direction, Cell, Maze
│   ├── generator.py         # MazeGenerator（ファサード）
│   ├── solver.py            # BFS 最短経路
│   ├── pattern.py           # "42" パターンスタンプ
│   ├── validator.py         # 迷路の整合性チェック
│   └── algorithms/          # 生成アルゴリズム群
│       ├── __init__.py      # レジストリ（名前 → クラス）
│       ├── base.py          # MazeAlgorithm 抽象基底クラス
│       ├── recursive_backtracker.py
│       └── kruskal.py
│
├── app/                     # アプリケーション層
│   ├── __init__.py
│   ├── config.py            # KEY=VALUE パーサー
│   ├── formatter.py         # 16進出力ファイルライター
│   ├── controller.py        # ユーザー操作ループ
│   └── display/             # 表示バックエンド
│       ├── __init__.py
│       ├── base.py          # MazeDisplay 抽象基底クラス
│       ├── terminal.py      # ASCII ターミナルレンダラー
│       └── colors.py        # ANSI カラースキーム
│
└── tests/                   # テスト（提出対象外）
    ├── test_maze.py
    ├── test_algorithms.py
    ├── test_solver.py
    ├── test_config.py
    └── ...
```

## 依存関係のルール

```
a_maze_ing.py → app/* と mazegen/* の両方を使う（唯一の接点）
app/*         → mazegen/* を使う
mazegen/*     → mazegen/* 内のみ（app を import しない）
tests/*       → 何でも import できる
```

このルールにより、`mazegen/` の中のどのファイルにも `from app import ...` は存在しません。これが「責務の分離」の実践です。
