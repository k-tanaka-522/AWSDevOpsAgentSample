# Infra-Architect レビューチェックリスト（IaC）

## 観点: 設計整合・ベストプラクティス

### 必須チェック項目

- [ ] **設計書との整合性**: インフラ設計書の通りに実装されているか
- [ ] **技術標準準拠**:
  - CloudFormation: `.claude/docs/40_standards/42_infra/iac/cloudformation.md`
  - Terraform: `.claude/docs/40_standards/42_infra/iac/terraform.md`
- [ ] **ディレクトリ構造**: stacks/templates/parameters の分離が適切か
- [ ] **パラメータ化**: 環境差分が適切に分離されているか
- [ ] **セキュリティ**: Security Groups、暗号化、IAM権限が適切か

### 追加チェック項目

- [ ] **ネストスタック/モジュール**: 再利用性が考慮されているか
- [ ] **タグ付け**: 必須タグが設定されているか
- [ ] **命名規則**: リソース名が規則に従っているか
- [ ] **ベストプラクティス**: AWS/Terraform のベストプラクティスに準拠しているか

### CloudFormation 固有チェック

- [ ] DeletionPolicy が適切に設定されているか
- [ ] UpdatePolicy が適切に設定されているか
- [ ] Outputs が適切に定義されているか

### Terraform 固有チェック

- [ ] state 管理が適切か（S3 + DynamoDB）
- [ ] provider version が固定されているか
- [ ] data source の活用が適切か

### 判定基準

| 結果 | 条件 |
|------|------|
| **approved** | 全ての必須項目が pass |
| **approved_with_comments** | 必須項目は pass、追加項目に warn あり |
| **rejected** | 必須項目に fail あり |
