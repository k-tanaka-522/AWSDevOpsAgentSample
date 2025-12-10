# /check-code コマンド

コード品質レビューを実施し、リファクタリング提案を行うコマンドです。

## 目的

- コード構造の適切性を評価
- リファクタリングが必要な箇所を特定
- ベストプラクティスへの準拠を確認
- 効率性・保守性の改善提案

## 実行フロー

### ステップ1: 一問一答ヒアリング（引数なしの場合）

#### 質問1: チェックの目的

```
/check-code を実行しました。

【質問1: チェックの目的】
どんなレビューをしますか？

A: 全体的な品質チェック（構造、ベストプラクティス、保守性など）
B: 特定の困りごとがある（詳しく教えてください）
```

**ユーザーが A を選択した場合**:
- 質問3（チェック範囲）へ進む

**ユーザーが B を選択した場合**:
- 質問2へ進む

---

#### 質問2: 困りごとの内容（B選択時のみ）

```
【質問2: 困りごとの内容】
どんな問題がありますか？

例:
- パフォーマンスが遅い
- セキュリティが心配
- テストが書きにくい
- コードが読みにくい
- エラーハンドリングが不安
- その他（具体的に教えてください）
```

ユーザーの回答を記録し、この困りごとを**最優先の観点**としてチェックします。

---

#### 質問3: チェック範囲

```
【質問3: チェック範囲】
どこをチェックしますか？

A: 最近変更したファイル（Git diff 基準: main...HEAD）
B: プロジェクト全体（該当ディレクトリすべて）
C: 特定のファイル/ディレクトリを指定
```

**A を選択した場合**:
```bash
git diff --name-only main...HEAD
```
で変更ファイルを取得し、プロジェクトタイプに応じたディレクトリ（infra/, src/, app/ など）に絞り込み。

**B を選択した場合**:
プロジェクトタイプを自動判定し、該当ディレクトリ配下のすべてのコードファイルをチェック。

**C を選択した場合**:
```
どのファイル/ディレクトリをチェックしますか？
例: src/services/user.ts
例: infra/cloudformation/stacks/01-network/
```

---

### ステップ2: プロジェクトタイプの自動判定

以下の条件でプロジェクトタイプを判定し、対象ディレクトリを決定：

```javascript
// インフラプロジェクト
if (exists('infra/cloudformation/') || exists('infra/terraform/')) {
  projectType = 'infrastructure';
  targetDirs = ['infra/cloudformation/', 'infra/terraform/'];
  standards = ['45_cloudformation.md', '46_terraform.md', '49_security.md'];
}

// アプリケーションプロジェクト
if (exists('src/') || exists('app/')) {
  projectType = 'application';
  targetDirs = ['src/', 'app/', 'tests/'];
  // package.json, tsconfig.json などから言語を判定
  standards = ['41_python.md', '42_typescript.md', '43_csharp.md', '44_go.md'];
}

// フルスタック
if (infrastructure && application) {
  projectType = 'fullstack';
  targetDirs = [...infrastructureDirs, ...applicationDirs];
  standards = [...infrastructureStandards, ...applicationStandards];
}
```

---

### ステップ3: チェック実行

以下の順序でチェックを実施：

#### 3-1. 技術標準の確認

`.claude/docs/40_standards/` から該当する技術標準を読み込む。

例:
- TypeScript プロジェクト → `42_typescript.md`
- CloudFormation → `45_cloudformation.md`
- セキュリティ → `49_security.md`

#### 3-2. 設計書の確認（背景理解）

`docs/03_基本設計/` などから設計書を読み込み、以下を理解：
- なぜこの技術選定をしたのか
- どんなアーキテクチャ方針なのか
- 技術標準を作成した際の背景（Web検索結果が反映されている可能性）

#### 3-3. コードの分析

対象ファイルを読み込み、以下の観点でチェック：

**基本チェック項目（必須）**:
- ✅ コード構造の適切性
  - 関数の長さ（推奨: 50行以内）
  - クラス設計（単一責任の原則）
  - ネストの深さ（推奨: 3階層以内）
- ✅ 技術標準への準拠
  - `.claude/docs/40_standards/` の規約に準拠しているか
- ✅ ベストプラクティス違反
  - 設計書・技術標準で言及されている方針との整合性

**追加チェック項目**:
- ✅ セキュリティ
  - ハードコードされた機密情報
  - SQLインジェクション、XSS などの脆弱性
  - 認証・認可の不備
- ✅ パフォーマンス
  - N+1 クエリ
  - 不要なループ処理
  - メモリリーク可能性
- ✅ テスタビリティ
  - テストしにくい構造
  - モックしにくい依存関係
- ✅ 保守性
  - マジックナンバー
  - コメント不足
  - ネーミングの分かりにくさ
- ✅ エラーハンドリング
  - 例外処理の不備
  - エラーメッセージの不適切さ
  - リトライ処理の欠如

**ユーザーの困りごとがある場合**:
- その困りごとに関連する項目を**最優先**でチェック
- 例: 「パフォーマンスが遅い」→ パフォーマンス観点を深掘り

#### 3-4. 必要に応じてWeb検索

以下の場合にWeb検索を実施：

**優先度1: ユーザーの困りごとに直結する情報**
```
困りごと: 「パフォーマンスが遅い」
→ "TypeScript performance optimization 2025"
→ "async/await performance best practices"
```

