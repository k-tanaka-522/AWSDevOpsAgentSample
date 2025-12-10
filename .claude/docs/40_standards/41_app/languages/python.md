# Python コーディング規約

## 基本方針

- **PEP 8準拠**
- **型ヒント必須**（Python 3.10+）
- **非同期処理推奨**（I/O処理）

---

## プロジェクト構成

```
myapp/
├── src/
│   ├── __init__.py
│   ├── api/          # FastAPI
│   ├── services/     # ビジネスロジック
│   ├── models/       # SQLAlchemy models
│   └── utils/        # ユーティリティ
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── requirements.txt
└── pyproject.toml
```

---

## コーディング規約

### コメント規約

**全言語共通のコメント規約**: `.claude/agents/coder/AGENT.md` の「💬 コメント規約」セクションを参照

**必須事項**:
- すべての関数/メソッドにdocstring（日本語）
- 「目的・理由」「影響範囲」「前提条件」を記載
- AI協業を前提としたコンテキスト明記

---

### 型ヒント

```python
# ✅ Good
def get_user(user_id: int) -> User | None:
    return db.query(User).filter_by(id=user_id).first()

# ❌ Bad
def get_user(user_id):  # 型ヒントなし
    return db.query(User).filter_by(id=user_id).first()
```

### 非同期処理

```python
# ✅ Good
async def get_user(user_id: int) -> User | None:
    return await db.execute(select(User).where(User.id == user_id))

# ❌ Bad（I/O処理なのに同期）
def get_user(user_id: int) -> User | None:
    return db.execute(select(User).where(User.id == user_id))
```

### エラーハンドリング

```python
# ✅ Good
class UserNotFoundError(Exception):
    pass

def get_user(user_id: int) -> User:
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    return user

# ❌ Bad
def get_user(user_id: int) -> User | None:
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return None  # エラーか空か区別できない
    return user
```

---

## テスト

- **フレームワーク**: pytest
- **カバレッジ目標**: 80%以上
- **モック**: unittest.mock

```python
# テスト例
def test_get_user_success():
    # Arrange
    user = User(id=1, name="Test")

    # Act
    result = get_user(1)

    # Assert
    assert result.id == 1
```

---

## 依存関係管理

```bash
# requirements.txt
fastapi==0.109.0
sqlalchemy==2.0.25
pydantic==2.5.0

# インストール
pip install -r requirements.txt
```

---

**参照**: `.claude/docs/10_facilitation/2.4_実装フェーズ/2.4.5_言語別コーディング規約適用/2.4.5.1_Python規約適用/`
