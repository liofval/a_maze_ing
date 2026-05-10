**[English](README.md)** | **[日本語](README.ja.md)**

*このプロジェクトは 42 カリキュラムの一環として kaztakam monoda により作成されました。*

## 概要

A-Maze-ing は Python で書かれた迷路ジェネレーターです。ランダムな迷路を生成し、視覚的に表示します。複数の生成アルゴリズム、シードによる再現性、16進数の壁エンコーディング形式での出力に対応しています。また、完全に閉じたセルを使って迷路内に「42」パターンを埋め込みます。

### 機能一覧

- 完全迷路の生成（任意の2点間に正確に1つの経路）
- 不完全迷路の生成（ループを含む複数の経路）
- 2つの生成アルゴリズム: Recursive Backtracker と Kruskal
- BFS による最短経路探索
- ANSI カラー対応の ASCII ターミナル表示
- インタラクティブ操作（再生成、パス表示切替、色変更）
- ターミナルでの迷路生成ステップアニメーション
- pip でインストール可能な再利用ライブラリ `mazegen`

## 使用方法

### 必要環境

- Python 3.10 以降
- コア機能に外部依存なし

### インストール

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

### 実行

```bash
python3 a_maze_ing.py config.txt
```

Makefile 経由:

```bash
make run
```

### リント

```bash
make lint          # flake8 + mypy
make lint-strict   # flake8 + mypy --strict
```

### テスト

```bash
make test
```

### mazegen パッケージのビルド

```bash
make build
```

リポジトリのルートに `mazegen-1.0.0-py3-none-any.whl` と `mazegen-1.0.0.tar.gz` が生成されます。

## 設定ファイル

設定ファイルは `KEY=VALUE` 形式で、1行に1ペア。`#` で始まる行はコメントです。

### 必須キー

| キー | 説明 | 例 |
|------|------|------|
| `WIDTH` | 迷路の幅（セル数） | `WIDTH=20` |
| `HEIGHT` | 迷路の高さ（セル数） | `HEIGHT=15` |
| `ENTRY` | 入口座標 (x,y) | `ENTRY=0,0` |
| `EXIT` | 出口座標 (x,y) | `EXIT=19,14` |
| `OUTPUT_FILE` | 出力ファイル名 | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | 完全迷路フラグ (True/False) | `PERFECT=True` |

### オプションキー

| キー | 説明 | デフォルト |
|------|------|-----------|
| `SEED` | 再現性のためのランダムシード | ランダム |
| `ALGORITHM` | 生成アルゴリズム | `recursive_backtracker` |

### 利用可能なアルゴリズム

- `recursive_backtracker` — 反復的DFS。長く曲がりくねった通路を生成。
- `kruskal` — Union-Find を用いたランダム化 Kruskal 法。短く分岐の多い経路を生成。

### 設定例

```
# A-Maze-ing デフォルト設定
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=recursive_backtracker
```

## 迷路生成アルゴリズム

### メイン: Recursive Backtracker（反復的DFS）

デフォルトのアルゴリズムは、明示的なスタックを使用した深さ優先探索です（Python の再帰ではなく、大きな迷路でのスタックオーバーフローを回避）。入口セルから開始し、未訪問の隣接セルをランダムに選んで通路を掘ります。未訪問の隣接セルがなくなったらバックトラックします。これにより自然に完全迷路（全域木）が生成されます。

### このアルゴリズムを選んだ理由

- 理解と実装が容易 — 学習価値が高い
- 長い通路を持つ美しい迷路を生成
- 追加処理なしで自然に完全迷路を生成
- 反復的スタックにより Python の再帰制限を回避

### サブ: Kruskal のアルゴリズム

Union-Find（素集合）データ構造を使用。全ての内部壁をランダムにシャッフルし、異なる連結成分を接続する壁を順に除去します。根本的に異なるアプローチを示すもので、短い行き止まりと多くの分岐を持つ迷路を生成します。

## 再利用可能コード — mazegen ライブラリ

`mazegen/` パッケージは、pip でインストールして他のプロジェクトにインポートできるスタンドアロンの迷路生成ライブラリです。アプリケーション固有のコード（設定パーサー、ファイル I/O、表示）は含みません。

### インストール

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### 基本的な使い方

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

### カスタムパラメータ

```python
gen = MazeGenerator(
    width=30,
    height=20,
    entry=(0, 0),
    exit_=(29, 19),
    perfect=False,           # ループを許可
    seed=123,
    algorithm="kruskal",     # Kruskal のアルゴリズムを使用
)
```

### 構造へのアクセス

