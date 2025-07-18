from time import sleep
from .celery_worker import celery_app

@celery_app.task
def send_email_task(to_email: str):
    print(f"[Worker] Отправляем email на {to_email}...")
    sleep(5)  # эмуляция долгой задачи
    print(f"[Worker] Email успешно отправлен на {to_email}")
    return {"status": "sent", "email": to_email}
