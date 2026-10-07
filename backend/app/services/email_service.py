import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME
        self.is_configured = bool(self.host and self.user and self.password)

    def _send_email(self, to_email: str, subject: str, html_content: str):
        if not self.is_configured:
            logger.warning(f"Email system not configured. Skipping email to {to_email}")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email

        part = MIMEText(html_content, "html")
        msg.attach(part)

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            logger.info(f"Successfully sent email to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_invitation_email(self, to_email: str, inviter_name: str, person_name: str, family_name: str, frontend_url: str):
        subject = f"{inviter_name} invited you to join FamilyNest"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #6d4c41;">Welcome to FamilyNest! 🌳</h2>
            <p>Hi there,</p>
            <p><strong>{inviter_name}</strong> has invited you to join the <strong>{family_name}</strong> family tree and claim your profile as <strong>{person_name}</strong>.</p>
            <p>FamilyNest is a private, secure space for your family to share history, photos, and memories.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{frontend_url}/register" style="background-color: #8d6e63; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Create Your Account
                </a>
            </div>
            <p>Please use this exact email address (<strong>{to_email}</strong>) when registering so we can link your profile automatically.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;" />
            <p style="font-size: 12px; color: #888;">If you don't know {inviter_name}, you can safely ignore this email.</p>
        </div>
        """
        return self._send_email(to_email, subject, html_content)

    def send_otp_email(self, to_email: str, otp: str, context: str = "verification"):
        subject = "FamilyNest Verification Code" if context == "verification" else "FamilyNest Password Reset Code"
        action = "verify your email address" if context == "verification" else "reset your password"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #6d4c41;">FamilyNest Security 🔒</h2>
            <p>Hi there,</p>
            <p>Here is your 6-digit code to {action}:</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="background-color: #f5f5f5; border: 1px solid #ddd; font-family: monospace; font-size: 32px; letter-spacing: 5px; padding: 15px 30px; border-radius: 6px; display: inline-block;">
                    {otp}
                </span>
            </div>
            <p style="color: #666; font-size: 14px;">This code will expire in 15 minutes. Do not share this code with anyone.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;" />
            <p style="font-size: 12px; color: #888;">If you didn't request this, you can safely ignore this email.</p>
        </div>
        """
        return self._send_email(to_email, subject, html_content)

email_service = EmailService()
