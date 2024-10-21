import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email: str, subject: str, body: str):
    
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD")

    # Crea el objeto MIMEMultipart
    message = MIMEMultipart()
    message["From"] = gmail_user
    message["To"] = to_email
    message["Subject"] = subject

    # Añade el cuerpo del mensaje
    message.attach(MIMEText(body, "plain"))

    try:
        # Crea una conexión segura con el servidor SMTP de Gmail
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        
        # Inicia sesión en la cuenta
        server.login(gmail_user, gmail_password)
        
        # Envía el correo
        server.sendmail(gmail_user, to_email, message.as_string())
        server.close()

        print("Correo enviado exitosamente!")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")