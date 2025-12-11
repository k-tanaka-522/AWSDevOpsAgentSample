# D-02-02 [画面] メイン画面ViewModel詳細

## 1. クラス概要
`MainWindowViewModel` はアプリケーションのメイン画面の状態を管理し、タスクリストの表示制御、およびCRUD操作の起点となるコマンドを提供する。

## 2. プロパティ定義
| プロパティ名 | 型 | 通知 | 説明 |
|---|---|---|---|
| Tasks | `ObservableCollection<TaskItem>` | ○ | 画面リストにバインドされるタスクコレクション。 |
| SelectedTask | `TaskItem` | ○ | リストで現在選択中のタスク。右ペインの表示ソース。 |
| StatusMessage | `string` | ○ | ステータスバーへの表示メッセージ（例: "読み込み完了"）。 |
| IsLoading | `bool` | ○ | 非同期処理中のプログレス表示制御フラグ。 |

## 3. コマンド定義
| コマンド名 | 処理概要 | 備考 |
|---|---|---|
| `LoadedCommand` | 画面初期表示時に発火。`SqliteTaskRepository` からデータを全件取得し `Tasks` に格納する。 | `async` |
| `AddTaskCommand` | `TaskDetailDialog` を新規モードで開き、保存されたら `Tasks` に追加する。 | |
| `CompleteTaskCommand` | パラメータのTaskを完了状態にし、DB更新後、リストから除外または視覚的にグレーアウトする。 | |
| `SortCommand` | ユーザーの指定（優先度順/期日順）に応じて `Tasks` をソートし直す。 | デフォルトは優先度順 |

## 4. 状態遷移・振る舞い詳細
1. **初期化**:
   - コンストラクタでリポジトリをDIで受け取る。
   - `LoadedCommand` 実行時に `IsLoading = true` → `LoadData()` → `Sort()` → `IsLoading = false` の順で処理。
2. **優先度再計算**:
   - タスク追加・編集時、自動的にバックグラウンドで優先度が計算されるが、ViewModel側ではリストの再ソート (`SortTasks()`) を呼び出して表示順序を維持する。
