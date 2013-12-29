from django.conf import settings
from django.core.mail import get_connection
from celery.task import task


CONFIG = getattr(settings, 'EMAIL_TASK_CONFIG', {})
BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

TASK_CONFIG = {
    'name': 'email_send',
    'ignore_result': True,
    'queue': 'email',
    'max_retries': 5,
    'default_retry_delay': 180
}
TASK_CONFIG.update(CONFIG)


@task(**TASK_CONFIG)
def send_email(message, **kwargs):
    logger = send_email.get_logger()
    conn = get_connection(backend=BACKEND,
                          **kwargs.pop('_backend_init_kwargs', {}))
    try:
        result = conn.send_messages([message])
        logger.debug("Successfully sent email message to %r.", message.to)
        return result
    except Exception, e:
        logger.warning("Failed to send email message to %r, retrying.",
                       message.to)
        send_email.retry(exc=e)

SendEmailTask = send_email