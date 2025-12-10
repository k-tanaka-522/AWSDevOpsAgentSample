# IaC Import 標準（AI活用前提）

**目的**: 緊急対応で作成した管理外リソースを、AIと協力してIaC・設計書に取り込む

---

## 対象シナリオ

- PITR復旧後のRDSインスタンス
- 手動で変更したリソース設定
- コンソールで緊急追加したリソース

---

## 標準プロセス

### 1. AWS CLI でリソース情報を取得

**目的**: 実リソースの設定値をJSON形式で取得

**実施者**: エンジニア（または AI に依頼）

**例**:
```bash
# RDS の場合
aws rds describe-db-instances \
  --db-instance-identifier <リソース識別子> \
  --output json > /tmp/resource.json

# ECS の場合
aws ecs describe-task-definition \
  --task-definition <タスク定義名> \
  --output json > /tmp/resource.json

# Security Group の場合
aws ec2 describe-security-groups \
  --group-ids <sg-xxxxx> \
  --output json > /tmp/resource.json
```

---

### 2. AI に CloudFormation 生成を依頼

**目的**: 取得したJSON情報から CloudFormation テンプレートを生成

**AI への依頼内容**:
```
以下のリソース情報から、CloudFormation テンプレートを生成してください。

[/tmp/resource.json の内容を貼り付け]

要件:
- 既存の CloudFormation スタック構造に合わせる
- パラメーター化すべき値は Parameters に抽出
- 論理IDは既存の命名規則に従う
```

**AI の作業**:
- CloudFormation YAML 生成
- パラメーター抽出
- 既存テンプレートとの整合性確認

---

### 3. CloudFormation Import 実行を AI に依頼

**目的**: 生成したテンプレートで Import Change Set を作成・実行

**AI への依頼内容**:
```
生成した CloudFormation テンプレートで Import を実行してください。

リソース情報:
- リソースタイプ: AWS::RDS::DBInstance
- 論理ID: RDSInstance
- リソース識別子: <リソース識別子>
- スタック名: <スタック名>
```

**AI の作業**:
- Import Change Set 作成コマンド生成
- Change Set レビュー
- 実行コマンド生成
- 実行結果確認

---

### 4. GitHub への取り込みを AI に依頼

**目的**: IaC コードを Git リポジトリに反映

**AI への依頼内容**:
```
以下のファイルを更新して、Git commit してください。

更新対象:
- infra/cloudformation/database.yaml
- infra/parameters/prod.json
- docs/03_基本設計/99_パラメーターシート.md（自動生成）
- docs/03_基本設計/05_データベース設計.md（ADR追記）

コミットメッセージ:
"Import: PITR復旧後のRDSをCloudFormationに取り込み"
```

**AI の作業**:
- ファイル更新
- パラメーターシート自動生成
- ADR 生成（障害内容、対応内容、今後の対策）
- Git commit & push

---

## チェックリスト

AI に以下を確認してもらってください：

- [ ] CloudFormation Import 成功
- [ ] IaC ファイル更新（`infra/cloudformation/*.yaml`, `infra/parameters/*.json`）
- [ ] パラメーターシート更新（`docs/03_基本設計/99_パラメーターシート.md`）
- [ ] 設計書 ADR 追記（`docs/03_基本設計/XX_XXX設計.md`）
- [ ] Git commit & push 完了

---

## AI への依頼例（テンプレート）

### 全体フロー

```
RDS障害が発生し、PITRで復旧しました。
復旧後のRDSインスタンス（myapp-prod-db-restored）を CloudFormation に取り込んでください。

手順:
1. AWS CLI でリソース情報を取得
2. CloudFormation テンプレート生成
3. CloudFormation Import 実行
4. GitHub に取り込み（IaC、パラメーターシート、設計書ADR）

【障害情報】
- 日時: 2025-10-26 14:00
- 事象: RDSストレージ容量不足
- 対応: PITR復旧、ストレージ 50GB → 100GB 拡張
- リソース識別子: myapp-prod-db-restored
```

---

## トラブルシューティング

### Import 失敗時

**AI に依頼**:
```
CloudFormation Import が失敗しました。
以下のエラーメッセージを解析して、対処方法を提案してください。

[エラーメッセージを貼り付け]
```

### Drift 検出時

**AI に依頼**:
```
CloudFormation Import 後に Drift が検出されました。
Drift を解消してください。

[Drift 検出結果を貼り付け]
```

---

## まとめ

**AIと協力して進める前提**:
- AWS CLI でリソース情報取得
- AI に CloudFormation 生成を依頼
- AI に Import 実行を依頼
- AI に GitHub 取り込みを依頼

**所要時間**: 約10-15分（AIと協力）
