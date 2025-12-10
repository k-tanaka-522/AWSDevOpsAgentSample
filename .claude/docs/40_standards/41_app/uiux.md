# UI/UX 技術標準

## 基本方針

- **ユーザーファースト**: 使いやすさを最優先
- **アクセシビリティ**: WCAG 2.1 AA準拠
- **一貫性**: デザインシステムに従う
- **レスポンシブ**: PC・タブレット対応

---

## 技術スタック

### 推奨フレームワーク

**Tailwind CSS + daisyUI** (推奨)

```html
<!-- CDN読み込み（プロトタイプ用） -->
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.6.0/dist/full.min.css" rel="stylesheet" />
<script src="https://cdn.tailwindcss.com"></script>
```

**理由**:
- ✅ コンポーネントがすぐ使える
- ✅ プロトタイプ → 実装への移行が楽
- ✅ 日本の行政システムに適したデザイン

---

## デザインシステム

### カラーパレット

#### Primary（メイン）
- **青**: `#3B82F6` (Tailwind blue-500)
- 用途: メインボタン、リンク、アクティブ状態

#### Secondary（サブ）
- **グレー**: `#6B7280` (Tailwind gray-500)
- 用途: サブボタン、無効状態

#### Success（成功）
- **緑**: `#10B981` (Tailwind green-500)
- 用途: 成功メッセージ、完了状態

#### Warning（警告）
- **黄**: `#F59E0B` (Tailwind yellow-500)
- 用途: 注意メッセージ

#### Danger（危険）
- **赤**: `#EF4444` (Tailwind red-500)
- 用途: 削除ボタン、エラーメッセージ

#### Background（背景）
- **明るいグレー**: `#F9FAFB` (Tailwind gray-50)
- 用途: ページ背景

### Tailwind クラス例

```html
<!-- Primary ボタン -->
<button class="btn btn-primary">保存</button>

<!-- Success メッセージ -->
<div class="alert alert-success">
  保存しました
</div>

<!-- Danger ボタン -->
<button class="btn btn-error">削除</button>
```

---

### タイポグラフィ

#### フォント
- **和文**: Noto Sans JP
- **欧文**: Inter

#### サイズ

| 用途 | サイズ | Tailwind クラス | 例 |
|------|--------|-----------------|-----|
| 大見出し | 2rem (32px) | `text-3xl` | ページタイトル |
| 中見出し | 1.5rem (24px) | `text-2xl` | セクションタイトル |
| 小見出し | 1.25rem (20px) | `text-xl` | サブセクション |
| 本文 | 1rem (16px) | `text-base` | 通常テキスト |
| 小 | 0.875rem (14px) | `text-sm` | 補足テキスト |

#### フォントウェイト

| 用途 | ウェイト | Tailwind クラス |
|------|----------|-----------------|
| 見出し | Bold (700) | `font-bold` |
| 本文 | Regular (400) | `font-normal` |
| 補足 | Regular (400) | `font-normal` |

---

### 余白（Spacing）

#### 基本単位: 0.25rem (4px)

| サイズ | 値 | Tailwind クラス | 用途 |
|--------|-----|-----------------|------|
| XS | 0.25rem (4px) | `p-1`, `m-1` | 最小余白 |
| S | 0.5rem (8px) | `p-2`, `m-2` | 小余白 |
| M | 1rem (16px) | `p-4`, `m-4` | 標準余白 |
| L | 2rem (32px) | `p-8`, `m-8` | 大余白 |
| XL | 3rem (48px) | `p-12`, `m-12` | 特大余白 |

#### 推奨パターン

```html
<!-- カード -->
<div class="card bg-base-100 shadow-xl">
  <div class="card-body">  <!-- デフォルト: p-8 -->
    コンテンツ
  </div>
</div>

<!-- セクション間 -->
<section class="mb-8">
  セクション1
</section>
<section class="mb-8">
  セクション2
</section>
```

---

## コンポーネント

### ボタン

#### 基本ボタン

