import time

def send_notification_email(email, subject, body):
    print("Enviando email para:", email)
    print("Assunto: ", subject)
    print("Notificação: ", body)
    time.sleep(5)
    print("Ok!")
    return "OK"