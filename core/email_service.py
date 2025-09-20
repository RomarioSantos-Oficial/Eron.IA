import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.sender_email = os.getenv('SENDER_EMAIL')

    def send_email(self, to_email, subject, body):
        if not all([self.smtp_username, self.smtp_password, self.sender_email]):
            print("Erro: Configurações de email não encontradas")
            return False

        try:
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = to_email
            message["Subject"] = subject

            message.attach(MIMEText(body, "html"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)

            return True
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False

    def send_confirmation_email(self, to_email, confirmation_token):
        subject = "Confirme seu email - Eron.IA"
        body = f"""
        <html>
            <body>
                <h2>Bem-vindo ao Eron.IA!</h2>
                <p>Para confirmar seu email, clique no link abaixo:</p>
                <p><a href="http://localhost:5000/confirm_email/{confirmation_token}">
                    Confirmar Email
                </a></p>
                <p>Se você não criou uma conta, ignore este email.</p>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, body)

    def send_reset_password_email(self, to_email, reset_token):
        subject = "Recuperação de Senha - Eron.IA"
        body = f"""
        <html>
            <body>
                <h2>Recuperação de Senha</h2>
                <p>Para criar uma nova senha, clique no link abaixo:</p>
                <p><a href="http://localhost:5000/reset_password/{reset_token}">
                    Criar Nova Senha
                </a></p>
                <p>Se você não solicitou a recuperação de senha, ignore este email.</p>
                <p>Este link expira em 1 hora.</p>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, body)
