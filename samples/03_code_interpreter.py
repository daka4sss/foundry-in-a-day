"""
Sample 03: Agent with Code Interpreter
=======================================
Code Interpreter ツールを使って、エージェントにPythonコードを実行させるサンプルです。

このサンプルでは以下を学びます：
- Code Interpreter ツールの有効化
- データ分析タスクの実行
- 生成されたファイル（グラフなど）の取得
"""

import os
import tempfile
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    MessageRole,
    CodeInterpreterTool,
    ToolSet,
)

# 環境変数の読み込み
load_dotenv()

# 設定
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")


def main():
    """Code Interpreter を使ったエージェントのサンプル"""
    
    # 1. クライアントの初期化
    print("🔧 クライアントを初期化しています...")
    credential = DefaultAzureCredential()
    client = AgentsClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    
    try:
        # 2. Code Interpreter ツールの作成
        print("🛠️ Code Interpreter ツールを設定しています...")
        code_interpreter = CodeInterpreterTool()
        toolset = ToolSet()
        toolset.add(code_interpreter)
        
        # 3. エージェントの作成（Code Interpreter 付き）
        print("🤖 エージェントを作成しています...")
        agent = client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name="code-interpreter-assistant",
            instructions="""あなたはデータ分析の専門家です。
Code Interpreter を使って、Pythonコードを実行してユーザーのリクエストに応えてください。
グラフを作成する場合は、matplotlib を使用してください。
日本語で回答してください。""",
            toolset=toolset
        )
        print(f"   エージェント作成完了: {agent.id}")
        
        # 4. スレッドの作成
        print("📝 スレッドを作成しています...")
        thread = client.threads.create()
        
        # 5. メッセージの送信（コード実行が必要な質問）
        user_message = """
以下のデータを分析して、棒グラフを作成してください：

商品A: 売上 150万円
商品B: 売上 230万円
商品C: 売上 180万円
商品D: 売上 95万円
商品E: 売上 310万円

また、合計売上と平均売上も計算してください。
"""
        print(f"💬 メッセージを送信しています...")
        print(f"   {user_message[:50]}...")
        
        client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_message
        )
        
        # 6. エージェントの実行（自動でツール呼び出しを処理）
        print("⚡ エージェントを実行しています（Code Interpreter が動作中）...")
        run = client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )
        print(f"   実行完了: ステータス = {run.status}")
        
        # 7. 応答の取得
        print("\n📨 応答を取得しています...\n")
        messages = client.messages.list(thread_id=thread.id)
        
        for msg in reversed(list(messages)):
            role = "👤 User" if msg.role == MessageRole.USER else "🤖 Assistant"
            print(f"{role}:")
            
            for content_item in msg.content:
                if hasattr(content_item, "text"):
                    print(f"   {content_item.text.value}")
                elif hasattr(content_item, "image_file"):
                    # 画像ファイルが生成された場合
                    file_id = content_item.image_file.file_id
                    print(f"   📊 [画像ファイル生成: {file_id}]")
                    
                    # ファイルをダウンロード
                    try:
                        file_content = client.files.get_content(file_id)
                        output_path = os.path.join(tempfile.gettempdir(), f"output_chart_{file_id[:8]}.png")
                        with open(output_path, "wb") as f:
                            f.write(file_content)
                        print(f"   💾 ファイル保存: {output_path}")
                    except Exception as e:
                        print(f"   ⚠️ ファイル保存エラー: {e}")
            print()
        
    finally:
        # 8. クリーンアップ
        print("🧹 クリーンアップしています...")
        try:
            client.delete_agent(agent.id)
            print("   エージェントを削除しました")
        except Exception:
            pass
    
    print("✅ 完了!")


if __name__ == "__main__":
    main()
