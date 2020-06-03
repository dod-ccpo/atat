from contextlib import contextmanager
import smtplib
import io
from email.message import EmailMessage


class MailConnection(object):
    def send(self, message):
        raise NotImplementedError()

    @property
    def messages(self):
        raise NotImplementedError()


class SMTPConnection(MailConnection):
    def __init__(self, server, port, username, password, use_tls=False, debug_smtp=0):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.debug_smtp = debug_smtp

    @contextmanager
    def _connected_host(self):
        host = None

        if self.use_tls:
            host = smtplib.SMTP(self.server, self.port)
            host.starttls()
        else:
            host = smtplib.SMTP_SSL(self.server, self.port)

        host.set_debuglevel(self.debug_smtp)
        host.login(self.username, self.password)

        yield host

        host.quit()

    @property
    def messages(self):
        return []

    def send(self, message):
        with self._connected_host() as host:
            host.send_message(message)


class RedisConnection(MailConnection):
    def __init__(self, redis, **kwargs):
        super().__init__(**kwargs)
        self.redis = redis
        self._reset()

    def _reset(self):
        self.redis.delete("atat_inbox")

    @property
    def messages(self):
        return [msg.decode() for msg in self.redis.lrange("atat_inbox", 0, -1)]

    def send(self, message):
        self.redis.lpush("atat_inbox", str(message))


class Mailer(object):
    def __init__(self, connection, sender):
        self.connection = connection
        self.sender = sender

    def _build_message(self, recipients, subject, body):
        msg = EmailMessage()
        msg.set_content(body)
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        return msg

    def _add_attachment(self, message, content, filename, maintype, subtype):
        with io.BytesIO(content) as bytes_:
            message.add_attachment(
                bytes_.read(), filename=filename, maintype=maintype, subtype=subtype
            )

    def send(self, recipients, subject, body, attachments=[]):
        """
        Send a message, optionally with attachments.
        Attachments should be provided as a list of dictionaries of the form:
        {
            content: bytes,
            maintype: string,
            subtype: string,
            filename: string,
        }
        """
        message = self._build_message(recipients, subject, body)
        if attachments:
            message.make_mixed()
            for attachment in attachments:
                self._add_attachment(
                    message,
                    content=attachment["content"],
                    filename=attachment["filename"],
                    maintype=attachment.get("maintype", "application"),
                    subtype=attachment.get("subtype", "octet-stream"),
                )
        self.connection.send(message)

    @property
    def messages(self):
        return self.connection.messages
