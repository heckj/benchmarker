from celery.task import task

@task(serializer="json")
def add(x, y):
    return x + y
