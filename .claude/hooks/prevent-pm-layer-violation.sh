#!/bin/bash
# PM Layer 1 違反検知 Hook (ハイブリッド方式)
# PMが成果物を直接編集しようとした際にブロックし、適切なサブエージェントへの委譲を促す

CONFIG_FILE=".claude/project-structure.json"

# ファイルパス取得
FILE_PATH=""

# 環境変数から取得を試みる
if [ -n "$CLAUDE_HOOK_PARAMS" ]; then
    FILE_PATH=$(echo "$CLAUDE_HOOK_PARAMS" | jq -r '.file_path // empty' 2>/dev/null)
fi

# 標準入力から取得を試みる（環境変数がない場合）
if [ -z "$FILE_PATH" ] && [ ! -t 0 ]; then
    STDIN_PARAMS=$(cat)
    FILE_PATH=$(echo "$STDIN_PARAMS" | jq -r '.file_path // empty' 2>/dev/null)
fi

# ファイルパスが取得できない場合はスキップ
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# ========================================
# アプローチ1: 設定ファイルベース（優先）
# ========================================
if [ -f "$CONFIG_FILE" ]; then
    # allow_write リストと照合（早期リターン）
    ALLOW_PATTERNS=$(jq -r '.pm_policy.allow_write[]' "$CONFIG_FILE" 2>/dev/null)
    for pattern in $ALLOW_PATTERNS; do
        # **を*に変換してパターンマッチング
        pattern_glob="${pattern//\*\*/\*}"
        if [[ "$FILE_PATH" == $pattern_glob ]]; then
            exit 0  # 許可
        fi
    done

    # deny_write リストと照合
    DENY_PATTERNS=$(jq -r '.pm_policy.deny_write[]' "$CONFIG_FILE" 2>/dev/null)
    for pattern in $DENY_PATTERNS; do
        pattern_glob="${pattern//\*\*/\*}"
        if [[ "$FILE_PATH" == $pattern_glob ]]; then
            # 委譲先ラベル取得
            AGENT=$(jq -r ".pm_policy.labels[\"$pattern\"] // \"サブエージェント\"" "$CONFIG_FILE" 2>/dev/null)

            echo "❌ PM Layer 1 違反: 成果物の編集禁止" >&2
            echo "" >&2
            echo "対象: $FILE_PATH" >&2
            echo "→ Task ツールで $AGENT に委譲してください" >&2
            exit 2  # ブロッキングエラー
        fi
    done

    # 設定ファイルに該当なし → 許可
    exit 0
fi

# ========================================
# アプローチ2: 自動検出（フォールバック）
# ========================================

# PMが自由に編集できるパス(早期リターン)
case "$FILE_PATH" in
    docs/requirements/*|docs/要件定義/*|.claude-state/*)
        exit 0  # 許可
        ;;
esac

# パターンベースで判定
# 1. コードディレクトリ検出
if [[ "$FILE_PATH" =~ ^(src|app|backend|frontend|server|client)/ ]]; then
    echo "❌ PM Layer 1 違反: コードの編集禁止" >&2
    echo "" >&2
    echo "対象: $FILE_PATH" >&2
    echo "→ Task ツールで Coder に委譲してください" >&2
    exit 2
fi

# 2. インフラディレクトリ検出
if [[ "$FILE_PATH" =~ ^(infra|infrastructure|terraform|cloudformation)/ ]]; then
    echo "❌ PM Layer 1 違反: インフラコードの編集禁止" >&2
    echo "" >&2
    echo "対象: $FILE_PATH" >&2
    echo "→ Task ツールで Infra-Architect / SRE に委譲してください" >&2
    exit 2
fi

# 3. テストディレクトリ検出
if [[ "$FILE_PATH" =~ ^(tests?|__tests__|spec)/ ]]; then
    echo "❌ PM Layer 1 違反: テストコードの編集禁止" >&2
    echo "" >&2
    echo "対象: $FILE_PATH" >&2
    echo "→ Task ツールで QA に委譲してください" >&2
    exit 2
fi

# 4. 設計書検出
if [[ "$FILE_PATH" =~ ^docs/(design|設計|基本設計|詳細設計)/ ]]; then
    echo "❌ PM Layer 1 違反: 設計書の編集禁止" >&2
    echo "" >&2
    echo "対象: $FILE_PATH" >&2
    echo "PMは設計書を読んでレビューしますが、作成はしません" >&2
    echo "" >&2
    echo "→ Task ツールで委譲:" >&2
    echo "   App-Architect / Infra-Architect" >&2
    exit 2
fi

# 5. 技術標準
if [[ "$FILE_PATH" =~ ^\.claude/docs/40_standards/ ]]; then
    echo "⚠️ 技術標準の編集検知" >&2
    echo "" >&2
    echo "対象: $FILE_PATH" >&2
    echo "技術標準はサブエージェントが参照します" >&2
    exit 2
fi

# その他のパスは許可
exit 0
