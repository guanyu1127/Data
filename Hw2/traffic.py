import pandas as pd
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

# 讀取 API 金鑰
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

#HW2 開始

# 讀取 CSV
input_csv = "c5ec7a1f-3995-4c87-a59a-1f9a761570bf.csv"
df = pd.read_csv(input_csv)

# ========== 基本統計 ==========
speed_stats = {
    "速限_平均值": round(df["速限"].mean(), 1),
    "速限_最大值": int(df["速限"].max()),
    "速限_最小值": int(df["速限"].min())
}
division_counts = df["轄區分局"].value_counts().to_dict()
district_counts = df["行政區"].value_counts().to_dict()
direction_counts = df["拍攝行向"].value_counts().to_dict()

# ========== 組成提示詞 ==========
prompt = f"""
你是一位交通數據分析師，以下是交通科技執法設備的統計結果，請幫我寫一段 100 字內的數據摘要與改善建議：
1. 速限統計：平均速限 {speed_stats['速限_平均值']} km/h，最高 {speed_stats['速限_最大值']} km/h，最低 {speed_stats['速限_最小值']} km/h。
2. 轄區分局分布：{division_counts}
3. 行政區分布：{district_counts}
4. 拍攝行向分布：{direction_counts}
請加上一段具體改善交通安全的建議。
"""

# ========== Gemini 回覆 ==========
model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content(prompt)
suggestion = response.text.strip()

# ========== 匯出到新的 CSV ==========
output_data = {
    "速限_平均值": [speed_stats["速限_平均值"]],
    "速限_最大值": [speed_stats["速限_最大值"]],
    "速限_最小值": [speed_stats["速限_最小值"]],
    "轄區分局分布": [json.dumps(division_counts, ensure_ascii=False)],
    "行政區分布": [json.dumps(district_counts, ensure_ascii=False)],
    "拍攝行向分布": [json.dumps(direction_counts, ensure_ascii=False)],
    "Gemini建議": [suggestion]
}

output_df = pd.DataFrame(output_data)
output_csv = "traffic_analysis_result.csv"
output_df.to_csv(output_csv, index=False, encoding="utf-8-sig")

print("✅ 分析完成！結果已儲存為：traffic_analysis_result.csv")
#HW2 結束
