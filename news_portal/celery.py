import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_portal.settings')
app = Celery('news_portal')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
     'weekly_new_post_notify': {
         'task': 'news_portal.tasks.weekly_new_post_notification',
         'schedule': crontab(minute='0', hour='8', day_of_week='mon'),
     },
 }