FROM python:3.6

RUN apt-get update && apt-get install -y supervisor

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - && \
    apt-get install -y nodejs && \
	apt-get install -y npm && \
    npm install -g bower

RUN npm install quill-image-resize
	
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PYTHONUNBUFFERED 1
WORKDIR /code
COPY bower.json .bowerrc /code/
RUN bower --allow-root install
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install ptvsd
COPY supervisor.conf /etc/supervisor/supervisor.conf
COPY . /code/
COPY filer.base64.json /code/
COPY system.json /code/
RUN python manage.py collectstatic --noinput
EXPOSE 8000 5678
ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]
