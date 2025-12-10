---
name: review-infra-design
description: >
  インフラ設計書のクロスレビュー。
  Infra-Architect が作成した設計書を SRE と Consultant がレビュー。
  設計フェーズ完了後、PMがレビューを委譲した際に使用。
allowed-tools:
  - Read
  - Glob
---

# インフラ設計書レビュースキル

## 概要

インフラ設計書（`docs/03_基本設計/infra/`）のクロスレビューを実施。

## レビュアー

| レビュアー | 観点 | チェックリスト |
|-----------|------|---------------|
| SRE | 運用・実装可能性 | `checklist/sre.md` |
| Consultant | ビジネス要件整合 | `checklist/consultant.md` |

## 使用方法

PMからTask委譲を受けた際、自分の役割に対応するチェックリストを参照してレビューを実施。

## 出力形式

```markdown
## レビュー結果

### 基本情報
- 対象: {ファイルパス}
- レビュアー: {自分の役割}
- 結果: approved / approved_with_comments / rejected

### チェックリスト
| 項目 | 状態 | 備考 |
|------|------|------|
| {項目1} | pass/warn/fail | {備考} |

### フィードバック
#### 良い点
- {良い点}

#### 改善が必要な点
- 箇所: {ファイル:行番号}
- 問題: {具体的な問題}
- 提案: {改善案}
```
