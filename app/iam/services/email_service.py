import logging

logger = logging.getLogger(__name__)


class EmailService:
    def send_activation_email(self, email: str, username: str, activation_link: str) -> None:
        subject = "Activate your account"
        html_content = f"""
        <h1>Welcome, {username}!</h1>
        <p>Please click the link below to activate your account:</p>
        <a href="{activation_link}">Activate Account</a>
        <p>This link will expire in 24 hours.</p>
        """

        # provider.send(to=email, subject=subject, html=html_content)

        text = "\n" + "-" * 20 + html_content + "\n" + "-" * 20
        logger.debug(text)
        logger.info(f"Activation email sent to {email}")
