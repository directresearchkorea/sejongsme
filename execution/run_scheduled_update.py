import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
from datetime import datetime
import sys

# .env 파일에서 GMAIL_USER, GMAIL_APP_PASSWORD 읽어오기
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k.strip()] = v.strip()

GMAIL_USER = os.environ.get('GMAIL_USER', '')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')

def send_email(subject, body, to_email):
    gmail_user = GMAIL_USER
    gmail_password = GMAIL_APP_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, to_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    update_script = os.path.join(script_dir, "update_calendar_data.py")
    
    print(f"Running update script: {update_script}")
    
    try:
        # sys.executable instead of 'py' handles environments correctly if needed
        result = subprocess.run(
            [sys.executable, update_script], 
            cwd=project_dir, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        output = result.stdout
        status = "성공"
    except subprocess.CalledProcessError as e:
        output = str(e.stdout) + "\n" + str(e.stderr)
        status = "실패"
    except Exception as e:
        output = str(e)
        status = "실패"
        
    subject = f"[{status}] 세종시 산하기관 입찰정보 캘린더 업데이트 보고 ({datetime.now().strftime('%Y-%m-%d')})"
    body = f"""안녕하세요,

세종시 중소기업 지원정책/입찰정보 캘린더 데이터 업데이트 작업 결과입니다.

[작업 결과]
상태: {status}
실행 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[작업 로그 요약]
{output[:2000] + ('...' if len(output) > 2000 else '')}
"""
    send_email(subject, body, "yourfriendjay@gmail.com")

if __name__ == "__main__":
    main()
