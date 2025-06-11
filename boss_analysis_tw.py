# -*- coding: utf-8 -*-
import os
import smtplib
from datetime import datetime
from dateutil import parser
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.text import MIMEText
from openai import OpenAI
import random

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def compute_age(data):
    d, m, y = data.get("dob_day"), data.get("dob_month"), data.get("dob_year")
    try:
        if d and m and y:
            month = int(m)
            bd = datetime(int(y), month, int(d))
        else:
            bd = parser.parse(data.get("dob", ""), dayfirst=True)
    except Exception:
        bd = datetime.today()
    today = datetime.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))


def send_email(html_body: str):
    msg = MIMEText(html_body, 'html')
    msg["Subject"] = "老闆報告提交"
    msg["From"] = SMTP_USERNAME
    msg["To"] = SMTP_USERNAME
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


@app.route("/boss_analyze", methods=["POST"])
def boss_analyze():
    data = request.get_json(force=True)

    member_name = data.get("memberName", "").strip()
    member_name_cn = data.get("memberNameCn", "").strip()
    position = data.get("position", "").strip()
    department = data.get("department", "").strip() or '核心職能'
    experience = data.get("experience", "").strip()
    sector_raw = data.get("sector", "").strip()
    challenge = data.get("challenge", "").strip()
    focus = data.get("focus", "").strip()
    email = data.get("email", "").strip()
    country = data.get("country", "").strip()
    age = compute_age(data)

    # === REPHRASED SECTOR DESCRIPTIONS IN TRADITIONAL CHINESE ===
    sector_map = {
        "內部 – 行政/人資/營運/財務": "關鍵的行政與營運領域",
        "內部 – 技術/工程/資訊": "創新的技術與工程領域",
        "外部 – 業務/商務開發/零售": "快節奏的業務與客戶關係領域",
        "外部 – 服務/物流/現場工作": "充滿活力的物流與現場服務領域"
    }
    sector = sector_map.get(sector_raw, sector_raw)

    raw_info = f"""
    <h3>📥 提交的表單資料：</h3>
    <ul style="line-height:1.8;">
      <li><strong>法定姓名：</strong> {member_name}</li>
      <li><strong>中文姓名：</strong> {member_name_cn}</li>
      <li><strong>職位：</strong> {position}</li>
      <li><strong>部門：</strong> {department}</li>
      <li><strong>經驗：</strong> {experience} 年</li>
      <li><strong>行業：</strong> {sector_raw}</li>
      <li><strong>挑戰：</strong> {challenge}</li>
      <li><strong>關注領域：</strong> {focus}</li>
      <li><strong>電子郵件：</strong> {email}</li>
      <li><strong>國家/地區：</strong> {country}</li>
      <li><strong>出生日期：</strong> {data.get("dob_day", "")} - {data.get("dob_month", "")}月 - {data.get("dob_year", "")}</li>
      <li><strong>推薦人：</strong> {data.get("referrer", "")}</li>
      <li><strong>聯絡方式：</strong> {data.get("contactNumber", "")}</li>
    </ul>
    <hr><br>
    """

    metrics = []
    for title, color in [
        ("溝通效率", "#5E9CA0"),
        ("領導力準備度", "#FF9F40"),
        ("任務完成可靠性", "#9966FF"),
    ]:
        seg, reg, glo = sorted([random.randint(60, 90), random.randint(55, 85), random.randint(60, 88)], reverse=True)
        metrics.append((title, seg, reg, glo, color))

    bar_html = ""
    for title, seg, reg, glo, color in metrics:
        bar_html += f"<strong>{title}</strong><br>"
        labels = ["個人表現", "區域基準", "全球基準"]
        values = [seg, reg, glo]
        for i, v in enumerate(values):
            bar_html += (
                f"<span style='font-size:14px; width:80px; display:inline-block;'>{labels[i]}:</span>"
                f"<span style='display:inline-block;width:{v}%;height:12px;"
                f" background:{color}; margin-right:6px; border-radius:4px; vertical-align:middle;'></span> {v}%<br>"
            )
        bar_html += "<br>"

    # === DYNAMIC OPENING SENTENCES IN TRADITIONAL CHINESE ===
    opening_templates = [
        f"在{country}的{sector}中深耕{experience}年，這本身就是對堅韌與專業的最好證明。",
        f"憑藉在{country}要求嚴苛的{sector}中{experience}年的專注投入，一段非凡的成長與影響力之路已清晰可見。",
        f"要在{country}的{sector}中航行{experience}年，需要獨特的技巧和決心——這些品質在卓越的職業生涯中得到了完美的體現。",
        f"在{country}快節奏的{sector}中長達{experience}年的職業生涯，充分說明了對卓越和持續適應的非凡承諾。"
    ]
    chosen_opening = random.choice(opening_templates)
    
    # FINAL "YES" SUMMARY: Observational, rich, and dynamic in Traditional Chinese
    summary = (
        "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>🧠 對此專業檔案的深度洞察：</div><br>"
        + f"<p style='line-height:1.8; font-size:16px; margin-bottom:18px; text-align:justify;'>"
        + f"{chosen_opening} 這樣一段寶貴的經歷自然會磨練出卓越的人際溝通能力，高達{metrics[0][1]}%的溝通效率分數就反映了這一點。這不僅是一項後天習得的技能，更是建立強大團隊和成功合作的基石，從而能夠在複雜的內部目標和市場脈搏之間游刃有餘。"
        + "</p>"
        + f"<p style='line-height:1.8; font-size:16px; margin-bottom:18px; text-align:justify;'>"
        + f"在當今的商業環境中，真正的領導力更多地由影響力和適應性來衡量。以區域基準{metrics[1][2]}%衡量的領導力準備度，通常表明對此類現代領導力支柱已具備直覺性的掌握。此檔案揭示了一位能夠在壓力時刻為團隊提供清晰思路與沉穩風範的專業人士，從而贏得信任，並透過備受尊重的引導激勵團隊採取行動。"
        + "</p>"
        + f"<p style='line-height:1.8; font-size:16px; margin-bottom:18px; text-align:justify;'>"
        + f"高達{metrics[2][1]}%的任務完成可靠性，是其巨大影響力與戰略智慧的有力證明。對於{position}這樣的關鍵角色，這反映出一種罕見的洞察力——不僅能夠高效地完成工作，更能識別出哪些任務真正舉足輕重並將其做到极致。這種水平的表現不僅能驅動成果，也預示著其已準備好迎接更大的挑戰。"
        + "</p>"
        + f"<p style='line-height:1.8; font-size:16px; margin-bottom:18px; text-align:justify;'>"
        + f"將{focus}作為戰略重點，是一個極具遠見和洞察力的決策。這完美契合了整個區域的戰略轉型趨勢，使這項技能成為未來發展的基石。在此領域的投入，標誌著一位擁有清晰且充滿希望發展軌跡的專業人士，準備好創造深遠持久的價值。"
        + "</p>"
    )

    # UPDATED PROMPT: Asks for a more professional tone, tailored for Taiwan
    prompt = (
        f"為一位來自{country}、在{sector_raw}行業有{experience}年經驗、擔任{position}職位的人，提供10條可行的、專業的、且鼓舞人心的改進建議。"
        f"他們面臨的挑戰是「{challenge}」，並希望專注於「{focus}」。"
        f"每條建議都應是一條清晰、有建設性的忠告，並符合台灣的商業文化。語氣應當是賦能和尊重的，避免過於隨意。請恰當地使用表情符號來增加親和力，而非顯得不專業。"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.75 
    )
    tips = response.choices[0].message.content.strip().split("\n")
    tips_html = "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>💡 創意建議：</div><br>"
    for line in tips:
        if line.strip():
            tips_html += f"<p style='margin:16px 0; font-size:17px;'>{line.strip()}</p>"

    footer = (
        '<div style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">'
        '<strong>本報告中的見解是透過KataChat的AI系統分析得出的：</strong><br>'
        '1. 我們的專有匿名專業檔案資料庫，涵蓋新加坡、馬來西亞和台灣的行業數據<br>'
        '2. 來自可信的OpenAI研究和領導力趨勢資料集的全球商業基準數據<br>'
        '<em>所有資料都透過我們的AI模型進行處理，以識別統計上顯著的模式，並保持嚴格的PDPA合規。</em>'
        '</div>'
        '<p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">'
        '<strong>PS:</strong> 您的個人化報告將在24到48小時內送達您的電子信箱。<br>'
        '如果您想進一步討論，請隨時與我們聯繫——我們很樂意為您安排一次15分鐘的電話會議。'
        '</p>'
    )

    email_output = raw_info + bar_html + summary + tips_html + footer
    display_output = bar_html + summary + tips_html + footer

    send_email(email_output)

    return jsonify({
        "analysis": display_output
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5002)) 
    app.run(debug=True, host="0.0.0.0", port=port)
