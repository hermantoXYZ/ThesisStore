from django.core.mail.backends.smtp import EmailBackend
from app.models import WebSetting


class DynamicEmailBackend(EmailBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        setting = WebSetting.objects.first()
        if setting:
            self.host = setting.smtp_host
            self.port = setting.smtp_port
            self.username = setting.smtp_user
            self.password = setting.smtp_password
            self.use_tls = True
            self.from_email = setting.smtp_from_email or setting.smtp_user

    def send_messages(self, email_messages):
        for message in email_messages:
            if getattr(self, 'from_email', None):
                message.from_email = self.from_email
        return super().send_messages(email_messages)