```html
<!-- Primary -->
<button class="btn btn-primary">保存</button>

<!-- Secondary -->
<button class="btn btn-secondary">キャンセル</button>

<!-- Danger -->
<button class="btn btn-error">削除</button>

<!-- Ghost（背景なし） -->
<button class="btn btn-ghost">戻る</button>
```

#### サイズ

```html
<!-- Large -->
<button class="btn btn-lg btn-primary">大きいボタン</button>

<!-- Default -->
<button class="btn btn-primary">通常ボタン</button>

<!-- Small -->
<button class="btn btn-sm btn-primary">小さいボタン</button>
```

#### 無効状態

```html
<button class="btn btn-primary" disabled>無効</button>
```

---

### フォーム

#### テキスト入力

```html
<div class="form-control">
  <label class="label">
    <span class="label-text">氏名 <span class="text-error">*</span></span>
  </label>
  <input type="text" placeholder="山田 太郎" class="input input-bordered" required />
  <label class="label">
    <span class="label-text-alt">姓と名をスペースで区切ってください</span>
  </label>
</div>
```

#### セレクトボックス

```html
<div class="form-control">
  <label class="label">
    <span class="label-text">都道府県</span>
  </label>
  <select class="select select-bordered">
    <option disabled selected>選択してください</option>
    <option>東京都</option>
    <option>大阪府</option>
  </select>
</div>
```

#### チェックボックス

```html
<div class="form-control">
  <label class="label cursor-pointer">
    <span class="label-text">利用規約に同意する</span>
    <input type="checkbox" class="checkbox" />
  </label>
</div>
```

---

### テーブル

```html
<div class="overflow-x-auto">
  <table class="table table-zebra w-full">
    <thead>
      <tr>
        <th>ID</th>
        <th>氏名</th>
        <th>メールアドレス</th>
        <th>操作</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>1</td>
        <td>田中 太郎</td>
        <td>tanaka@example.com</td>
        <td>
          <button class="btn btn-sm btn-primary">詳細</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

---

### アラート

```html
<!-- Success -->
<div class="alert alert-success">
  <svg>...</svg>
  <span>保存しました</span>
</div>

<!-- Error -->
<div class="alert alert-error">
  <svg>...</svg>
  <span>エラーが発生しました</span>
</div>

<!-- Warning -->
<div class="alert alert-warning">
  <svg>...</svg>
  <span>注意: 保存されていない変更があります</span>
</div>
```

---

### モーダル

```html
<!-- モーダルボタン -->
<button class="btn" onclick="my_modal.showModal()">モーダルを開く</button>

<!-- モーダル -->
<dialog id="my_modal" class="modal">
  <div class="modal-box">
    <h3 class="font-bold text-lg">確認</h3>
    <p class="py-4">本当に削除しますか？</p>
    <div class="modal-action">
      <form method="dialog">
        <button class="btn btn-ghost">キャンセル</button>
        <button class="btn btn-error">削除</button>
      </form>
    </div>
  </div>
</dialog>
```

---

## レイアウト

### ページレイアウト

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ページタイトル</title>
  <link href="https://cdn.jsdelivr.net/npm/daisyui@4.6.0/dist/full.min.css" rel="stylesheet" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
  <!-- ヘッダー -->
  <div class="navbar bg-base-100 shadow-md">
    <div class="flex-1">
      <a class="btn btn-ghost text-xl">アプリ名</a>
    </div>
    <div class="flex-none">
      <ul class="menu menu-horizontal px-1">
        <li><a>メニュー1</a></li>
        <li><a>メニュー2</a></li>
      </ul>
    </div>
  </div>

  <!-- メインコンテンツ -->
  <div class="container mx-auto p-8">
    <h1 class="text-3xl font-bold mb-6">ページタイトル</h1>

    <!-- コンテンツ -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        コンテンツ
      </div>
    </div>
  </div>

  <!-- フッター -->
  <footer class="footer footer-center p-4 bg-base-300 text-base-content mt-8">
    <aside>
      <p>Copyright © 2025 - All rights reserved</p>
    </aside>
  </footer>
</body>
</html>
```

