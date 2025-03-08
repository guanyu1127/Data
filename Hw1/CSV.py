import pandas as pd

# 創建測試資料
data = [
    {"User_ID": "001", "Age": 25, "Weight (kg)": 70, "Height (cm)": 175, "Dietary_Habits": "喜歡高熱量食物", "Health_Goals": "想減重"},
    {"User_ID": "002", "Age": 30, "Weight (kg)": 80, "Height (cm)": 180, "Dietary_Habits": "吃素", "Health_Goals": "想增肌"},
    {"User_ID": "003", "Age": 40, "Weight (kg)": 60, "Height (cm)": 165, "Dietary_Habits": "喜歡甜食", "Health_Goals": "維持健康"},
    {"User_ID": "004", "Age": 35, "Weight (kg)": 90, "Height (cm)": 170, "Dietary_Habits": "吃高蛋白飲食", "Health_Goals": "想增肌"},
    {"User_ID": "005", "Age": 28, "Weight (kg)": 55, "Height (cm)": 160, "Dietary_Habits": "地中海飲食", "Health_Goals": "提高能量"},
]

# 轉換為 DataFrame
df = pd.DataFrame(data)

# 儲存為 CSV 檔案
csv_filename = "user_health_data.csv"
df.to_csv(csv_filename, index=False, encoding="utf-8-sig")

print(f"已成功生成 {csv_filename}，可用於測試！")