```python
maze = gen.get_maze()

# 全セルを走査
for cell in maze.iter_cells():
    print(f"({cell.x},{cell.y}) walls={cell.walls:#06b}")

# 特定の壁を確認
from mazegen import Direction
if maze.has_wall(5, 3, Direction.E):
    print("(5,3) の東側の壁は閉じています")

# 解法経路を取得
path = gen.solve()
if path:
    for step in path:
        print(step.to_char(), end="")
```

### アニメーション生成

```python
# ジェネレータを使ったステップごとの生成
for maze, x, y in gen.generate_animated():
    print(f"セル ({x}, {y}) を掘削")
# maze は完全に生成済み
```

### 新しいアルゴリズムの追加

```python
from mazegen.algorithms.base import MazeAlgorithm
from mazegen.maze import Maze
import random

class MyAlgorithm(MazeAlgorithm):
    def generate(self, maze: Maze, rng: random.Random) -> None:
        # maze.remove_wall() を呼んで通路を掘る
        ...
```

`mazegen/algorithms/__init__.py` に登録:

```python
ALGORITHMS["my_algorithm"] = MyAlgorithm
```

## アーキテクチャ

```
a_maze_ing.py          エントリーポイント
├── app/               アプリケーション層
│   ├── config.py      設定パーサー (KEY=VALUE)
│   ├── formatter.py   16進出力ライター
│   ├── controller.py  インタラクティブメニューループ（アニメーション付き）
│   └── display/       ビジュアライゼーション
│       ├── base.py    MazeDisplay ABC
│       ├── terminal.py ASCII レンダラー
│       └── colors.py  ANSI カラースキーム
└── mazegen/           再利用可能ライブラリ (pip installable)
    ├── maze.py        Direction, Cell, Maze データモデル
    ├── generator.py   MazeGenerator ファサード
    ├── solver.py      BFS 最短経路
    ├── pattern.py     "42" パターンスタンプ
    ├── validator.py   迷路バリデーション
    └── algorithms/    Strategy パターン
        ├── base.py    MazeAlgorithm ABC
        ├── recursive_backtracker.py
        └── kruskal.py
```

### 主要な設計判断

| 判断 | 根拠 |
|------|------|
| `Direction(IntFlag)` で N=1,E=2,S=4,W=8 | ビット値が出力仕様と完全一致 — `format(walls, 'X')` が変換なしで正しい16進数を出力 |
| `Maze.remove_wall()` が両側を更新 | 壁の一貫性を規律ではなく構造で保証 |
| Strategy パターンでアルゴリズム実装 | 1メソッドの実装 + dict への登録だけで新アルゴリズム追加可能 |
| `mazegen/` と `app/` を分離 | ライブラリはアプリ依存なし、スタンドアロンでインストール可能 |
| 反復的DFS（再帰ではなく） | Python の再帰制限は1000; 100x100 の迷路は10,000セル |
| 42パターンを生成前にスタンプ | アルゴリズムが凍結セルを自然に回避 |
| ジェネレータベースのアニメーション (`yield`) | 表示ロジックと結合せずにアルゴリズムの中間状態を公開 |

## ドキュメント

詳細なドキュメントが [`.docs/`](.docs/README.md) にあります:

| ドキュメント | 内容 |
|-------------|------|
| [アーキテクチャ](.docs/01-architecture.md) | プロジェクト全体の構成と責務分離 |
| [データモデル](.docs/02-data-model.md) | Direction, Cell, Maze の詳解 |
| [アルゴリズム](.docs/03-algorithms.md) | 迷路生成の仕組みと比較 |
| [16進エンコーディング](.docs/04-hex-encoding.md) | 壁エンコーディング形式の解説 |
| [デザインパターン](.docs/05-design-patterns.md) | Strategy, Facade, Registry パターン |
| [42 パターン](.docs/06-42-pattern.md) | 「42」スタンプの配置ロジック |
| [ソルバー](.docs/07-solver.md) | BFS 最短経路アルゴリズム |
| [テスト](.docs/08-testing.md) | テスト戦略とテストの書き方 |

## 参考資料

- [Maze generation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracker](https://en.wikipedia.org/wiki/Maze_generation_algorithm#Randomized_depth-first_search)
- [Kruskal's Algorithm](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Union-Find data structure](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)

### AI の使用について

AI (Claude) は以下の用途で使用しました:
- プロジェクトのアーキテクチャ設計とファイル構成の計画
- 全モジュールのコード生成（レビューと修正を適用）
- プロジェクト課題 PDF の日本語翻訳
- アニメーション機能の実装（ジェネレータパターン、ANSIターミナル制御）

生成されたコードは全て `flake8`、`mypy --strict`、`pytest` でレビュー、テスト、検証済みです。
