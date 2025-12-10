# プロトタイプHTMLテンプレート

## 概要

このテンプレートは、UI/UX設計時に使用する張りぼてHTML（プロトタイプ）のサンプルです。
Tailwind CSS + daisyUI を使用しています。

---

## ファイル構成

```
prototype/
├── README.md               # このファイル
├── index.html              # サンプル: トップページ
├── users-list.html         # サンプル: ユーザー一覧
├── user-detail.html        # サンプル: ユーザー詳細
└── user-edit.html          # サンプル: ユーザー編集
```

---

## 使い方

### 1. コピーして新規プロジェクトで使用

```bash
# プロトタイプディレクトリを作成
mkdir prototypes

# テンプレートをコピー
cp .claude/templates/prototype/*.html prototypes/
```

### 2. ブラウザで開く

```bash
# ローカルサーバーを起動（推奨）
python -m http.server 8000

# または直接開く
open prototypes/index.html
```

### 3. カスタマイズ

- カラー、フォント、レイアウトを調整
- モックデータを追加
- 画面遷移を追加

---

## 技術スタック

- **Tailwind CSS 3.x**: ユーティリティファーストCSSフレームワーク
- **daisyUI 4.x**: Tailwind CSSベースのコンポーネントライブラリ
- **CDN読み込み**: プロトタイプ用（本番ではビルドツール推奨）

---

## サンプル画面

### index.html
トップページ（ダッシュボード）のサンプル

### users-list.html
ユーザー一覧画面のサンプル
- 検索フォーム
- データテーブル
- ページネーション

### user-detail.html
ユーザー詳細画面のサンプル
- 詳細情報表示
- アクションボタン

### user-edit.html
ユーザー編集画面のサンプル
- 入力フォーム
- バリデーション（JavaScript未実装）
- 保存・キャンセルボタン

---

## カスタマイズ例

### カラー変更

```html
<!-- Primary色をカスタマイズ -->
<script>
tailwind.config = {
  theme: {
    extend: {
      colors: {
        primary: '#1E40AF',  // カスタムPrimary色
      }
    }
  }
}
</script>
```

### daisyUIテーマ変更

```html
<html data-theme="corporate">  <!-- ビジネス向けテーマ -->
<html data-theme="light">      <!-- ライトテーマ（デフォルト） -->
<html data-theme="dark">       <!-- ダークテーマ -->
```

---

## 次のステップ

プロトタイプ完成後:

1. **レビュー**: Architectによる設計レビュー
2. **ユーザーテスト**: 実際のユーザーによる操作確認
3. **Coderへ引き継ぎ**: プロトタイプHTMLを参考に実装

---

## 参考資料

- [Tailwind CSS公式ドキュメント](https://tailwindcss.com/docs)
- [daisyUI公式ドキュメント](https://daisyui.com/)
- [UIUX技術標準](.claude/docs/40_standards/54_uiux.md)
