import gradio as gr
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from snownlp import SnowNLP
import uuid
import os

# 中文字體支援（Windows）
matplotlib.rc('font', family='Microsoft JhengHei')

# 根據美味指數產生評語
def generate_comment(score):
    if score >= 9:
        return "超級推薦！美味到不行～"
    elif score >= 7:
        return "很好吃，值得一試"
    elif score >= 5:
        return "還不錯，可以嚐嚐"
    elif score >= 3:
        return "普通，見仁見智"
    else:
        return "不太推薦，可能踩雷"

# 分析主邏輯
def analyze_food(file):
    if file is None:
        return "請上傳 CSV 檔案", None, None

    df = pd.read_csv(file.name)
    if "食物名稱" not in df.columns or "小語" not in df.columns:
        return "❌ 錯誤：CSV 檔案必須包含「食物名稱」與「小語」欄位", None, None

    # 美味指數分析
    df["美味指數"] = df["小語"].apply(lambda text: round(SnowNLP(str(text)).sentiments * 9 + 1, 1))
    df["評語"] = df["美味指數"].apply(generate_comment)

    # 儲存分析後 CSV
    csv_output = f"food_result_{uuid.uuid4().hex}.csv"
    df.to_csv(csv_output, index=False, encoding="utf-8-sig")

    # 畫圖表
    plt.figure(figsize=(10, 5))
    plt.bar(df["食物名稱"], df["美味指數"], color='orange')
    plt.ylim(0, 10)
    plt.ylabel("美味指數 (1~10)")
    plt.title("🍜 食物推薦分析圖")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plot_path = f"food_chart_{uuid.uuid4().hex}.png"
    plt.savefig(plot_path)
    plt.close()

    return "✅ 分析完成！以下是結果：", csv_output, plot_path

# 清除欄位
def clear_all():
    return None, "", None, None

# Gradio UI
with gr.Blocks(title="美食推薦分析網站") as demo:
    gr.Markdown("## 🍽️ 美食推薦分析網站")
    gr.Markdown("上傳包含「食物名稱」與「小語」欄位的 CSV，系統會分析出每道菜的推薦指數與圖表！")

    with gr.Row():
        csv_input = gr.File(label="📎 上傳 CSV 檔案", file_types=[".csv"])
        analyze_btn = gr.Button("🚀 開始分析", variant="primary")
        clear_btn = gr.Button("🧹 清除")

    with gr.Row():
        status_text = gr.Textbox(label="狀態", interactive=False)
    
    with gr.Row():
        download_csv = gr.File(label="⬇️ 分析後 CSV", interactive=False)
        download_plot = gr.Image(label="📊 分析圖表", interactive=False)

    analyze_btn.click(fn=analyze_food, inputs=[csv_input], outputs=[status_text, download_csv, download_plot])
    clear_btn.click(fn=clear_all, inputs=[], outputs=[csv_input, status_text, download_csv, download_plot])

# 啟動網站
if __name__ == "__main__":
    demo.launch()
