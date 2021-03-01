FROM python:3.6

RUN apt-get update && apt-get install -y supervisor

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - && \
    apt-get install -y nodejs && \
    apt-get install npm -y && \
    npm install -g bower
	
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
ENV PYTHONUNBUFFERED 1
WORKDIR /code
RUN mkdir -p node_modules/ 
COPY bower.json .bowerrc /code/
RUN bower --allow-root install
RUN sed -i 's/\/assets\/images\/ng-emoji-picker/\/static\/\/static\/lib\/ng-emoji-picker\/img/g' /code/staticfiles/lib/ng-emoji-picker/js/jquery.emojiarea.js
RUN sed -i 's/\/assets\/images\/ng-emoji-picker/\/static\/\/static\/lib\/ng-emoji-picker\/img/g' /code/staticfiles/lib/ng-emoji-picker/css/emoji.css
COPY idna-2.10-py2.py3-none-any.whl /code/
RUN pip install idna-2.10-py2.py3-none-any.whl
COPY django-multisite.tar.gz /code/
RUN tar xvzf django-multisite.tar.gz
RUN python django-multisite/setup.py install
RUN rm -fr django-multisite django-multisite.tar.gz django_multisite.egg-info
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install ptvsd
RUN pip install https://github.com/darklow/django-suit/tarball/v2
COPY supervisor.conf /etc/supervisor/supervisor.conf
COPY supervisor.deploy.conf /etc/supervisor/supervisor.deploy.conf
COPY . /code/
COPY filer.base64.json /code/
COPY system.json /code/
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN python manage.py collectstatic --noinput
CMD ["supervisord", "-c", "/etc/supervisor/supervisor.deploy.conf"]
