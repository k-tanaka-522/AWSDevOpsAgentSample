# AIdev開発プロセス規約 - Notion 完全ガイド

## 📖 このドキュメントについて

このドキュメントは、**AIdev開発プロセス規約**の完全版がまとまっているNotionワークスペースへのナビゲーションガイドです。

Claude Codeを活用した開発において、AIファシリテーターとして機能するための実践的な規約とガイドラインがすべて含まれています。

---

## 🌐 Notion ワークスペース（メインページ）

**AIdev開発プロセス規約 - トップページ:**
https://pacific-packet-4aa.notion.site/AIdev-28f3b027c0d18191abddc81d578ecd68

**使い方:**
- 初めての方は、上記トップページから「01 コア行動原則」を最初に読んでください
- 実装・設計時は、該当するセクション（04 技術標準）を参照してください
- 困ったときは「05 よくある質問・トラブルシューティング」を確認してください

---

## 📋 目次 - フェーズ別テンプレート・パターン集

このインデックスは、**開発フェーズごとに必要なテンプレート・パターンへの直リンク集**です。

実装・設計時に該当するページを開いて、規約・Good Example・Bad Exampleを確認してください。

---

## 🎯 フェーズ別ナビゲーション

### 企画フェーズ
- ビジネスゴール設定
- ステークホルダー分析
- プロジェクトスコープ定義

### 要件定義フェーズ
- 機能要件テンプレート
- 非機能要件テンプレート
- 制約条件の整理

### 設計フェーズ
- アーキテクチャパターン選定
- Infrastructure as Code 設計
- API設計標準

### 実装フェーズ
- コーディング規約（言語別）
- コードテンプレート
- エラーハンドリングパターン

### テストフェーズ
- テストパターン
- テストケーステンプレート
- カバレッジ基準

### 納品フェーズ
- デプロイチェックリスト
- ドキュメントテンプレート
- リリースノートテンプレート

---

## 📌 コア行動原則

**01 コア行動原則**
https://pacific-packet-4aa.notion.site/01-2903b027c0d180dd903fd11890c487f5

AI開発ファシリテーターとしての使命と、絶対に譲らない3つの原則。
- 原則1: ビジネス理解が最優先
- 原則2: 抜け漏れは命取り
- 原則3: ドキュメントが成果物

---

## 📅 フェーズ管理

**02 開発フェーズ管理**
https://pacific-packet-4aa.notion.site/02-2903b027c0d180429fdff2898983eb95

企画 → 要件定義 → 設計 → 実装 → テスト → デプロイのフェーズ遷移管理。

**▶ 2.1 フェーズ遷移ルール**
https://pacific-packet-4aa.notion.site/2-1-2903b027c0d181ff9daef1c8e6aeede5

各フェーズの開始条件・完了条件・遷移ルールを定義。

**▶ 2.2 フェーズごとの決定項目**
https://pacific-packet-4aa.notion.site/2-2-2903b027c0d181b6824ad36625d3b01c

各フェーズで必ず決定すべき項目のチェックリスト。

---

## 💬 ファシリテーション戦略

**03 ファシリテーション戦略**
https://pacific-packet-4aa.notion.site/03-2903b027c0d1803ab4add55cec4397da

ユーザーとの対話を重視し、一問一答形式で詳細な情報を収集。

**▶ 3.1 ヒアリング・コンテクスト管理**
https://pacific-packet-4aa.notion.site/3-1-2903b027c0d1816d936bebb1df652ed2

一問一答の進め方、コンテクスト管理、ビジネス背景ヒアリング手法。

**▶ 3.2 ドキュメント生成ガイドライン**
（配下ページを検索中...）

**▶ 3.3 ユーザー配慮・品質確保**
（配下ページを検索中...）

---

## 🔧 技術標準

**04 技術標準**
https://pacific-packet-4aa.notion.site/04-2903b027c0d180f58ecfc1d4eb7df1fb

