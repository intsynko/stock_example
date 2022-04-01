import os
from threading import Thread

from src.stocks_generator import uwsgi_task
from src.app import app


if __name__ == "__main__":
    Thread(target=uwsgi_task).start()
    app.run(os.environ.get('HOST', '127.0.0.1'), os.environ.get('PORT', 5000))
