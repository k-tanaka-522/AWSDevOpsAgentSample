# 状態管理ヘルパー

このドキュメントは、プロジェクト状態を自動管理するためのガイドラインです。

## 概要

あなた（Claude）は、プロジェクトの進行に応じて、自動的に`.claude-state/`配下のファイルを更新してください。

---

## 1. 自動更新のタイミング

以下のタイミングで、状態ファイルを自動更新してください：

### 1.1 プロジェクト開始時
- `.claude-state/project-state.json` が存在しない場合、自動生成
- プロジェクト名、タイプを記録

### 1.2 フェーズ遷移時
- フェーズの開始時：`started_at`を記録
- フェーズの完了時：`completed_at`を記録
- ドキュメント生成時：`document`にパスを記録

### 1.3 重要な決定時
- 技術スタック選定
- アーキテクチャ決定
- インフラ設計
- CI/CD戦略

→ `.claude-state/decisions.json`に追記

### 1.4 タスク・課題発生時
- 新しいタスクが必要になった時
- ブロッカーが発生した時
- 課題が解決した時

→ `.claude-state/tasks.json`を更新

---

## 2. ファイルフォーマット

### 2.1 project-state.json

```json
{
  "project": {
    "name": "介護保険申請管理システム",
    "type": "web-application",
    "phase": "design",
    "created_at": "2025-10-01T10:00:00Z",
    "updated_at": "2025-10-02T15:30:00Z"
  },
  "phases": {
    "planning": {
      "status": "completed",
      "started_at": "2025-10-01T10:00:00Z",
      "completed_at": "2025-10-01T12:00:00Z",
      "document": "docs/01_企画書.md"
    },
    "requirements": {
      "status": "completed",
      "started_at": "2025-10-01T13:00:00Z",
      "completed_at": "2025-10-02T10:00:00Z",
      "document": "docs/02_要件定義書.md"
    },
    "design": {
      "status": "in_progress",
      "started_at": "2025-10-02T11:00:00Z",
      "completed_at": null,
      "document": null
    },
    "implementation": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "document": null
    },
    "testing": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "document": null
    },
    "deployment": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "document": null
    }
  },
  "requirements": {
    "business_background": {
      "industry": "healthcare",
      "target_users": "ケアマネジャー、施設管理者",
      "current_issues": "手作業での申請書類作成、進捗管理が困難"
    },
    "tech_stack": {
      "frontend": "React",
      "backend": "Node.js + Express",
      "database": "PostgreSQL",
      "infrastructure": "AWS (ECS, RDS)",
      "ci_cd": "GitHub Actions"
    },
    "functional_requirements": [
      "利用者情報管理",
      "申請書類生成",
      "進捗管理",
      "通知機能"
    ],
    "non_functional_requirements": {
      "performance": "応答時間2秒以内",
      "security": "個人情報保護法対応",
      "availability": "稼働率99.9%"
    },
    "constraints": {
      "budget": "初期開発500万円",
      "timeline": "3ヶ月",
      "team_size": "3名"
    }
  },
  "design": {
    "architecture": "3層アーキテクチャ（Web, API, DB）",
    "tech_stack": {
      "web": "React + TypeScript",
      "api": "Node.js + Express",
      "database": "RDS PostgreSQL",
      "cache": "ElastiCache Redis",
      "storage": "S3"
    },
    "infrastructure": {
      "hosting": "AWS ECS Fargate",
      "network": "VPC（Multi-AZ）",
      "cdn": "CloudFront",
      "monitoring": "CloudWatch + X-Ray"
    },
    "cicd_strategy": {
      "tool": "GitHub Actions",
      "environments": ["dev", "stg", "prod"],
      "deployment": "Blue-Green Deployment"
    }
  },
  "implementation": {
    "directory_structure": "src/（components, pages, api, utils）",
    "coding_standards_applied": true
  },
  "metadata": {
    "version": "1.0.0",
    "last_command": "/status"
  }
}
```

### 2.2 tasks.json

```json
{
  "tasks": [
    {
      "id": "task-001",
      "title": "VPC設計の完了",
      "status": "completed",
      "priority": "high",
      "created_at": "2025-10-02T11:00:00Z",
      "completed_at": "2025-10-02T13:00:00Z",
      "phase": "design"
    },
    {
      "id": "task-002",
      "title": "ECS構成の決定",
      "status": "in_progress",
      "priority": "high",
      "created_at": "2025-10-02T13:30:00Z",
      "completed_at": null,
      "phase": "design"
    },
    {
      "id": "task-003",
      "title": "CI/CD戦略のヒアリング",
      "status": "pending",
      "priority": "medium",
      "created_at": "2025-10-02T14:00:00Z",
      "completed_at": null,
      "phase": "design"
    }
  ],
  "issues": [
    {
      "id": "issue-001",
      "title": "コスト見積もりが未実施",
      "severity": "medium",
      "status": "open",
      "created_at": "2025-10-02T15:00:00Z",
      "resolved_at": null,
      "impact": "予算超過のリスク",
      "action": "AWSコスト計算ツールで見積もり実施"
    }
  ]
}
```