一貫した品質、堅牢性、保守可能性を確保する技術標準。

**⚠️ 重要な前提:**
- すべての技術標準は、プロジェクト要件・チーム構成・予算・スケジュール・運用方針などの要因により、適用アプローチが変わります
- 「唯一の正解」ではなく、状況に応じて最適な手法を選択してください

---

### 🌐 共通技術標準

**▶ 4.1 共通技術標準**
https://pacific-packet-4aa.notion.site/4-1-2903b027c0d181858554f3e1c2daa793

すべてのプロジェクトに共通する技術標準（コード品質、命名規則、バージョン管理等）。

---

### ☁️ Infrastructure as Code

**▶ 4.2 IaC 共通原則**
https://pacific-packet-4aa.notion.site/4-2-Infrastructure-as-Code-IaC-2903b027c0d1810eacb0f7e5c8c325da

CloudFormation/Terraform両方に共通する基本思想と原則。

- **4.2.2 環境分離戦略**
  https://pacific-packet-4aa.notion.site/4-2-2-2903b027c0d181d786d9d956bc332a96
  dev/stg/prod環境の分離戦略、パラメータ管理。

- **4.2.3 CI/CD統合原則**
  https://pacific-packet-4aa.notion.site/4-2-3-CI-CD-2903b027c0d181cf8142fd5cbf576e61
  IaCのCI/CD統合、自動テスト、dry-run戦略。

**▶ 4.3 AWS CloudFormation規約**
https://pacific-packet-4aa.notion.site/4-3-AWS-CloudFormation-2903b027c0d18128b26cc4b79ab78ce8

AWSネイティブIaCの完全ガイド（✅ Good Example / ❌ Bad Example 多数）。

- **4.3.1 CloudFormation設計原則**
  https://pacific-packet-4aa.notion.site/4-3-1-CloudFormation-2903b027c0d181b48f26d826a48e101d
  論理ID命名規則、日本語制約、モジュール分割原則。

- **4.3.2 Stack設計戦略**
  https://pacific-packet-4aa.notion.site/4-3-2-Stack-2903b027c0d1815c853be79c634775a6
  ネストスタック vs モノリシック、依存関係管理、Change Sets運用。

**▶ 4.4 Terraform規約**
https://pacific-packet-4aa.notion.site/4-4-Terraform-2903b027c0d18114a172d453028b9329

Terraform規約、モジュール設計パターン、状態管理・セキュリティ。

---

### 💻 プログラミング言語規約

**▶ 4.5 Python規約**
https://pacific-packet-4aa.notion.site/4-3-Python-2903b027c0d181c4ac55c112486787e5

PEP 8準拠、型ヒント、Docstring、エラーハンドリング（✅ Good / ❌ Bad 多数）。

**▶ 4.6 Node.js/TypeScript規約**
https://pacific-packet-4aa.notion.site/4-6-Node-js-TypeScript-2903b027c0d181da909aeb48392ce32e

TypeScript型定義、非同期処理パターン、エラーハンドリング（✅ Good / ❌ Bad 多数）。

**▶ 4.7 C# .NET Core規約**
https://pacific-packet-4aa.notion.site/4-7-C-NET-Core-2903b027c0d181e8894acedb08c981c4

C# コーディング規約、async/await、依存性注入パターン（✅ Good / ❌ Bad 多数）。

**▶ 4.8 Go言語規約**
https://pacific-packet-4aa.notion.site/4-8-Go-2903b027c0d1816b85f2ec49aaf1a20b

Effective Go準拠、エラーハンドリング、goroutine/channel並行処理（✅ Good / ❌ Bad 多数）。

---

### 🔒 セキュリティ・運用

**▶ 4.9 セキュリティ・運用基準**
https://pacific-packet-4aa.notion.site/4-9-2903b027c0d181339d0de2d2da27c93c

AWS Well-Architected Framework準拠、シークレット管理、ログ・監視戦略、インシデント対応。

---

