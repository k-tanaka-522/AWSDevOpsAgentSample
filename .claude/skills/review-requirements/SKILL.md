---
name: review-requirements
description: >
  要件定義書のクロスレビュー。
  PMが作成した要件定義書を Consultant, App-Architect, Infra-Architect がレビュー。
  要件定義フェーズ完了後、PMがレビューを委譲した際に使用。
allowed-tools:
  - Read
  - Glob
---

# 要件定義書レビュースキル

## 概要

要件定義書（`docs/requirements/`）のクロスレビューを実施。

## レビュアー

| レビュアー | 観点 | チェックリスト |
|-----------|------|---------------|
| Consultant | ビジネス整合性 | `checklist/consultant.md` |
| App-Architect | 技術実現可能性（アプリ） | `checklist/app-architect.md` |
| Infra-Architect | 技術実現可能性（インフラ） | `checklist/infra-architect.md` |

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
