# Azure AI Agent SDK v2 ワークショップ

Azure AI Foundry で Agent SDK v2 を使って AI エージェントを構築するハンズオンワークショップです。

## 📋 前提条件

- Python 3.9 以上
- Azure サブスクリプション
- Azure AI Foundry プロジェクト
- Azure CLI（`az login` で認証済み）

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-org/foundry-in-a-day.git
cd foundry-in-a-day
```

### 2. Python 仮想環境の作成

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

```bash
cp .env.sample .env
```

`.env` ファイルを編集して、Azure AI Foundry の設定を入力してください：

```
PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com/
MODEL_DEPLOYMENT_NAME=gpt-4o
```

### 5. Azure CLI で認証

```bash
az login
```

## 📚 サンプル一覧

| サンプル | 説明 | 学べること |
|---------|------|-----------|
| [01_basic_agent.py](samples/01_basic_agent.py) | 基本的なエージェント | エージェントの作成、スレッド、メッセージング |
| [02_function_tools.py](samples/02_function_tools.py) | Function Tools | カスタム関数の定義、ツール呼び出し |
| [03_code_interpreter.py](samples/03_code_interpreter.py) | Code Interpreter | Python コード実行、データ分析 |
| [04_file_search.py](samples/04_file_search.py) | File Search (RAG) | ファイル検索、Vector Store |
| [05_multi_agent.py](samples/05_multi_agent.py) | マルチエージェント | 複数エージェントの連携 |

## 🏃 サンプルの実行

各サンプルは個別に実行できます：

```bash
# 基本的なエージェント
python samples/01_basic_agent.py

# Function Tools
python samples/02_function_tools.py

# Code Interpreter
python samples/03_code_interpreter.py

# File Search
python samples/04_file_search.py

# マルチエージェント
python samples/05_multi_agent.py
```

## 📖 ワークショップの進め方

### Step 1: 基本を理解する (01_basic_agent.py)

最初のサンプルで、Agent SDK の基本的な使い方を学びます：
- クライアントの初期化
- エージェントの作成
- スレッドとメッセージの概念
- エージェントの実行と応答取得

### Step 2: ツールを使う (02_function_tools.py)

エージェントにカスタム関数を追加して、外部処理を実行する方法を学びます：
- Function Tool の定義方法
- ツール呼び出しのハンドリング
- 複数ツールの登録

### Step 3: コードを実行する (03_code_interpreter.py)

Code Interpreter を使って、エージェントに Python コードを実行させます：
- データ分析タスク
- グラフ生成
- ファイル出力の取得

### Step 4: RAG を実装する (04_file_search.py)

File Search ツールで、ドキュメントベースの Q&A を実現します：
- ファイルのアップロード
- Vector Store の作成
- 検索と引用

### Step 5: 複数エージェントを連携する (05_multi_agent.py)

専門性の異なる複数のエージェントを協調させます：
- エージェントの役割分担
- オーケストレーションパターン
- 結果の統合

## 🔗 参考リンク

- [Azure AI Agents SDK ドキュメント](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme)
- [Azure AI Foundry](https://ai.azure.com/)
- [Azure AI Agents Labs](https://github.com/Azure/azure-ai-agents-labs)

## 📝 ライセンス

MIT License