## 05 よくある質問・トラブルシューティング

**ページURL:**
https://pacific-packet-4aa.notion.site/05-2903b027c0d180a48c18fc7ff717cb33

---

## 📝 使い方 - フェーズ別実践ガイド

### 🎯 現在のフェーズから探す

**企画フェーズ**
1. `02 開発フェーズ管理` → `2.2 フェーズごとの決定項目` で確認すべき項目をチェック
2. `03 ファシリテーション戦略` → `3.1 ヒアリング・コンテクスト管理` でヒアリング手法を学ぶ
3. ビジネスゴール・ステークホルダー分析を実施

**要件定義フェーズ**
1. `02 開発フェーズ管理` → `2.2 フェーズごとの決定項目` で必須項目をチェック
2. `03 ファシリテーション戦略` → 機能要件・非機能要件のヒアリング手法を確認
3. 制約条件（予算・期間・技術制約）を明確化

**設計フェーズ**
1. `04 技術標準` → `4.2 IaC共通原則` でアーキテクチャパターンを検討
2. CloudFormation or Terraform → 該当規約ページで設計パターンを確認
3. 環境分離戦略（dev/stg/prod）を決定

**実装フェーズ**
1. 使用言語の規約ページを開く（例: `4.5 Python規約`）
2. ✅ Good Example を確認してコーディング
3. ❌ Bad Example で避けるべきパターンをチェック
4. IaC実装時は `4.3 CloudFormation規約` or `4.4 Terraform規約` を参照

**テスト・納品フェーズ**
1. `4.9 セキュリティ・運用基準` でチェックリストを確認
2. `02 開発フェーズ管理` → `2.1 フェーズ遷移ルール` で完了条件を確認
3. dry-run必須（本番デプロイ前に必ず差分確認）

---

### 🔍 技術から探す

**Infrastructure as Code:**
- **CloudFormation** → `4.3 AWS CloudFormation規約` → `4.3.1 設計原則` / `4.3.2 Stack設計戦略`
- **Terraform** → `4.4 Terraform規約`
- **環境分離** → `4.2.2 環境分離戦略`
- **CI/CD** → `4.2.3 CI/CD統合原則`

**プログラミング言語:**
- **Python** → `4.5 Python規約`
- **TypeScript** → `4.6 Node.js/TypeScript規約`
- **C#** → `4.7 C# .NET Core規約`
- **Go** → `4.8 Go言語規約`

**セキュリティ・運用:**
- **シークレット管理** → `4.9 セキュリティ・運用基準`
- **監視・ログ** → `4.9 セキュリティ・運用基準`

---

### ✅ Notionページで必ず確認すること

各技術標準ページには以下が含まれています：

1. **✅ Good Example** - 推奨パターン（コピペ可能）
2. **❌ Bad Example** - 避けるべきアンチパターン
3. **📌 コーディング規約** - 命名規則、構成、制約
4. **🔧 トラブルシューティング** - よくあるエラーと対処法

**実装の流れ:**
```
1. Notionページを開く
   ↓
2. Good Example を確認
   ↓
3. 規約に従って実装
   ↓
4. Bad Example と照らし合わせてセルフレビュー
   ↓
5. チェックリストで最終確認
```

---

## 🔄 自動更新について

**Notionが更新されたら、自動的に最新ルールが適用されます。**

- Notion上で規約が改善・追加されると、次回のプロジェクトから自動的に反映
- ページURLは固定されているため、リンク切れの心配なし
- チーム全体で常に最新の規約を参照可能

---

## ⚠️ 注意事項

- **すべてのURLは永続的:** `https://pacific-packet-4aa.notion.site/` ドメインで公開、ページIDは変更されない限り永続的に使用可能
- **実装時は必ずNotionの最新版を参照:** ローカルにコピーせず、常にNotionを開いて確認すること
- **状況に応じて適用:** 技術標準は「唯一の正解」ではなく、プロジェクト要件に応じて最適な手法を選択すること
