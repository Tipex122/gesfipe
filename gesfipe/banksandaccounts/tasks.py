from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time

@shared_task
def adding_task(x, y):
    return x + y

@shared_task
def message_task(message="Je suis le meilleur !"):
    print('Request: {0}'.format(message))


#####################  Celery - Redis ##################################

@shared_task(bind=True)
def my_task(self, seconds):
    progress_recorder = ProgressRecorder(self)
    result = 0
    for i in range(seconds):
        time.sleep(1)
        result += i
        print('Avancement barre de progression : {}'.format(result))
        progress_recorder.set_progress(i + 1, seconds)
        print('Progress_recorder : ---> {}'.format(progress_recorder.task))
    return result