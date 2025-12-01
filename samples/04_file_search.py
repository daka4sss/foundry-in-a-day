"""
Sample 04: Agent with File Search (RAG)
========================================
File Search ツールを使って、アップロードしたファイルを検索・参照するサンプルです。
これにより、RAG（Retrieval-Augmented Generation）のようなパターンを実現できます。

このサンプルでは以下を学びます：
- ファイルのアップロード
- Vector Store の作成
- File Search ツールの有効化
- ファイル内容に基づいた質問応答
"""

import os
import tempfile
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    MessageRole,
    FileSearchTool,
    ToolSet,
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
)

# 環境変数の読み込み
load_dotenv()

# 設定
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")


def create_sample_document():
    """サンプルドキュメントを作成"""
    content = """
# Azure AI Foundry 製品マニュアル

## 概要
Azure AI Foundry は、エンタープライズ向けの AI アプリケーション開発プラットフォームです。
開発者は、最新の AI モデルを活用したアプリケーションを迅速に構築できます。

## 主な機能

### 1. モデルカタログ
- OpenAI GPT-4o, GPT-4, GPT-3.5
- Meta Llama 3
- Mistral
- その他多数のオープンソースモデル

### 2. AI Agent Service
エージェント機能を提供するマネージドサービスです。
- Function Calling
- Code Interpreter
- File Search (RAG)
- Multi-modal support

### 3. プロンプトフロー
ノーコード/ローコードで AI ワークフローを構築できます。

## 料金体系
- 従量課金制
- 使用したトークン数に応じて課金
- 詳細は Azure の価格ページを参照

## サポート
- ドキュメント: https://learn.microsoft.com/azure/ai-foundry
- コミュニティ: https://aka.ms/ai-foundry-community
- サポートチケット: Azure Portal から起票

## よくある質問

Q: 日本リージョンで利用できますか？
A: はい、Japan East リージョンで利用可能です。

Q: オンプレミスでの利用は可能ですか？
A: いいえ、Azure AI Foundry はクラウドサービスのみの提供です。

Q: 既存の Azure OpenAI Service との違いは？
A: Azure AI Foundry は、Azure OpenAI Service を含む包括的な AI 開発プラットフォームです。
   エージェント機能、RAG、ファインチューニングなど、より多くの機能を統合的に提供します。
"""
    
    filepath = os.path.join(tempfile.gettempdir(), "sample_document.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def main():
    """File Search を使ったエージェントのサンプル"""
    
    # 1. クライアントの初期化
    print("🔧 クライアントを初期化しています...")
    credential = DefaultAzureCredential()
    client = AgentsClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    
    vector_store = None
    agent = None
    
    try:
        # 2. サンプルドキュメントの作成とアップロード
        print("📄 サンプルドキュメントを作成しています...")
        doc_path = create_sample_document()
        
        print("📤 ファイルをアップロードしています...")
        with open(doc_path, "rb") as f:
            uploaded_file = client.files.upload(file=f, purpose="assistants")
        print(f"   ファイルアップロード完了: {uploaded_file.id}")
        
        # 3. Vector Store の作成
        print("🗃️ Vector Store を作成しています...")
        vector_store = client.vector_stores.create_and_poll(
            name="product-manual-store",
            data_sources=[
                VectorStoreDataSource(
                    asset_identifier=uploaded_file.id,
                    asset_type=VectorStoreDataSourceAssetType.FILE_ID
                )
            ]
        )
        print(f"   Vector Store 作成完了: {vector_store.id}")
        
        # 4. File Search ツールの作成
        print("🛠️ File Search ツールを設定しています...")
        file_search = FileSearchTool(vector_store_ids=[vector_store.id])
        toolset = ToolSet()
        toolset.add(file_search)
        
        # 5. エージェントの作成（File Search 付き）
        print("🤖 エージェントを作成しています...")
        agent = client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name="file-search-assistant",
            instructions="""あなたは製品サポートの専門家です。
提供されたドキュメントを参照して、ユーザーの質問に正確に回答してください。
ドキュメントに記載がない情報については、その旨を明確に伝えてください。
日本語で回答してください。""",
            toolset=toolset
        )
        print(f"   エージェント作成完了: {agent.id}")
        
        # 6. 複数の質問を順番に処理
        questions = [
            "Azure AI Foundry で利用できるモデルを教えてください。",
            "AI Agent Service ではどんな機能が使えますか？",
            "日本リージョンで利用できますか？"
        ]
        
        for question in questions:
            print(f"\n{'='*50}")
            print(f"📝 質問: {question}")
            print('='*50)
            
            # スレッドの作成
            thread = client.threads.create()
            
            # メッセージの送信
            client.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=question
            )
            
            # エージェントの実行
            print("⚡ 検索中...")
            run = client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id
            )
            
            # 応答の取得
            messages = client.messages.list(thread_id=thread.id)
            
            for msg in messages:
                if msg.role == MessageRole.ASSISTANT:
                    for content_item in msg.content:
                        if hasattr(content_item, "text"):
                            print(f"\n🤖 回答:\n{content_item.text.value}")
                            
                            # 引用（annotations）があれば表示
                            if hasattr(content_item.text, "annotations") and content_item.text.annotations:
                                print("\n📚 参照:")
                                for ann in content_item.text.annotations:
                                    if hasattr(ann, "file_citation"):
                                        print(f"   - {ann.text}")
                    break
        
    finally:
        # 7. クリーンアップ
        print(f"\n{'='*50}")
        print("🧹 クリーンアップしています...")
        
        try:
            if agent:
                client.delete_agent(agent.id)
                print("   エージェントを削除しました")
        except Exception:
            pass
        
        try:
            if vector_store:
                client.vector_stores.delete(vector_store.id)
                print("   Vector Store を削除しました")
        except Exception:
            pass
    
    print("✅ 完了!")


if __name__ == "__main__":
    main()
