# 技術標準ドキュメント

aiDevフレームワークで使用する技術標準を定義しています。

## ディレクトリ構成

```
40_standards/
├── 41_app/              # アプリケーション設計標準
│   ├── languages/       # プログラミング言語標準
│   ├── frameworks/      # フレームワーク標準
│   ├── api_design.md    # API設計標準
│   ├── database.md      # データベース設計標準
│   └── uiux.md          # UI/UX設計標準
│
├── 42_infra/            # インフラ設計標準
│   ├── iac/             # Infrastructure as Code標準
│   ├── cicd/            # CI/CD標準
│   └── testing/         # インフラテスト標準
│
└── 49_common/           # 共通標準
    └── security.md      # セキュリティ標準
```

## 41_app/ - アプリケーション設計標準

### languages/ - プログラミング言語標準

| ファイル | 対象 | 担当エージェント |
|---------|------|----------------|
| [python.md](41_app/languages/python.md) | Python 3.11+ | Coder |
| [typescript.md](41_app/languages/typescript.md) | TypeScript 5.0+ | Coder |
| [csharp.md](41_app/languages/csharp.md) | C# 12 (.NET 8) | Coder |
| [go.md](41_app/languages/go.md) | Go 1.21+ | Coder |

### frameworks/ - フレームワーク標準

| ファイル | 対象 | 担当エージェント |
|---------|------|----------------|
| [react_nextjs.md](41_app/frameworks/react_nextjs.md) | React 18 + Next.js 14 | Coder |
| [flutter.md](41_app/frameworks/flutter.md) | Flutter 3.x | Coder |

### その他アプリケーション標準

| ファイル | 対象 | 担当エージェント |
|---------|------|----------------|
| [api_design.md](41_app/api_design.md) | REST/GraphQL API設計 | Architect, Coder |
| [database.md](41_app/database.md) | RDB/NoSQL設計 | Architect, Coder |
| [uiux.md](41_app/uiux.md) | UI/UXデザイン | Designer |

## 42_infra/ - インフラ設計標準

### iac/ - Infrastructure as Code標準

| ファイル | 対象 | 担当エージェント |
|---------|------|----------------|
| [cloudformation.md](42_infra/iac/cloudformation.md) | AWS CloudFormation | Architect, SRE |
| [terraform.md](42_infra/iac/terraform.md) | Terraform | Architect, SRE |
| [iac-import.md](42_infra/iac/iac-import.md) | 既存インフラのIaC化 | SRE |

### cicd/ - CI/CD標準

| ファイル | 対象 | 担当エージェント |
|---------|------|----------------|
| [github_actions.md](42_infra/cicd/github_actions.md) | GitHub Actions | SRE |
| [cicd-security.md](42_infra/cicd/cicd-security.md) | CI/CDセキュリティ | SRE |

### testing/ - インフラテスト標準

| ファイル | 対象 | 担当エージェント |
|---------|------|----------------|
| [infra-test-structure.md](42_infra/testing/infra-test-structure.md) | インフラテスト計画・実施 | QA, SRE |

## 49_common/ - 共通標準

| ファイル | 対象 | 担当エージェント |
|---------|------|----------------|
| [security.md](49_common/security.md) | セキュリティ全般 | 全エージェント |

## 使い方

### エージェント別参照ガイド

**Architect（設計）**
- アプリ設計: `41_app/api_design.md`, `41_app/database.md`
- インフラ設計: `42_infra/iac/`配下
- セキュリティ: `49_common/security.md`

**Coder（実装）**
- 言語標準: `41_app/languages/` 配下
- フレームワーク標準: `41_app/frameworks/` 配下
- セキュリティ: `49_common/security.md`

**Designer（UI/UX）**
- UI/UX標準: `41_app/uiux.md`

**SRE（インフラ運用）**
- IaC標準: `42_infra/iac/` 配下
- CI/CD標準: `42_infra/cicd/` 配下
- セキュリティ: `49_common/security.md`

**QA（品質保証）**
- アプリテスト標準: 各言語標準のテストセクション
- インフラテスト標準: `42_infra/testing/infra-test-structure.md`
- セキュリティ: `49_common/security.md`

## 更新履歴

- 2025-11-27: インフラテスト標準を追加
- 2025-11-09: ディレクトリ構造を再編成（アプリ/インフラ/共通に分離）
- 2025-11-08: UI/UX標準を追加
- 2025-11-07: コメント規約を追加
