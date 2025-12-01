"""
Sample 02: Agent with Function Tools
=====================================
エージェントにカスタム関数（ツール）を追加して、外部処理を実行するサンプルです。

このサンプルでは以下を学びます：
- Function Tool の定義
- ToolSet を使ったツールの登録
- ツール呼び出しの処理
- エージェントとツールの連携
"""

import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    MessageRole,
    FunctionTool,
    ToolSet,
    RunStatus,
    SubmitToolOutputsAction,
)

# 環境変数の読み込み
load_dotenv()

# 設定
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")


# ========================================
# カスタム関数（ツール）の定義
# ========================================

def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    指定された場所の天気を取得する（デモ用のダミーデータ）
    
    Args:
        location: 場所の名前（例: "東京"）
        unit: 温度の単位 ("celsius" または "fahrenheit")
    
    Returns:
        天気情報の辞書
    """
    # 実際のアプリケーションでは、ここで天気APIを呼び出します
    weather_data = {
        "東京": {"temp": 22, "condition": "晴れ", "humidity": 60},
        "大阪": {"temp": 24, "condition": "曇り", "humidity": 65},
        "札幌": {"temp": 15, "condition": "雨", "humidity": 80},
        "福岡": {"temp": 25, "condition": "晴れ", "humidity": 55},
    }
    
    data = weather_data.get(location, {"temp": 20, "condition": "不明", "humidity": 50})
    
    if unit == "fahrenheit":
        data["temp"] = data["temp"] * 9 / 5 + 32
    
    return {
        "location": location,
        "temperature": data["temp"],
        "unit": unit,
        "condition": data["condition"],
        "humidity": data["humidity"]
    }


def calculate(expression: str) -> dict:
    """
    数式を計算する
    
    Args:
        expression: 計算式（例: "2 + 3 * 4"）
    
    Returns:
        計算結果の辞書
    """
    try:
        # 安全な評価のため、許可された文字のみを含むかチェック
        allowed_chars = set("0123456789+-*/().% ")
        if not all(c in allowed_chars for c in expression):
            return {"error": "無効な文字が含まれています", "expression": expression}
        
        result = eval(expression)  # noqa: S307 - 入力は検証済み
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e), "expression": expression}


# ========================================
# ツールの定義（OpenAI Function Calling 形式）
# ========================================

# 天気取得ツールの定義
weather_tool_definition = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "指定された場所の現在の天気情報を取得します",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "天気を取得する場所（例: 東京, 大阪）"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "温度の単位"
                }
            },
            "required": ["location"]
        }
    }
}

# 計算ツールの定義
calculate_tool_definition = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "数式を計算して結果を返します",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "計算する数式（例: 2 + 3 * 4）"
                }
            },
            "required": ["expression"]
        }
    }
}


def execute_tool(tool_name: str, arguments: dict) -> str:
    """ツール名と引数に基づいてツールを実行"""
    if tool_name == "get_weather":
        result = get_weather(**arguments)
    elif tool_name == "calculate":
        result = calculate(**arguments)
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    
    return json.dumps(result, ensure_ascii=False)


def main():
    """Function Tools を使ったエージェントのサンプル"""
    
    # 1. クライアントの初期化
    print("🔧 クライアントを初期化しています...")
    credential = DefaultAzureCredential()
    client = AgentsClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    
    try:
        # 2. ツールの作成
        print("🛠️ ツールを定義しています...")
        functions = FunctionTool(definitions=[weather_tool_definition, calculate_tool_definition])
        toolset = ToolSet()
        toolset.add(functions)
        
        # 3. エージェントの作成（ツール付き）
        print("🤖 エージェントを作成しています...")
        agent = client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name="function-tools-assistant",
            instructions="""あなたは便利なアシスタントです。
ユーザーの質問に答えるために、必要に応じて以下のツールを使用してください：
- get_weather: 天気情報を取得
- calculate: 数式を計算

日本語で回答してください。""",
            toolset=toolset
        )
        print(f"   エージェント作成完了: {agent.id}")
        
        # 4. スレッドの作成
        print("📝 スレッドを作成しています...")
        thread = client.threads.create()
        
        # 5. メッセージの送信（ツールを使う質問）
        user_message = "東京と大阪の天気を教えてください。また、(23 + 17) * 2 を計算してください。"
        print(f"💬 メッセージを送信: {user_message}")
        
        client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_message
        )
        
        # 6. エージェントの実行（ツール呼び出しを処理）
        print("⚡ エージェントを実行しています...")
        run = client.runs.create(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # 7. ツール呼び出しのループ処理
        while True:
            run = client.runs.get(thread_id=thread.id, run_id=run.id)
            print(f"   ステータス: {run.status}")
            
            if run.status == RunStatus.COMPLETED:
                break
            elif run.status == RunStatus.FAILED:
                print(f"❌ エラー: {run.last_error}")
                break
            elif run.status == RunStatus.REQUIRES_ACTION:
                # ツール呼び出しが必要
                if isinstance(run.required_action, SubmitToolOutputsAction):
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    tool_outputs = []
                    
                    for tool_call in tool_calls:
                        print(f"   🔧 ツール呼び出し: {tool_call.function.name}")
                        arguments = json.loads(tool_call.function.arguments)
                        output = execute_tool(tool_call.function.name, arguments)
                        print(f"      結果: {output}")
                        
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": output
                        })
                    
                    # ツールの結果を送信
                    run = client.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
            else:
                # 処理中の場合は少し待つ
                import time
                time.sleep(1)
        
        # 8. 応答の取得
        print("\n📨 応答を取得しています...\n")
        messages = client.messages.list(thread_id=thread.id)
        
        for msg in reversed(list(messages)):
            role = "👤 User" if msg.role == MessageRole.USER else "🤖 Assistant"
            content_text = ""
            for content_item in msg.content:
                if hasattr(content_item, "text"):
                    content_text += content_item.text.value
            print(f"{role}: {content_text}\n")
        
    finally:
        # 9. クリーンアップ
        print("🧹 クリーンアップしています...")
        try:
            client.delete_agent(agent.id)
            print("   エージェントを削除しました")
        except Exception:
            pass
    
    print("✅ 完了!")


if __name__ == "__main__":
    main()
