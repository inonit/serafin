# Serafin
_An interactive content creation kit_

Serafin is a platform that gives content-builders a set of flexible tools, allowing them to create a diverse set of data- and logic-driven web sites of any complexity. Examples include:

- Web forms and questionaires
- Self-help programs
- E-learning programs
- Dynamic websites with a complex underlying logic

Serafin was developed by [Inonit AS](http://inonit.no/) for [SERAF](http://www.med.uio.no/klinmed/english/research/centres/seraf/), the Norwegian Centre for Addiction Research at the University of Oslo, in order to create a program to help users stop smoking while exploring therapeutic techniques, and gather research data.

Program flow is controlled on different levels. Sessions may be put into sequence, inviting registered users to follow the program day by day, or they may be accessed manually. Sessions are built as a series of pages and other events, allowing the users' path to be controlled by their own choices. Pages and other content may present text, media or forms for the user to fill out.


## Local development setup

The preferred method for running Serafin for development is through docker-compose. It will set up complete environment for you, including PostgreSQL, Redis and a python container with the Django development server.

Code changes will be reflected in the app

Install [docker](https://docs.docker.com/engine/installation/) and [docker-compose](https://docs.docker.com/compose/install/).

Run docker-compose to build the environment:

    $ docker-compose up

Optionally you can use the `-d` flag to keep them running in the background.

Run database migrations (first time, but may be needed after model changes):

    $ docker exec -it serafin_app_1 ./manage.py migrate 
    $ docker exec -it serafin_app_1 ./manage.py migrate --database vault

Create a local admin user (first time only):

    $ docker exec -it serafin_app_1 ./manage.py createsuperuser

Run other Django management commands the same way.
