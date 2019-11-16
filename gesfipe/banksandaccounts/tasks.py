from celery import shared_task

@shared_task
def adding_task(x, y):
    return x + y

@shared_task
def debug_task(message="Je suis le meilleur !"):
    print('Request: {0}'.format(message))
