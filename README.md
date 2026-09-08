# ComfyUI-PromptSnapshot

ComfyUI のワークフロー内で生成・変換したプロンプトを、編集可能な状態で保持するためのカスタムノードです。

LLM、翻訳ノード、プロンプト生成ノードなどから受け取った文字列を `Prompt Snapshot` に取り込み、ノード上の複数行テキストフィールドへ表示します。

取り込んだプロンプトはその場で編集でき、編集後の内容をそのまま後続ノードへ出力できます。

また、現在使用しているプロンプトをワークフローの Widget 値として保持するため、生成画像に ComfyUI の workflow metadata を保存している場合は、その画像からワークフローを読み込んだ際にもプロンプトを確認できます。

---

## Features

* 上流ノードから `STRING` のプロンプトを受け取る
* 受け取ったプロンプトを編集可能な複数行テキストフィールドへ表示
* 編集したプロンプトをそのまま `STRING` として出力
* 上流プロンプトが変更された場合だけ Snapshot を自動更新
* 上流プロンプトが変わっていなければ、手動編集した内容を維持
* 現在のプロンプトを ComfyUI の workflow metadata に保持
* 生成画像からワークフローを復元した場合にもプロンプトを確認可能
* 外部 Python パッケージ不要
* ComfyUI の JavaScript Extension による Widget 同期

---

# Why Prompt Snapshot?

たとえば、次のようなワークフローを考えます。

```text
[Japanese Prompt]
        │
        ▼
[Translation / LLM]
        │
        │ English prompt
        ▼
 [Prompt Snapshot]
        │
        ▼
[Image / Video Generation]
```

LLM や翻訳ノードによってプロンプトを自動生成している場合、その出力は実行時に生成される一時的な値です。

そのまま画像生成ノードへ接続すると、

```text
入力した日本語
       ↓
LLM / Translation
       ↓
実際に生成に使われた英語プロンプト
```

のうち、最終的にどのプロンプトが使われたのかをワークフロー上から確認しづらくなることがあります。

`Prompt Snapshot` を途中に入れることで、

```text
LLM が生成したプロンプト
        ↓
Prompt Snapshot に保存
        ↓
必要なら人間が編集
        ↓
実際の画像・動画生成に使用
```

という流れを作ることができます。

---

# Installation

## 1. `custom_nodes` へ移動

ComfyUI の `custom_nodes` ディレクトリへ移動します。

```bash
cd ComfyUI/custom_nodes
```

## 2. リポジトリを clone

```bash
git clone https://github.com/Knightkun2023/ComfyUI-PromptSnapshot.git
```

インストール後は次のような構成になります。

```text
ComfyUI/
└── custom_nodes/
    └── ComfyUI-PromptSnapshot/
        ├── __init__.py
        ├── prompt_snapshot.py
        ├── LICENSE
        ├── README.md
        └── js/
            └── prompt_snapshot.js
```

## 3. ComfyUI を再起動

ComfyUI を完全に再起動し、ブラウザを再読み込みしてください。

ノード検索で、

```text
Prompt Snapshot
```

を検索できます。

カテゴリは、

```text
utils
└── text
    └── Prompt Snapshot
```

です。

---

# Dependencies

追加の Python パッケージは必要ありません。

このカスタムノードには `requirements.txt` はなく、ComfyUI が提供する Python / JavaScript API のみを使用します。

---

# Node

ノード名:

```text
Prompt Snapshot
```

カテゴリ:

```text
utils/text
```

---

# Inputs

| Input       | Type     | Description                    |
| ----------- | -------- | ------------------------------ |
| `prompt_in` | `STRING` | 上流ノードから受け取るプロンプト               |
| `prompt`    | `STRING` | 現在の Snapshot。編集可能な複数行テキストフィールド |

## `prompt_in`

上流の LLM、翻訳、テンプレート処理などによって生成されたプロンプトを接続します。

`prompt_in` は接続専用の入力です。

例:

```text
[LLM / Translator]
       │
       │ STRING
       ▼
   prompt_in
[Prompt Snapshot]
```

## `prompt`

現在の Snapshot が表示される複数行テキストフィールドです。

このフィールドは直接編集できます。

たとえば、上流の LLM が、

```text
A cinematic portrait of a woman standing near a window.
```

を生成したあと、Prompt Snapshot 上で、

```text
A cinematic portrait of a woman standing near a window,
soft morning sunlight, natural expression, shallow depth of field.
```

のように手動で調整できます。

---

# Output

| Output   | Type     | Description      |
| -------- | -------- | ---------------- |
| `prompt` | `STRING` | 現在の Snapshot の内容 |

出力された `prompt` は、そのまま CLIP Text Encode、画像生成、動画生成、その他のプロンプト入力へ接続できます。

```text
[Prompt Snapshot]
       │
       │ prompt
       ▼
[Text Encode / Image Generation / Video Generation]
```

---

# Behavior

Prompt Snapshot の重要な特徴は、上流入力と手動編集を区別することです。

## First execution

最初の実行では、

```text
prompt_in
```

の内容が Snapshot として採用されます。

たとえば、

```text
prompt_in:
A cinematic portrait of a woman.
```

なら、`prompt` フィールドにも、

```text
A cinematic portrait of a woman.
```

が表示され、その文字列が出力されます。

---

## Editing the snapshot

最初の実行後、`prompt` フィールドを手動で編集できます。

例:

```text
A cinematic portrait of a woman,
soft natural lighting and shallow depth of field.
```

この状態でも `prompt_in` が前回と同じなら、次回のワークフロー実行時には上流の値で上書きされません。

