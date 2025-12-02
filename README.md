# Azure AI Foundry Workshop

Microsoft Foundry SDK を使って AI エージェントを構築するハンズオンです。

## 📁 コンテンツ

| # | ファイル | 内容 |
|---|----------|------|
| 1 | `simple-agent.ipynb` | 基本的なエージェント作成とプロンプト実行 |
| 2 | `web-search-agent.ipynb` | Bing Grounding Tool でWeb検索（ストリーミング対応） |
| 3 | `web-search-tool-agent.ipynb` | WebSearchPreviewTool でシンプルにWeb検索 |
| 4 | `mcp-server-agent.ipynb` | MCP (Model Context Protocol) サーバー連携 |
| 5 | `foundry memory.ipynb` | メモリストアによるユーザー情報の保存・検索 |

### 1. 仮想環境の作成
```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化（Windows）
.\venv\Scripts\activate

# 仮想環境を有効化（Mac/Linux）
source venv/bin/activate
```

### 2. 依存関係インストール
```bash
pip install -r requirements.txt
```


### 3. 環境変数設定
`.env.sample` をコピーして `.env` を作成:
```bash
cp .env.sample .env
```

`.env` を編集:
```env
project_endpoint=<Foundry プロジェクトエンドポイント>
BING_PROJECT_CONNECTION_ID=<Bing接続ID>  # 2番で使用
```

### 4. Azure認証
`DefaultAzureCredential` を使用。以下のいずれかで認証:
```bash
az login
```
または VS Code Azure拡張機能でサインイン。

## 🚀 実行方法

各 `.ipynb` ファイルを VS Code または Jupyter で開き、セルを順番に実行。

## 📋 前提条件

- Python 3.8+
- Foundry Project
- デプロイ済みモデル（例: `gpt-4.1`）
- Bing Search 接続（2番用）
- MCP 接続（4番用）

## 🔗 参考リンク

- [Microsoft Foundry ドキュメント](https://learn.microsoft.com/ja-jp/azure/ai-foundry/what-is-azure-ai-foundry?view=foundry)
- [Azure AI Projects SDKの最新インストール方法](https://learn.microsoft.com/ja-jp/azure/ai-foundry/quickstarts/get-started-code?view=foundry&preserve-view=true&tabs=python%2Cpython2#install-and-authenticate)