**優先度2: ベストプラクティスの確認が必要な場合**
```
コード分析中に「もっと良い方法があるかも？」と判断した場合
→ "CloudFormation nested stacks best practices 2025"
→ "TypeScript error handling patterns 2025"
```

**検索結果の活用**:
- 最新のベストプラクティスと照合
- 設計書・技術標準に反映されていない新しい知見があればそれを指摘

---

### ステップ4: リファクタリング提案（構造的説明形式）

**提案フォーマット**:

```markdown
## `/check-code` レビュー結果

### チェック対象
- 範囲: [最近変更したファイル / プロジェクト全体 / 指定ファイル]
- プロジェクトタイプ: [infrastructure / application / fullstack]
- 対象ファイル数: N ファイル

---

### 📊 総合評価

- ✅ 良好: X 項目
- ⚠️ 改善推奨: Y 項目
- 🚨 要対応: Z 項目

---

### 🚨 要対応（優先度: 高）

#### 📄 src/services/user.ts

**問題: `createUser()` 関数が100行（単一責任の原則違反）**

【リファクタリング内容】
1. `validateUserInput()` に分離 → 行15-25のバリデーション部分
2. `saveUserToDatabase()` に分離 → 行27-35のDB処理
3. `sendWelcomeEmail()` に分離 → 行37-45のメール送信

【分割後のメイン関数イメージ】
```typescript
function createUser(data) {
  validateUserInput(data);
  const user = saveUserToDatabase(data);
  sendWelcomeEmail(user);
  return user;
}
```

【理由】
- 単一責任の原則に違反（バリデーション・永続化・通知を1関数で実施）
- テストが困難（3つの関心事をモックする必要）
- 再利用性が低い

【参考】
- 技術標準: `.claude/docs/40_standards/42_typescript.md` - 関数は50行以内推奨
- ベストプラクティス: [Web検索結果があれば記載]

---

#### 📄 infra/cloudformation/stacks/01-network/main.yaml

**問題: パラメーター値がハードコード**

【リファクタリング内容】
- 行12-15の CIDR ブロック値を `parameters/dev.json` に移動
- `Ref: VpcCidr` でパラメーター参照に変更

【修正後のイメージ】
```yaml
VPC:
  Type: AWS::EC2::VPC
  Properties:
    CidrBlock: !Ref VpcCidr  # パラメーター参照
```

【理由】
- 環境差分を集約する方針（`parameters/*.json`）に違反
- dev/stg/prd で値を変える場合にテンプレート修正が必要になる

【参考】
- 技術標準: `.claude/docs/40_standards/45_cloudformation.md` - パラメーター分離必須

---

### ⚠️ 改善推奨（優先度: 中）

[同様のフォーマットで列挙]

---

### ✅ 良好（問題なし）

以下のファイルは問題ありませんでした：
- src/utils/logger.ts
- infra/cloudformation/templates/network/vpc-and-igw.yaml

---

### 📝 次のアクション

リファクタリングを実施しますか？

**承認いただければ、AIが自動で修正します。**
- 修正後は Git diff で変更内容を確認できます
- 問題があれば `git restore` で元に戻せます

承認する場合は「OK」または「実施して」とお伝えください。
一部だけ修正する場合は「user.ts だけ修正して」のように指定してください。
```

---

### ステップ5: ユーザー承認待ち

提案を提示したら、ユーザーの承認を待ちます。

**承認パターン**:
- 「OK」「実施して」「すべて修正して」→ すべてのリファクタリングを実行
- 「user.ts だけ修正して」→ 指定されたファイルのみ修正
- 「パフォーマンス関連だけ」→ 特定カテゴリのみ修正
- 「いったん見送り」→ 修正せずに終了

---

### ステップ6: リファクタリング実行（承認後）

承認されたリファクタリングを実行：

1. 提案内容に基づいてコードを修正
2. 修正結果を報告
3. Git diff で確認を促す

```markdown
## リファクタリング完了

以下のファイルを修正しました：

✅ src/services/user.ts
  - createUser() を3つの関数に分割
  - validateUserInput(), saveUserToDatabase(), sendWelcomeEmail() を追加

✅ infra/cloudformation/stacks/01-network/main.yaml
  - CIDR ブロックをパラメーター参照に変更

---

### 確認方法

```bash
git diff
```

で変更内容を確認してください。

問題があれば以下で元に戻せます：
```bash
git restore src/services/user.ts
git restore infra/cloudformation/stacks/01-network/main.yaml
```
```

---

## 引数付き実行（将来拡張）

将来的に以下のような引数付き実行も検討：

```bash
# 特定ファイルを指定
/check-code src/services/user.ts

# 特定の観点でチェック
/check-code --focus=performance

# 範囲を指定
/check-code --scope=recent  # 最近変更したファイル
/check-code --scope=all     # プロジェクト全体
```

現時点では引数なし（一問一答ヒアリング）のみサポート。

---

## 注意事項

1. **Web検索は必要最小限**
   - まず技術標準・設計書を確認
   - 本当に必要な場合のみWeb検索

2. **ユーザーの困りごとを最優先**
   - 全体チェックよりも困りごと解決を優先
   - 困りごとに関連する項目を深掘り

3. **提案は簡潔に**
   - Git diff で確認できるから全文不要
   - 構造的説明 + 最小限のコード例

4. **承認なしで修正しない**
   - 必ずユーザーの承認を得てから実行
   - 部分的な承認も受け付ける
