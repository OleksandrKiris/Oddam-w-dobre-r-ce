import smtplib
from email.mime.text import MIMEText

EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_HOST_USER = '832219569f3daa'
EMAIL_HOST_PASSWORD = '306138df5c1dc8'

msg = MIMEText('This is a test email.')
msg['Subject'] = 'Test Email'
msg['From'] = EMAIL_HOST_USER
msg['To'] = 'recipient@example.com'

with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    server.sendmail(msg['From'], [msg['To']], msg.as_string())

print("Test email sent")
