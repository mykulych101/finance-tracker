from django.core import mail
from django.test import TestCase

from users.tasks import send_email


class SendEmailTaskTests(TestCase):
    def test_renders_template_and_sends_to_recipients(self):
        send_email(
            subject="Activate your account",
            template="email/activation_email.html",
            recipients=["john@example.com"],
            context={"user_name": "John Doe", "activation_link": "https://example.com/activate/uid/token/"},
        )

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.subject, "Activate your account")
        self.assertEqual(sent.to, ["john@example.com"])
        self.assertIn("Hi John Doe,", sent.body)
        self.assertIn("https://example.com/activate/uid/token/", sent.body)

    def test_sends_to_every_recipient(self):
        send_email(
            subject="Activate your account",
            template="email/activation_email.html",
            recipients=["john@example.com", "jane@example.com"],
            context={"user_name": "John Doe", "activation_link": "https://example.com/activate/uid/token/"},
        )

        self.assertEqual(mail.outbox[0].to, ["john@example.com", "jane@example.com"])
