"""
Sample 01: Basic Agent
======================
Azure AI Agent SDK v2 を使って、基本的なエージェントを作成して対話するサンプルです。

このサンプルでは以下を学びます：
- Azure AI Agent クライアントの初期化
- エージェントの作成
- スレッドの作成とメッセージの送信
- エージェントの実行と応答の取得
- リソースのクリーンアップ
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole

# 環境変数の読み込み
load_dotenv()

# 設定
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")


def main():
    """基本的なエージェントを作成して対話するサンプル"""
    
    # 1. クライアントの初期化
    # DefaultAzureCredential は Azure CLI, 環境変数, マネージドID など複数の認証方法を自動で試行します
    print("🔧 クライアントを初期化しています...")
    credential = DefaultAzureCredential()
    client = AgentsClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    
    try:
        # 2. エージェントの作成
        print("🤖 エージェントを作成しています...")
        agent = client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name="basic-assistant",
            instructions="あなたは親切で丁寧な日本語アシスタントです。ユーザーの質問に分かりやすく回答してください。"
        )
        print(f"   エージェント作成完了: {agent.id}")
        
        # 3. スレッドの作成
        # スレッドは会話のセッションを表します
        print("📝 スレッドを作成しています...")
        thread = client.threads.create()
        print(f"   スレッド作成完了: {thread.id}")
        
        # 4. メッセージの送信
        print("💬 メッセージを送信しています...")
        message = client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content="Azure AI Foundry について簡単に教えてください。"
        )
        print(f"   メッセージ送信完了: {message.id}")
        
        # 5. エージェントの実行
        print("⚡ エージェントを実行しています...")
        run = client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )
        print(f"   実行完了: ステータス = {run.status}")
        
        # 6. 応答の取得
        print("\n📨 応答を取得しています...\n")
        messages = client.messages.list(thread_id=thread.id)
        
        # メッセージを古い順に表示
        for msg in reversed(list(messages)):
            role = "👤 User" if msg.role == MessageRole.USER else "🤖 Assistant"
            # content はリスト形式なので、テキストを結合
            content_text = ""
            for content_item in msg.content:
                if hasattr(content_item, "text"):
                    content_text += content_item.text.value
            print(f"{role}: {content_text}\n")
        
    finally:
        # 7. クリーンアップ
        # 作成したエージェントを削除します
        print("🧹 クリーンアップしています...")
        try:
            client.delete_agent(agent.id)
            print("   エージェントを削除しました")
        except Exception:
            pass
    
    print("✅ 完了!")


if __name__ == "__main__":
    main()
