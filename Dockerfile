FROM python:2.7

RUN apt-get update && \
    apt-get upgrade -y

RUN apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g bower

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY bower.json .bowerrc /code/
RUN cd /code/ && bower --allow-root install
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
COPY serafin/local_settings.prod.py /code/serafin/local_settings.py
COPY supervisor.conf /etc/supervisor/supervisor.conf
EXPOSE 8000
ENTRYPOINT ["/code/docker-entrypoint.sh"]