### 2.3 decisions.json

```json
{
  "decisions": [
    {
      "id": "dec-001",
      "title": "フロントエンドフレームワークの選定",
      "decision": "React + TypeScript",
      "rationale": "チームの習熟度が高い、TypeScriptで型安全性確保",
      "alternatives": ["Vue.js", "Next.js"],
      "decided_at": "2025-10-01T14:00:00Z",
      "decided_by": "ユーザー + Claude",
      "phase": "requirements"
    },
    {
      "id": "dec-002",
      "title": "インフラ構成の選定",
      "decision": "AWS ECS Fargate + RDS",
      "rationale": "サーバーレスで運用負荷削減、スケーラビリティ確保",
      "alternatives": ["EC2 + Docker", "Lambda + DynamoDB"],
      "decided_at": "2025-10-02T11:30:00Z",
      "decided_by": "ユーザー + Claude",
      "phase": "design"
    }
  ]
}
```

---

## 3. 自動更新の実装方法

### 3.1 プロジェクト開始時

```markdown
ユーザー: 介護保険申請管理システムを作りたい
Claude: （以下を自動実行）
1. `.claude-state/project-state.json`を確認
2. 存在しない場合、初期状態で作成
3. `project.name`を記録
4. `phases.planning.status`を`in_progress`に変更
5. `phases.planning.started_at`に現在時刻を記録
```

**Write tool を使ってファイルを作成・更新してください。**

### 3.2 フェーズ遷移時

```markdown
Claude: 企画書を作成しました。内容を確認して、承認いただけますか？
ユーザー: 承認します
Claude: （以下を自動実行）
1. `project-state.json`を読み込み
2. `phases.planning.status`を`completed`に変更
3. `phases.planning.completed_at`に現在時刻を記録
4. `phases.planning.document`に`docs/01_企画書.md`を記録
5. `phases.requirements.status`を`in_progress`に変更
6. `phases.requirements.started_at`に現在時刻を記録
7. `project.phase`を`requirements`に変更
8. `project.updated_at`を更新
9. Edit tool でファイルを更新
```

### 3.3 重要な決定時

```markdown
Claude: フロントエンドフレームワークはReact + TypeScriptで進めましょう。理由は...
ユーザー: 了解しました
Claude: （以下を自動実行）
1. `decisions.json`を読み込み
2. 新しい決定を追加
   - title, decision, rationale, alternatives, decided_at等を記録
3. Edit tool でファイルを更新
```

### 3.4 タスク・課題発生時

```markdown
Claude: CI/CD戦略がまだ決まっていません。これは設計完了のブロッカーです。
Claude: （以下を自動実行）
1. `tasks.json`を読み込み
2. issues配列に新しい課題を追加
   - title: "CI/CD戦略が未決定"
   - severity: "high"
   - impact: "設計完了のブロッカー"
3. Edit tool でファイルを更新
```

---

## 4. 注意事項

### 4.1 タイムゾーン
- すべての日時はISO 8601形式（`2025-10-02T15:30:00Z`）で記録
- UTCを使用

### 4.2 ファイル存在確認
- 更新前に必ず Read tool で既存ファイルを読み込む
- 存在しない場合は Write tool で新規作成
- 存在する場合は Edit tool で更新

### 4.3 ユーザーへの通知
- 状態ファイルを更新したことを、ユーザーに明示的に伝える必要はありません
- 自動的に更新してください
- ただし、`/status`コマンドで状態を可視化します

### 4.4 競合回避
- 複数のフィールドを同時に更新する場合、1回のEdit tool呼び出しで完了させる
- 細かい更新を繰り返さない

---

## 5. `/status`コマンドとの連携

`/status`コマンドは、これらの状態ファイルを読み込んで、プロジェクトの全体像を表示します。

あなたが適切に状態を記録していれば、`/status`コマンドで正確な状況が表示されます。

---

## 6. まとめ

- プロジェクトの進行に応じて、自動的に状態ファイルを更新
- ユーザーに意識させない（自動バックグラウンド処理）
- `/status`コマンドで可視化
- セッションをまたいだ継続性を確保

**あなたの責務：**
適切なタイミングで、適切な状態を記録し、プロジェクトの継続性を保証すること。