つまり、

```text
prompt_in
    │
    │ unchanged
    ▼
Prompt Snapshot
    │
    └── 手動編集した prompt を維持
```

となります。

---

## When the upstream prompt changes

上流から渡された `prompt_in` が前回と異なる場合は、新しいプロンプトが Snapshot に反映されます。

```text
Previous prompt_in
        │
        │
        ├── same
        │      ↓
        │   edited prompt を維持
        │
        └── changed
               ↓
           新しい prompt_in で更新
```

これにより、

* 上流の設定を変えずに再実行した場合は手動編集を維持する
* 上流のプロンプトそのものを変更した場合は Snapshot も更新する

という使い分けができます。

---

# Typical Workflow

たとえば、日本語でプロンプトを作成し、LLM で英語へ変換して画像生成する場合です。

```text
[Japanese Prompt]
        │
        ▼
      [LLM]
 Japanese → English
        │
        ▼
[Prompt Snapshot]
        │
        │ editable English prompt
        ▼
[Image Generation]
```

### 1. 最初の実行

```text
Japanese Prompt
        ↓
LLM
        ↓
English Prompt A
        ↓
Prompt Snapshot
```

Prompt Snapshot に、

```text
English Prompt A
```

が表示されます。

### 2. Snapshot を編集

ユーザーが、

```text
English Prompt A'
```

へ編集します。

### 3. 再実行

上流の入力を変更していなければ、

```text
English Prompt A'
```

がそのまま使用されます。

LLM が再度実行されても、`prompt_in` の内容が同じであれば Snapshot の手動編集内容は維持されます。

### 4. 上流プロンプトを変更

日本語プロンプトや LLM の出力が変更され、

```text
English Prompt B
```

になった場合は、

```text
Prompt Snapshot
    ↓
English Prompt B
```

へ自動的に更新されます。

---

# Workflow Metadata

Prompt Snapshot は現在使用しているプロンプトを、ノードの Widget 値として workflow metadata に反映します。

ComfyUI で生成画像へ workflow metadata を保存している場合、

```text
Generated Image
      │
      │ workflow metadata
      ▼
ComfyUI
```

とワークフローを読み戻した際に、その生成で使用していた Snapshot のプロンプトを確認できます。

これは、

```text
「この画像を生成したとき、
 最終的にどんなプロンプトを使っていたのか？」
```

を後から確認したい場合に便利です。

> [!NOTE]
> ComfyUI 側で metadata の保存を無効にしている場合、生成画像自体には workflow metadata は保存されません。
>
> 通常のワークフローファイルとして保存した場合は、Prompt Snapshot の `prompt` Widget もワークフローの一部として保存されます。

---

# How It Works

Prompt Snapshot は、前回入力された `prompt_in` をノードの property に保持します。

内部的には、

```text
prompt_snapshot_last_input
```

という値を使用します。

ワークフロー実行時に、

```text
current prompt_in
        │
        ▼
previous prompt_in と比較
        │
        ├── changed
        │      ↓
        │   prompt_in を Snapshot に採用
        │
        └── unchanged
               ↓
            prompt Widget の内容を採用
```

という判定を行います。

これにより、上流からの自動入力とユーザーによる手動編集を両立しています。

---

# JavaScript Extension

`js/prompt_snapshot.js` は、Python バックエンドで新しい Snapshot が採用された場合に、ComfyUI 上の `prompt` Widget を同期します。

上流プロンプトが変更された場合、

```text
Backend
   │
   │ snapshot_prompt
   ▼
JavaScript Extension
   │
   ▼
prompt Widget
```

という形で表示内容が更新されます。

上流入力が変化していない場合には Widget を更新しないため、ユーザーが編集した内容は維持されます。

---

# File Structure

```text
ComfyUI-PromptSnapshot/
├── __init__.py
├── prompt_snapshot.py
├── README.md
├── LICENSE
└── js/
    └── prompt_snapshot.js
```

### `prompt_snapshot.py`

Snapshot の判定、文字列出力、workflow metadata の更新を担当します。

### `js/prompt_snapshot.js`

バックエンドで Snapshot が更新された場合に、ComfyUI 上の `prompt` Widget を同期します。

### `__init__.py`

ComfyUI へのノード登録と JavaScript Extension ディレクトリの公開を行います。

---

# Troubleshooting

## Prompt Snapshot が表示されない

以下の場所にリポジトリが存在することを確認してください。

```text
ComfyUI/custom_nodes/ComfyUI-PromptSnapshot/
```

その後、ComfyUI を完全に再起動し、ブラウザを再読み込みしてください。

---

## `prompt` が更新されない

`prompt_in` の値が前回と同じ場合、これは正常な動作です。

Prompt Snapshot は手動編集した内容を維持するため、上流入力が変わらない限り `prompt` フィールドを上書きしません。

新しい Snapshot に切り替えるには、上流から渡される `prompt_in` の内容を変更してください。

---

## 編集した prompt が上流の値に戻った

`prompt_in` が前回の実行時から変更された場合、新しい上流プロンプトが優先されます。

これは、

```text
上流プロンプトが変更された
        ↓
新しい生成条件になった
        ↓
Snapshot も更新する
```

という意図した動作です。

---

## 生成画像からワークフローを読み込んでも Snapshot がない

生成時に ComfyUI の workflow metadata 保存が無効になっていないか確認してください。

metadata が画像に保存されていない場合、画像から元のワークフローや Snapshot を復元することはできません。

---

# License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.

---

# Repository

```text
https://github.com/Knightkun2023/ComfyUI-PromptSnapshot
```
