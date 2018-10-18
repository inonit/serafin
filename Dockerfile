FROM python:2.7

RUN apt-get update && apt-get install -y supervisor

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g bower

RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PYTHONUNBUFFERED 1
WORKDIR /code
COPY bower.json .bowerrc /code/
RUN bower --allow-root install
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY supervisor.conf /etc/supervisor/supervisor.conf
COPY . /code/
RUN python manage.py collectstatic --noinput
EXPOSE 8000
ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]
