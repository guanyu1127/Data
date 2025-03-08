import os
import asyncio
import pandas as pd
from dotenv import load_dotenv
import io

# 根據你的專案結構調整下列 import
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer

load_dotenv()

async def process_chunk(chunk, start_idx, total_records, model_client, termination_condition):
    """
    處理單一批次資料：
      - 轉換數據為字典格式
      - 根據使用者健康數據提供個人化飲食建議
      - 使用 MultimodalWebSurfer 來搜尋最新的營養建議
      - 回應包含完整建議與最新健康資訊
    """
    chunk_data = chunk.to_dict(orient='records')
    prompt = (
        f"目前正在處理第 {start_idx} 至 {start_idx + len(chunk) - 1} 筆資料（共 {total_records} 筆）。\n"
        f"以下為該批次資料:\n{chunk_data}\n\n"
        "請根據以上健康數據提供完整的健康飲食建議。\n"
        "請特別注意：\n"
        "  1. 分析使用者的年齡、體重、飲食習慣，並提供個人化的健康飲食建議；\n"
        "  2. 請 MultimodalWebSurfer 搜尋外部網站，找出最新的營養與健康飲食建議，\n"
        "     並將搜尋結果整合進回覆中；\n"
        "  3. 最後請提供具體的飲食計劃與推薦食物，並附上相關參考資訊。\n"
        "請各代理人協同合作，提供一份完整且具參考價值的健康飲食建議。"
    )
    
    # 為每個批次建立新的 agent 與 team 實例
    local_data_agent = AssistantAgent("data_agent", model_client)
    local_web_surfer = MultimodalWebSurfer("web_surfer", model_client)
    local_assistant = AssistantAgent("assistant", model_client)
    local_user_proxy = UserProxyAgent("user_proxy")
    local_team = RoundRobinGroupChat(
        [local_data_agent, local_web_surfer, local_assistant, local_user_proxy],
        termination_condition=termination_condition
    )
    
    messages = []
    async for event in local_team.run_stream(task=prompt):
        if isinstance(event, TextMessage):
            print(f"[{event.source}] => {event.content}\n")
            messages.append({
                "batch_start": start_idx,
                "batch_end": start_idx + len(chunk) - 1,
                "source": event.source,
                "content": event.content,
                "type": event.type,
                "prompt_tokens": event.models_usage.prompt_tokens if event.models_usage else None,
                "completion_tokens": event.models_usage.completion_tokens if event.models_usage else None
            })
    return messages

async def main():
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("請檢查 .env 檔案中的 GEMINI_API_KEY。")
        return

    # 初始化模型用戶端 (示範使用 gemini-2.0-flash)
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=gemini_api_key,
    )
    
    termination_condition = TextMentionTermination("exit")
    
    # 使用 pandas 以 chunksize 方式讀取 CSV 檔案
    csv_file_path = "user_health_data.csv"
    chunk_size = 1000
    chunks = list(pd.read_csv(csv_file_path, chunksize=chunk_size))
    total_records = sum(chunk.shape[0] for chunk in chunks)
    
    # 利用 map 與 asyncio.gather 同時處理所有批次
    tasks = list(map(
        lambda idx_chunk: process_chunk(
            idx_chunk[1],
            idx_chunk[0] * chunk_size,
            total_records,
            model_client,
            termination_condition
        ),
        enumerate(chunks)
    ))
    
    results = await asyncio.gather(*tasks)
    
    # 將所有批次的訊息平坦化成一個清單
    all_messages = [msg for batch in results for msg in batch]
    
    # 將對話紀錄整理成 DataFrame 並存成 CSV
    df_log = pd.DataFrame(all_messages)
    output_file = "diet_recommendations_log.csv"
    df_log.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"已將所有對話紀錄輸出為 {output_file}")

if __name__ == '__main__':
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
