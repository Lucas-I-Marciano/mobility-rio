import smtplib
import os
from email.message import EmailMessage
import dotenv
dotenv.load_dotenv()

def send_notification_email(recipient_email, email_subject, body_plain_text, body_html_content=None):
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    if not SENDER_EMAIL:
        print("Error: SENDER_EMAIL environment variable not set.")
        raise Exception("Error: SENDER_EMAIL environment variable not set.")
    GMAIL_APP_PASSWORD  = os.getenv("GMAIL_APP_PASSWORD")
    if not GMAIL_APP_PASSWORD :
        print("Error: GMAIL_APP_PASSWORD  environment variable not set.")
        raise Exception("Error: GMAIL_APP_PASSWORD  environment variable not set.")

    msg = EmailMessage()
    msg['Subject'] = email_subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg.set_content(body_plain_text)
    if body_html_content:
        msg.add_alternative(body_html_content, subtype='html')
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            print("Connected to Gmail SMTP server...")
            smtp_server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            print("Login successful...")
            # Send the email
            smtp_server.send_message(msg)
            print(f"Email sent successfully from {SENDER_EMAIL} to {recipient_email}!")

    except smtplib.SMTPAuthenticationError:
        print("Authentication Error: Check your email and App Password.")
        print("Make sure you are using an App Password and not your main password.")
        print("Verify the App Password was entered correctly (16 characters without spaces).")
    except smtplib.SMTPConnectError:
        print("Connection Error: Could not connect to the Gmail SMTP server.")
        print("Check your internet connection or if a firewall is blocking port 465.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
EMAIL_CONFIRMATION_SUBJECT = "Seu Alerta de Ônibus Rio foi Criado!"

EMAIL_CONFIRMATION_BODY_TEXT = """
Olá!

Seu alerta de ônibus foi criado com sucesso em nosso sistema.

Linha Monitorada: {bus_line}
Ponto Selecionado: (Lat: {stop_lat}, Lng: {stop_lng})
Janela de Horário (Hora Local SP): {start_time} - {end_time}

Fique atento! Nós te enviaremos um e-mail quando um ônibus da linha {bus_line} estiver a aproximadamente 10 minutos de chegar ao seu ponto dentro da janela de horário definida.

Obrigado por usar o Alerta Bus Rio!
"""

EMAIL_CONFIRMATION_BODY_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: sans-serif; line-height: 1.6; color: #333; }}
  .container {{ padding: 20px; border: 1px solid #ddd; border-radius: 5px; max-width: 600px; margin: 20px auto; background-color: #f9f9f9; }}
  h2 {{ color: #2a4b7c; }}
  strong {{ color: #0056b3; }}
  .footer {{ font-size: 0.9em; color: #777; margin-top: 15px; }}
</style>
</head>
<body>
<div class="container">
  <h2>Alerta de Ônibus Criado com Sucesso!</h2>
  <p>Olá!</p>
  <p>Seu alerta de ônibus foi registrado em nosso sistema com os seguintes detalhes:</p>
  <ul>
    <li><strong>Linha Monitorada:</strong> {bus_line}</li>
    <li><strong>Ponto Selecionado (Aprox.):</strong> Lat: {stop_lat}, Lng: {stop_lng}</li>
    <li><strong>Janela de Horário (Hora Local SP):</strong> {start_time} - {end_time}</li>
  </ul>
  <p>Fique atento(a)! Enviaremos uma notificação por e-mail quando um ônibus da linha <strong>{bus_line}</strong> estiver a aproximadamente <strong>10 minutos</strong> de chegar ao seu ponto, dentro da janela de horário que você definiu.</p>
  <hr>
  <p class="footer">Obrigado por usar o Alerta Bus Rio!</p>
</div>
</body>
</html>
"""

EMAIL_SEND_ALERT_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <style>
            body {{ font-family: sans-serif; line-height: 1.6; color: #333; }}
            .container {{ padding: 20px; border: 1px solid #ddd; border-radius: 5px; max-width: 600px; margin: 20px auto; background-color: #f9f9f9; }}
            h2 {{ color: #2a4b7c; }}
            strong {{ color: #0056b3; }}
            .footer {{ font-size: 0.9em; color: #777; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Ônibus Chegando!</h2>
            <p>Olá!</p>
            <p>O ônibus <strong>{bus_ordem}</strong> da linha <strong>{bus_line}</strong> está a aproximadamente <strong>{time} minutos</strong> de distância do ponto cadastrado.</p>
            <p>Por favor, dirija-se ao ponto de ônibus.</p>
            <hr>
            <p class="footer">Obrigado por usar o Alerta Bus Rio!</p>
        </div>
    </body>
</html>
"""

EMAIL_SEND_ALERT_PLAIN = """
Olá!

O ônibus {bus_ordem} da linha {bus_line} está a aproximadamente {time} minutos de distância do ponto cadastrado.

Por favor, dirija-se ao ponto de ônibus.

Obrigado por usar o Alerta Bus Rio!
"""
