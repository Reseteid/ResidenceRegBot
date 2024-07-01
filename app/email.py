import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'residencebot@gmail.com'
EMAIL_PASSWORD = 'agwh feql gfsn yogg'

def generate_code_and_send_email(user_email):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = user_email
    msg['Subject'] = 'Код для восстановления пароля'

    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    msg.attach(MIMEText(f'Ваш код: {code}', 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, user_email, msg.as_string())
    return code
