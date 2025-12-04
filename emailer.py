import config
import smtplib
import sqlite3
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re


def regex_query(position_db, job_keyword_config):
    parts = job_keyword_config.split()
    for word in parts:
        pattern = re.escape(word)
        if not re.search(pattern, position_db, re.IGNORECASE):
            return False
    return True


def retrieve_jobs():
    conn = sqlite3.connect("vacancy.db")
    conn.create_function("REGEX_QUERY", 2, regex_query)
    cursor = conn.cursor()

    now_time = datetime.now().strftime("%d-%m-%Y")

    cursor.execute(
        """
        SELECT "position", "company", "link", "date_found", "job_site"
        FROM "jobs"
        WHERE "date_found" LIKE ?
        AND REGEX_QUERY(position, ?) = 1""",
        (f"{now_time}%", config.job_keyword),
    )

    data = cursor.fetchall()
    conn.close()
    return data


def report():
    now_time = datetime.now().strftime("%d-%m-%Y")
    jobs = retrieve_jobs()

    if not jobs:
        print("There's no new position today")
        return

    print(f"Found {len(jobs)} new vacancies. Preparing the email.")

    list_items = ""
    for job in jobs:
        position, company, link, date_found, job_site = job
        list_items += f"""
        <div style="display: flex; align-items: center; width: 100%; border-bottom: 1px solid #eeeeee; padding-bottom: 15px; margin-bottom: 15px;">
            
            <div style="text-align: left; padding-left: 12px;">
                <div style="font-size: 12px; color: #777777; margin-bottom: 4px;">
                    ☆ {date_found} on {job_site}
                </div>
                <div style="font-size: 18px; font-weight: bold; color: #333333; margin-bottom: 2px;">
                    {position}
                </div>
                <div style="font-size: 14px; color: #555555;">
                    {company}
                </div>
            </div>

            <div style="margin-left: auto; padding-left: 15px; padding-right: 12px;">
                <a href='{link}' style="background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 14px; font-weight: bold; display: inline-block; white-space: nowrap;">
                    Apply Here &rarr;
                </a>
            </div>
            
        </div>
        """

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                
                <h2 style="color: #2c3e50; text-align: center;">Vacancies Report</h2>
                
                <p style="font-size: 16px; color: #2c3e50; text-align:center;">
                    Hello, these are <b>{len(jobs)} new positions</b> on keyword: <i>{config.job_keyword}</i>
                </p>
                
                <hr style="border: 0; border-top: 1px solid #eee; margin: 17px 0;">
                
                {list_items}
                
                <p style="font-size: 16px; color: #2c3e50; text-align: center;">
                    <i>Have a great day! sincerely, harits.edu.bot [┐∵]┘</i>
                </p>
            </div>
        </body>
    </html>
    """

    message = MIMEMultipart()
    message["From"] = config.sender_email
    message["To"] = config.receiver_email
    message["Subject"] = f"Vacancies report: {len(jobs)} positions on ({now_time})"
    message.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(config.sender_email, config.sender_password)
        server.sendmail(config.sender_email, config.receiver_email, message.as_string())
        server.quit()
        print("Email succesfully sent")
    except Exception as Error:
        print(f">> Email failed: {Error}")


if __name__ == "__main__":
    print("Testing email from database")
    report()
