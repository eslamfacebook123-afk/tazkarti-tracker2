import requests, smtplib, os, json, csv
from email.mime.text import MIMEText
from io import StringIO

API_URL  = "https://www.tazkarti.com/data/matches-list-json.json"
SHEET_ID = os.environ["SHEET_ID"]  # في GitHub Secrets اسمه SHEET_ID وقيمته: 1cf2yHUa4ACAIiRuCftf8QeMJZ7n48hATJxF5TmcUIiM
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_emails():
    r = requests.get(SHEET_URL, timeout=15)
    reader = csv.reader(StringIO(r.text))
    next(reader)
    emails = [row[1] for row in reader if len(row) > 1 and "@" in row[1]]
    return list(set(emails))

def send_email(to, subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"]    = os.environ["EMAIL_FROM"]
    msg["To"]      = to
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(os.environ["EMAIL_FROM"], os.environ["EMAIL_PASS"])
        s.send_message(msg)

def check():
    r = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    matches = json.loads(r.text)

    for m in matches:
        t1   = m.get("teamName1", "").lower()
        t2   = m.get("teamName2", "").lower()
        t1ar = m.get("teamNameAr1", "") or ""
        t2ar = m.get("teamNameAr2", "") or ""
        stad = m.get("stadiumName", "").lower()
        tour = m.get("tournament", {}).get("nameEn", "").lower()

        teams = [t1, t2, t1ar, t2ar]

        is_target = any(
            x in t for x in [
                "alithad", "ittihad", "الاتحاد",   # الاتحاد السكندري
                "telecom", "تليكوم",                # تليكوم
                "zamalek", "الزمالك",               # الزمالك ✅ جديد
                "ahly", "al ahly", "الأهلي",        # الأهلي  ✅ جديد
            ]
            for t in teams
        )

        is_basket = (
            "basket" in tour or
            "hassan" in stad or
            "سلة"   in (m.get("tournament", {}).get("nameAr", "") or "")
        )

        if is_target and is_basket:
            name1 = m.get("teamNameAr1") or m.get("teamName1", "")
            name2 = m.get("teamNameAr2") or m.get("teamName2", "")
            date  = m.get("kickOffTime", "")
            venue = m.get("stadiumName", "")

            emails = get_emails()
            print(f"✅ وجدنا ماتش! بنبعت لـ {len(emails)} إيميل...")

            for email in emails:
                try:
                    send_email(
                        email,
                        "🎟️ تذاكر ماتش سلة نزلت على تذكرتي!",
                        f"الماتش: {name1} vs {name2}\n"
                        f"التاريخ: {date}\n"
                        f"الاستاد: {venue}\n\n"
                        f"اشتري دلوقتي:\n"
                        f"https://tazkarti.com/#/matches\n\n"
                        f"--- تم الإشعار عبر نظام التتبع التلقائي ---"
                    )
                    print(f"  ✓ أُرسل إلى {email}")
                except Exception as e:
                    print(f"  ✗ فشل {email}: {e}")
            return

    print("لا يوجد تذاكر بعد...")

check()
