"""
Sample 05: Multi-Agent Orchestration
=====================================
複数のエージェントを協調させて、複雑なタスクを処理するサンプルです。

このサンプルでは以下を学びます：
- 専門性の異なる複数エージェントの作成
- エージェント間の連携パターン
- オーケストレーションロジックの実装
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


class MultiAgentOrchestrator:
    """複数のエージェントを管理・連携させるオーケストレーター"""
    
    def __init__(self, client: AgentsClient):
        self.client = client
        self.agents = {}
    
    def create_agents(self):
        """専門エージェントを作成"""
        
        # リサーチエージェント
        self.agents["researcher"] = self.client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name="researcher-agent",
            instructions="""あなたはリサーチの専門家です。
与えられたトピックについて、重要なポイントを調査・整理してください。
箇条書きで、簡潔にまとめてください。"""
        )
        print(f"   📚 リサーチエージェント作成: {self.agents['researcher'].id}")
        
        # ライターエージェント
        self.agents["writer"] = self.client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name="writer-agent",
            instructions="""あなたはプロのテクニカルライターです。
提供された情報を基に、読みやすく魅力的な文章を作成してください。
マークダウン形式で出力してください。"""
        )
        print(f"   ✍️ ライターエージェント作成: {self.agents['writer'].id}")
        
        # レビューエージェント
        self.agents["reviewer"] = self.client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name="reviewer-agent",
            instructions="""あなたは品質管理の専門家です。
提供されたコンテンツをレビューし、改善点を具体的に指摘してください。
良い点と改善点の両方を挙げてください。"""
        )
        print(f"   🔍 レビューエージェント作成: {self.agents['reviewer'].id}")
    
    def run_agent(self, agent_name: str, prompt: str) -> str:
        """指定されたエージェントを実行"""
        agent = self.agents[agent_name]
        thread = None
        
        try:
            # スレッドを作成
            thread = self.client.threads.create()
            
            # メッセージを送信
            self.client.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=prompt
            )
            
            # 実行
            run = self.client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id
            )
            
            # 応答を取得
            messages = self.client.messages.list(thread_id=thread.id)
            
            for msg in messages:
                if msg.role == MessageRole.ASSISTANT:
                    for content_item in msg.content:
                        if hasattr(content_item, "text"):
                            return content_item.text.value
            
            return ""
        finally:
            # スレッドのクリーンアップ
            if thread:
                try:
                    self.client.threads.delete(thread.id)
                except Exception:
                    pass
    
    def orchestrate(self, topic: str) -> dict:
        """複数エージェントを協調させてタスクを実行"""
        results = {}
        
        # Step 1: リサーチ
        print("\n📚 Step 1: リサーチエージェントが調査中...")
        research_prompt = f"以下のトピックについて調査してください: {topic}"
        results["research"] = self.run_agent("researcher", research_prompt)
        print(f"   完了！")
        
        # Step 2: ライティング
        print("\n✍️ Step 2: ライターエージェントが執筆中...")
        writing_prompt = f"""以下の調査結果を基に、ブログ記事を作成してください：

調査結果:
{results['research']}

トピック: {topic}
"""
        results["article"] = self.run_agent("writer", writing_prompt)
        print(f"   完了！")
        
        # Step 3: レビュー
        print("\n🔍 Step 3: レビューエージェントが確認中...")
        review_prompt = f"""以下の記事をレビューしてください：

{results['article']}
"""
        results["review"] = self.run_agent("reviewer", review_prompt)
        print(f"   完了！")
        
        return results
    
    def cleanup(self):
        """作成したエージェントを削除"""
        for name, agent in self.agents.items():
            try:
                self.client.delete_agent(agent.id)
                print(f"   {name} エージェントを削除しました")
            except Exception:
                pass


def main():
    """Multi-Agent オーケストレーションのサンプル"""
    
    # 1. クライアントの初期化
    print("🔧 クライアントを初期化しています...")
    credential = DefaultAzureCredential()
    client = AgentsClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    
    # 2. オーケストレーターの作成
    orchestrator = MultiAgentOrchestrator(client)
    
    try:
        # 3. エージェントの作成
        print("\n🤖 専門エージェントを作成しています...")
        orchestrator.create_agents()
        
        # 4. マルチエージェント処理の実行
        topic = "Azure AI Foundry を使った生成AIアプリケーション開発のベストプラクティス"
        print(f"\n{'='*60}")
        print(f"📌 トピック: {topic}")
        print('='*60)
        
        results = orchestrator.orchestrate(topic)
        
        # 5. 結果の表示
        print(f"\n{'='*60}")
        print("📋 最終結果")
        print('='*60)
        
        print("\n【リサーチ結果】")
        print("-"*40)
        print(results["research"])
        
        print("\n【生成された記事】")
        print("-"*40)
        print(results["article"])
        
        print("\n【レビューコメント】")
        print("-"*40)
        print(results["review"])
        
    finally:
        # 6. クリーンアップ
        print(f"\n{'='*60}")
        print("🧹 クリーンアップしています...")
        orchestrator.cleanup()
    
    print("\n✅ 完了!")


if __name__ == "__main__":
    main()
