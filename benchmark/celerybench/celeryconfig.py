BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASWORD = ""
BROKER_VHOST = ""

# defined backend for retrieving task results
CELERY_RESULT_BACKEND = "amqp"

# modules containing works that are available through celery
CELERY_IMPORTS = ("benchmark.celerybench.tasks", )

# to run, invoke 'celeryd -l info'
# celeryd -l info -I tasks,handlers
