# A-Maze-ing ドキュメント

このディレクトリには、プロジェクトの設計・実装を理解するための詳細ドキュメントが含まれています。

## 目次

| ドキュメント | 内容 |
|-------------|------|
| [01-architecture.md](01-architecture.md) | プロジェクト全体のアーキテクチャと責務分離 |
| [02-data-model.md](02-data-model.md) | Direction, Cell, Maze のデータモデル詳解 |
| [03-algorithms.md](03-algorithms.md) | 迷路生成アルゴリズムの仕組みと比較 |
| [04-hex-encoding.md](04-hex-encoding.md) | 16進数による壁エンコーディングの仕組み |
| [05-design-patterns.md](05-design-patterns.md) | 使用しているデザインパターンの解説 |
| [06-42-pattern.md](06-42-pattern.md) | 「42」パターンの配置ロジック |
| [07-solver.md](07-solver.md) | BFS 最短経路探索の仕組み |
| [08-testing.md](08-testing.md) | テスト戦略とテストの書き方 |

## 推奨する読み順

初学者は以下の順で読むことを推奨します:

1. **01-architecture** — 全体像を掴む
2. **02-data-model** — コアとなるデータ構造を理解する
3. **04-hex-encoding** — 出力形式の仕組みを理解する
4. **03-algorithms** — 迷路がどう生成されるかを学ぶ
5. **05-design-patterns** — なぜこの構造になっているかを理解する
6. 残りは必要に応じて参照
