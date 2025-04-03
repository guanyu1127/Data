import os
from datetime import datetime
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF
import google.generativeai as genai

# 載入環境變數
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
#HW4 開始
def get_chinese_font_file():
    """尋找可用的中文字型"""
    fonts_path = r"C:\\Windows\\Fonts"
    candidates = ["kaiu.ttf", "msjh.ttf", "simsun.ttc", "NotoSansCJK-Regular.ttc"]
    for font in candidates:
        font_path = os.path.join(fonts_path, font)
        if os.path.exists(font_path):
            return os.path.abspath(font_path)
    return None

def generate_pdf(text, df):
    """生成包含 LLM 分析結果與表格的 PDF"""
    pdf = FPDF()
    pdf.add_page()
    chinese_font = get_chinese_font_file()
    if not chinese_font:
        return "錯誤：未找到中文字型"
    pdf.add_font("ChineseFont", "", chinese_font, uni=True)
    pdf.set_font("ChineseFont", "", 12)
    
    pdf.multi_cell(0, 10, text)
    pdf.ln(10)
    
    if df is not None:
        create_table(pdf, df)
    
    filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

def create_table(pdf, df):
    """在 PDF 中繪製表格"""
    pdf.set_font("ChineseFont", "", 10)
    col_width = pdf.w / (len(df.columns) + 1)
    pdf.set_fill_color(200, 200, 200)
    for col in df.columns:
        pdf.cell(col_width, 10, col, border=1, align="C", fill=True)
    pdf.ln()
    
    fill = False
    for _, row in df.iterrows():
        pdf.set_fill_color(230, 240, 255 if fill else 255, 255, 255)
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1, align="C", fill=True)
        pdf.ln()
        fill = not fill

def gradio_handler(pdf_file, user_prompt):
    """處理 PDF 上傳與 LLM 分析"""
    if pdf_file is not None:
        text = "已上傳 PDF: " + pdf_file.name
    else:
        text = "未提供 PDF，僅進行 LLM 分析"
    
    prompt = f"請根據以下內容進行分析：\n{user_prompt}\n\n{pdf_file.name if pdf_file else ''}"
    response = genai.chat(prompt)
    response_text = response.text.strip()
    
    df = pd.DataFrame({"分析結果": response_text.split("\n")})
    pdf_path = generate_pdf(response_text, df)
    
    return response_text, pdf_path

default_prompt = """請根據以下規則分析公車運量數據：
1. 運量變化趨勢
2. 熱門與冷門路線
3. 季節性影響
4. 業者比較
5. 提出改善建議
"""

with gr.Blocks() as demo:
    gr.Markdown("# 公車數據分析器")
    pdf_input = gr.File(label="上傳 PDF 檔案")
    user_input = gr.Textbox(label="請輸入分析指令", lines=5, value=default_prompt)
    output_text = gr.Textbox(label="分析結果", interactive=False)
    output_pdf = gr.File(label="下載 PDF 報告")
    submit_button = gr.Button("開始分析")
    submit_button.click(fn=gradio_handler, inputs=[pdf_input, user_input], outputs=[output_text, output_pdf])

demo.launch(share=True)
#HW4 結束
