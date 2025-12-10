# SRE レビューチェックリスト（インフラ設計書）

## 観点: 運用・実装可能性

### 必須チェック項目

- [ ] **実装可能性**: IaCで実現可能な設計か
- [ ] **運用性**: 監視、アラート、復旧手順の考慮があるか
- [ ] **コスト最適化**: 過剰なリソースがないか
- [ ] **セキュリティ**: セキュリティ設計が妥当か
- [ ] **可用性**: Multi-AZ、冗長構成が適切か

### 追加チェック項目

- [ ] **IaC実装方針**: CloudFormation/Terraform での実装イメージが明確か
- [ ] **デプロイ戦略**: Blue/Green、Rolling Update などの方針
- [ ] **バックアップ・リストア**: 復旧手順が明確か
- [ ] **スケーリング戦略**: Auto Scaling の設定方針

### 技術標準参照

確認すべき技術標準:
- `.claude/docs/40_standards/42_infra/` - インフラ技術標準
- `.claude/docs/40_standards/42_infra/iac/cloudformation.md` - CloudFormation標準
- `.claude/docs/40_standards/42_infra/iac/terraform.md` - Terraform標準

### 判定基準

| 結果 | 条件 |
|------|------|
| **approved** | 全ての必須項目が pass |
| **approved_with_comments** | 必須項目は pass、追加項目に warn あり |
| **rejected** | 必須項目に fail あり |
