import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Настройки
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "[EMAIL_ADDRESS]"
SENDER_PASSWORD = "[PASSWORD]"
RECIPIENT_EMAIL = "[EMAIL_ADDRESS]"

# Создаем сообщение
msg = MIMEMultipart()
msg['From'] = SENDER_EMAIL
msg['To'] = RECIPIENT_EMAIL
msg['Subject'] = "Тестовое письмо на Python"
msg.attach(MIMEText("Привет! Это тестовое сообщение, отправленное через SMTP.", "plain"))

try:
    # 1. Подключение к серверу
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()
    
    # 2. Перевод соединения в защищенный режим (STARTTLS)
    server.starttls()
    server.ehlo()
    
    # 3. Авторизация и отправка
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print("Письмо успешно отправлено!")

except Exception as e:
    print(f"Ошибка при отправке: {e}")

finally:
    server.quit()