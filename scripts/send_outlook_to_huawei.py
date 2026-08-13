#!/usr/bin/env python3
"""一次性发送脚本：将 morning-brief-outlook.html 发送到指定邮箱"""
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILE = os.path.join(BASE, "morning-brief-outlook.html")

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = "2027674540@qq.com"
SMTP_PASS = "rsdsoaxfejsjbcjc"
TO_EMAIL = "Ira.xiaoyi@huawei.com"
SUBJECT = "Ira 早报 · 2026-08-12 · 国际6/国内7精选"

# 读取HTML
with open(HTML_FILE, "r", encoding="utf-8") as f:
    html_body = f.read()

msg = MIMEMultipart("alternative")
msg["From"] = SMTP_USER
msg["To"] = TO_EMAIL
msg["Subject"] = Header(SUBJECT, "utf-8")

# 添加纯文本备选（部分客户端不支持 HTML）
text_body = "Ira 早报 2026-08-12：国际6篇、国内7篇。请在 HTML 邮件客户端查看完整版。"
msg.attach(MIMEText(text_body, "plain", "utf-8"))
msg.attach(MIMEText(html_body, "html", "utf-8"))

try:
    print(f"📤 正在连接 SMTP {SMTP_HOST}:{SMTP_PORT} ...")
    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
    server.login(SMTP_USER, SMTP_PASS)
    print(f"✅ 登录成功，发往 {TO_EMAIL}")
    server.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())
    server.quit()
    print(f"✅ 邮件发送成功！")
    print(f"   主题: {SUBJECT}")
    print(f"   收件人: {TO_EMAIL}")
except Exception as e:
    print(f"❌ 发送失败: {e}")
    sys.exit(1)