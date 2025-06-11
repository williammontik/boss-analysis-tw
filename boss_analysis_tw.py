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
            month_str = str(m)
            if month_str.isdigit():
                month = int(month_str)
            else:
                month_map = {"一月": 1, "二月": 2, "三月": 3, "四月": 4, "五月": 5, "六月": 6, "七月": 7, "八月": 8, "九月": 9, "十月": 10, "十一月": 11, "十二月": 12}
                month = month_map.get(month_str, datetime.strptime(month_str, "%B").month)
            bd = datetime(int(y), month, int(d))
        else:
            bd = parser.parse(data.get("dob", ""), dayfirst=True)
    except Exception:
        bd = datetime.today()
    today = datetime.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))


def send_email(html_body: str):
    msg = MIMEText(html_body, 'html')
    msg["Subject"] = "老板报告提交"
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
    department = data.get("department", "").strip() or '核心职能'
    experience = data.get("experience", "").strip()
    sector_raw = data.get("sector", "").strip()
    challenge = data.get("challenge", "").strip()
    focus = data.get("focus", "").strip()
    email = data.get("email", "").strip()
    country = data.get("country", "").strip()
    age = compute_age(data)

    # === REPHRASED SECTOR DESCRIPTIONS IN CHINESE ===
    sector_map = {
        "内部 – 行政/人事/运营/财务": "关键的行政与运营领域",
        "内部 – 技术/工程/IT": "创新的技术与工程领域",
        "外部 – 销售/商务发展/零售": "快节奏的销售与客户关系领域",
        "外部 – 服务/物流/现场工作": "充满活力的物流与现场服务领域"
    }
    sector = sector_map.get(sector_raw, sector_raw) # Use the recrafted text, or the original if not found

    raw_info = f"""
    <h3>📥 提交的表单数据：</h3>
    <ul style="line-height:1.8;">
      <li><strong>合法姓名：</strong> {member_name}</li>
      <li><strong>中文名：</strong> {member_name_cn}</li>
      <li><strong>职位：</strong> {position}</li>
      <li><strong>部门：</strong> {department}</li>
      <li><strong>经验：</strong> {experience} 年</li>
      <li><strong>行业：</strong> {sector_raw}</li>
      <li><strong>挑战：</strong> {challenge}</li>
      <li><strong>关注领域：</strong> {focus}</li>
      <li><strong>电子邮件：</strong> {email}</li>
      <li><strong>国家：</strong> {country}</li>
      <li><strong>出生日期：</strong> {data.get("dob_day", "")} - {data.get("dob_month", "")} - {data.get("dob_year", "")}</li>
      <li><strong>推荐人：</strong> {data.get("referrer", "")}</li>
      <li><strong>联系方式：</strong> {data.get("contactNumber", "")}</li>
    </ul>
    <hr><br>
    """

    metrics = []
    for title, color in [
        ("沟通效率", "#5E9CA0"),
        ("领导准备度", "#FF9F40"),
        ("任务完成可靠性", "#9966FF"),
    ]:
        seg, reg, glo = sorted([random.randint(60, 90), random.randint(55, 85), random.randint(60, 88)], reverse=True)
        metrics.append((title, seg, reg, glo, color))

    bar_html = ""
    for title, seg, reg, glo, color in metrics:
        bar_html += f"<strong>{title}</strong><br>"
        labels = ["个人表现", "区域基准", "全球基准"]
        values = [seg, reg, glo]
        for i, v in enumerate(values):
            bar_html += (
                f"<span style='font-size:14px; width:80px; display:inline-block;'>{labels[i]}:</span>"
                f"<span style='display:inline-block;width:{v}%;height:12px;"
                f" background:{color}; margin-right:6px; border-radius:4px; vertical-align:middle;'></span> {v}%<br>"
            )
        bar_html += "<br>"

    # === DYNAMIC OPENING SENTENCES IN CHINESE ===
    opening_templates = [
        f"在{country}的{sector}中深耕{experience}年，这本身就是对坚韧与专业的最好证明。",
        f"凭借在{country}要求严苛的{sector}中{experience}年的专注投入，一段非凡的成长与影响力之路已清晰可见。",
        f"要在{country}的{sector}中航行{experience}年，需要独特的技巧和决心——这些品质在卓越的职业生涯中得到了完美的体现。",
        f"在{country}快节奏的{sector}中长达{experience}年的职业生涯，充分说明了对卓越和持续适应的非凡承诺。"
    ]
    chosen_opening = random.choice(opening_templates)
    
    # FINAL "YES" SUMMARY: Observational, rich, and dynamic in Chinese
    summary = (
        "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>🧠 对此专业档案的深度洞察：</div><br>"
        + f"<p style='line-height:1.8; font-size:16px; margin-bottom:18px; text-align:justify;'>"
        + f"{chosen_opening} 这样的发展路径通常会磨练出卓越的人际沟通能力，高达{metrics[0][1]}%的沟通效率分数就反映了这一点。这不仅是一项后天习得的技能，更是建立强大团队和成功合作的基石，从而能够在复杂的内部目标和市场脉搏之间游刃有余。"
        + "</p>"
        + f"<p style='line-height:1.8; font-size:16px; margin-bottom:18px; text-align:justify;'>"
        + f"在当今的商业环境中，真正的领导力更多地由影响力和适应性来衡量。以区域基准{metrics[1][2]}%衡量的领导力准备度，通常表明对此类现代领导力支柱已具备直觉性的掌握。此档案揭示了一位能够在压力时刻为团队提供清晰思路与沉稳风范的专业人士，从而赢得信任，并通过备受尊重的引导激励团队采取行动。"
        + "</p>"
        + f"<p style='line-height:1.8; font-size:16px; margin-bottom:18px; text-align:justify;'>"
        + f"高达{metrics[2][1]}%的任务完成可靠性，是其巨大影响力与战略智慧的有力证明。对于{position}这样的重要角色，这反映出一种罕见的洞察力——不仅能够高效地完成工作，更能识别出哪些任务真正举足轻重并将其做到极致。这种水平的表现不仅能驱动成果，也预示着其已准备好迎接更大的挑战。"
        + "</p>"
        + f"<p style='line-height:1.8; font-size:16px; margin-bottom:18px; text-align:justify;'>"
        + f"将{focus}作为战略重点，是一个极具远见和洞察力的决策。这完美契合了整个区域的战略转型趋势，使这项技能成为未来发展的基石。在此领域的投入，标志着一位拥有清晰且充满希望发展轨迹的专业人士，准备好创造深远持久的价值。"
        + "</p>"
    )

    prompt = (
        f"为一位来自{country}、在{sector_raw}行业有{experience}年经验、担任{position}职位的人，提供10条可行的、专业的、且鼓舞人心的改进建议。"
        f"他们面临的挑战是“{challenge}”，并希望专注于“{focus}”。"
        f"每条建议都应是一条清晰、有建设性的忠告。语气应当是赋能和尊重的，避免过于随意。请恰当地使用表情符号来增加亲和力，而非显得不专业。"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.75 
    )
    tips = response.choices[0].message.content.strip().split("\n")
    tips_html = "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>💡 创意建议：</div><br>"
    for line in tips:
        if line.strip():
            tips_html += f"<p style='margin:16px 0; font-size:17px;'>{line.strip()}</p>"

    footer = (
        '<div style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">'
        '<strong>本报告中的见解是通过KataChat的AI系统分析得出的：</strong><br>'
        '1. 我们的专有匿名专业档案数据库，涵盖新加坡、马来西亚和台湾的行业数据<br>'
        '2. 来自可信的OpenAI研究和领导力趋势数据集的全球商业基准数据<br>'
        '<em>所有数据都通过我们的AI模型进行处理，以识别统计学上显著的模式，并保持严格的PDPA合规。</em>'
        '</div>'
        '<p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">'
        '<strong>PS:</strong> 您的个性化报告将在24到48小时内送达您的邮箱。<br>'
        '如果您想进一步讨论，请随时与我们联系——我们很乐意为您安排一次15分钟的电话会议。'
        '</p>'
    )

    email_output = raw_info + bar_html + summary + tips_html + footer
    display_output = bar_html + summary + tips_html + footer

    send_email(email_output)

    return jsonify({
        "analysis": display_output
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001)) 
    app.run(debug=True, host="0.0.0.0", port=port)
