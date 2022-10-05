import json
import pika
import django
import os
import sys
import time
from django.core.mail import send_mail
from pika.exceptions import AMQPConnectionError


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()


def process_approval(ch, method, properties, body):
    content = json.loads(body)
    subject = "Your presentation has been accepted"
    name = content["presenter_name"]
    title = content["title"]
    message = f"{name}, we're happy to tell you that your presentation {title} has been accepted"
    from_email = "admin@conference.go"
    to_email = content["presenter_email"]
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[to_email],
        fail_silently=False,
    )


def process_rejection(ch, method, properties, body):
    content = json.loads(body)
    subject = "Your presentation has been rejected"
    name = content["presenter_name"]
    title = content["title"]
    message = f"{name}, we're sorry to tell you that your presentation {title} has been rejected"
    from_email = "admin@conference.go"
    to_email = content["presenter_email"]
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[to_email],
        fail_silently=False,
    )


while True:
    try:
        parameters = pika.ConnectionParameters(host="rabbitmq")
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue="presentation_approvals")
        channel.basic_consume(
            queue="presentation_approvals",
            on_message_callback=process_approval,
            auto_ack=True,
        )
        channel.queue_declare(queue="presentation_rejections")
        channel.basic_consume(
            queue="presentation_rejections",
            on_message_callback=process_rejection,
            auto_ack=True,
        )
        channel.start_consuming()
    except AMQPConnectionError:
        print("AMQP connection error")
        time.sleep(2.0)
