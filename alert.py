import smtplib
import logging
import pandas as pd
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import create_engine

# ── Configuration ──────────────────────────────────────────
DB_USER       = "root"
DB_PASSWORD   = "Password"
DB_HOST       = "localhost"
DB_NAME       = "olist"

EMAIL_SENDER   = "your_email@gmail.com"    # your Gmail address
EMAIL_PASSWORD = "abcd efgh ijkl mnop"     # your 16-char app password
EMAIL_RECEIVER = "your_email@gmail.com"    # can be same as sender

THRESHOLD      = 10.0                      # alert if late_pct exceeds this
LOG_FILE       = r"C:\Users\Rutuja\Downloads\archive\alert_log.txt"

# ── Logging setup ──────────────────────────────────────────
logging.basicConfig(
    filename = LOG_FILE,
    level    = logging.INFO,
    format   = "%(asctime)s — %(message)s"
)

# ── Connect to MySQL ───────────────────────────────────────
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

# ── Run KPI query ──────────────────────────────────────────
def check_late_deliveries():
    df = pd.read_sql("""
        SELECT
            DATE_FORMAT(purchase_timestamp, '%%Y-%%u') AS week,
            COUNT(*) AS total_orders,
            SUM(CASE WHEN delivered_customer_at > estimated_delivery
                THEN 1 ELSE 0 END) AS late_orders,
            ROUND(100.0 * SUM(CASE WHEN delivered_customer_at > estimated_delivery
                THEN 1 ELSE 0 END) / COUNT(*), 1) AS late_pct
        FROM orders
        WHERE order_status = 'delivered'
        AND delivered_customer_at IS NOT NULL
        GROUP BY DATE_FORMAT(purchase_timestamp, '%%Y-%%u')
        HAVING COUNT(*) >= 10
        ORDER BY late_pct DESC
    """, engine)
    return df

# ── Send email ─────────────────────────────────────────────
def send_alert(breaching_weeks):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"⚠️ Late Delivery Alert — {len(breaching_weeks)} weeks above {THRESHOLD}%"
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECEIVER

    # Build table rows
    rows = ""
    for _, row in breaching_weeks.iterrows():
        rows += f"""
        <tr>
            <td style='padding:8px;border:1px solid #ddd'>{row['week']}</td>
            <td style='padding:8px;border:1px solid #ddd'>{int(row['total_orders'])}</td>
            <td style='padding:8px;border:1px solid #ddd'>{int(row['late_orders'])}</td>
            <td style='padding:8px;border:1px solid #ddd;color:red'><b>{row['late_pct']}%</b></td>
        </tr>
        """

    html = f"""
    <html><body>
    <h2 style='color:#cc0000'>⚠️ Late Delivery Threshold Breached</h2>
    <p>The following weeks exceeded the <b>{THRESHOLD}%</b> late delivery threshold:</p>
    <table style='border-collapse:collapse;width:100%'>
        <tr style='background:#f2f2f2'>
            <th style='padding:8px;border:1px solid #ddd'>Week</th>
            <th style='padding:8px;border:1px solid #ddd'>Total Orders</th>
            <th style='padding:8px;border:1px solid #ddd'>Late Orders</th>
            <th style='padding:8px;border:1px solid #ddd'>Late %</th>
        </tr>
        {rows}
    </table>
    <br>
    <p style='color:gray;font-size:12px'>
        Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 
        by Olist Analytics Alert System
    </p>
    </body></html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

# ── Main ───────────────────────────────────────────────────
def main():
    print(f"Running alert check — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("Alert check started")

    df = check_late_deliveries()
    breaching = df[df["late_pct"] > THRESHOLD]

    if breaching.empty:
        msg = f"✅ All clear — no weeks above {THRESHOLD}% late rate"
        print(msg)
        logging.info(msg)
    else:
        msg = f"⚠️ {len(breaching)} weeks breached {THRESHOLD}% threshold — sending alert"
        print(msg)
        logging.info(msg)
        send_alert(breaching)
        print("📧 Alert email sent successfully")
        logging.info("Alert email sent")

if __name__ == "__main__":
    main()