---

### グリッドレイアウト

```html
<!-- 2カラム -->
<div class="grid grid-cols-2 gap-4">
  <div class="card bg-base-100 shadow-xl">カラム1</div>
  <div class="card bg-base-100 shadow-xl">カラム2</div>
</div>

<!-- 3カラム -->
<div class="grid grid-cols-3 gap-4">
  <div class="card bg-base-100 shadow-xl">カラム1</div>
  <div class="card bg-base-100 shadow-xl">カラム2</div>
  <div class="card bg-base-100 shadow-xl">カラム3</div>
</div>

<!-- レスポンシブ（スマホ1列、タブレット2列、PC3列） -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="card bg-base-100 shadow-xl">カラム1</div>
  <div class="card bg-base-100 shadow-xl">カラム2</div>
  <div class="card bg-base-100 shadow-xl">カラム3</div>
</div>
```

---

## アクセシビリティ

### WCAG 2.1 AA 準拠

#### カラーコントラスト

**最低要件**: 4.5:1 (通常テキスト), 3:1 (大きいテキスト)

✅ **OK**:
- 黒 (#000000) on 白 (#FFFFFF): 21:1
- 青 (#3B82F6) on 白 (#FFFFFF): 4.6:1

❌ **NG**:
- 薄いグレー (#CCCCCC) on 白 (#FFFFFF): 1.6:1

#### aria属性

```html
<!-- ボタン -->
<button aria-label="ユーザーを削除" onclick="deleteUser()">
  <svg>...</svg>
</button>

<!-- フォーム -->
<input type="text" aria-label="検索キーワード" placeholder="検索..." />

<!-- リンク -->
<a href="/help" aria-label="ヘルプページを開く">
  <svg>...</svg>
</a>
```

#### キーボード操作

```html
<!-- Tab キーでフォーカス可能 -->
<button class="btn btn-primary" tabindex="0">ボタン</button>

<!-- フォーカスインジケーター -->
<button class="btn btn-primary focus:ring-2 focus:ring-blue-500">
  ボタン
</button>
```

---

## レスポンシブデザイン

### ブレークポイント

| デバイス | 幅 | Tailwind プレフィックス |
|----------|-----|------------------------|
| スマートフォン | < 768px | (なし) |
| タブレット | 768px - 1023px | `md:` |
| PC | ≥ 1024px | `lg:` |

### 例

```html
<!-- スマホ: 1列、タブレット以上: 2列 -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
  <div>カラム1</div>
  <div>カラム2</div>
</div>

<!-- スマホ: 小ボタン、タブレット以上: 通常ボタン -->
<button class="btn btn-sm md:btn-md btn-primary">
  ボタン
</button>
```

---

## パフォーマンス

### 画像最適化

```html
<!-- WebP形式推奨 -->
<img src="image.webp" alt="画像説明" class="w-full" loading="lazy" />

<!-- フォールバック -->
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="画像説明" class="w-full">
</picture>
```

### Lazy Loading

```html
<img src="image.jpg" alt="画像説明" loading="lazy" />
```

---

## ブラウザサポート

### 対応ブラウザ

- ✅ Chrome (最新版)
- ✅ Firefox (最新版)
- ✅ Safari (最新版)
- ✅ Edge (最新版)
- ❌ IE11 (非対応)

---

## テスト

### チェックリスト

- [ ] カラーコントラスト 4.5:1 以上
- [ ] キーボード操作可能
- [ ] スクリーンリーダー対応
- [ ] レスポンシブ確認（PC、タブレット）
- [ ] 実機テスト（iOS Safari、Android Chrome）

### ツール

- **Lighthouse**: パフォーマンス・アクセシビリティ測定
- **axe DevTools**: アクセシビリティチェック
- **WAVE**: WCAG準拠チェック

---

**参照**: `.claude/agents/designer/AGENT.md` - Designerエージェント
