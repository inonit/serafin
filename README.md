# SERAF Røykeslutt
_SERAF Smoke free_

[SERAF](http://www.med.uio.no/klinmed/english/research/centres/seraf/) is the Norwegian Centre for Addiction Research at the University of Oslo. SERAF Smoke free is a web application to help people quit smoking, while providing SERAF with research data.

## Prerequisites

    sudo apt-get install python python-virtualenv python-pip python-dev libjpeg8-dev zlib1g-dev libyaml-dev redis-server

(or equivalent)

Clone the project with submodules:

    git clone --recursive git@github.com:inonit/seraf.git

## Dependencies

    pip install -r requirements.txt

## Project rules

- Follow the [Inonit Coding standards](http://inonit.no/media/Codingstandards.pdf)
- Follow the [Inonit Developer workflow routines](http://inonit.no/media/Developerworkflowroutines.pdf)

## Project description
Our priorities for this project is:

a. Build the functionality that SERAF needs to cover their needs for a program to help people quit smoking, and to monitor the results of participants as test subjects. Specifically, SERAF wants to see if "slip management" is effective, through e.g. automated SMS follow-up to participants in the test group who do not follow the program as intended.

b. Make it general enough for other mainly academic use in the future. Examples could include similar self-help programs, or e-learning and online courses. We intend to release the base software under a free software licence once it's done.

To accomplish this, the system will be built in a modular way, with a high degree of separation between components.

### Users app
Uses a customized anomymous user model with common contrib.auth functions and handles login through generation of a personal login code for each user and part (day) of the program. Backup login through id and password.

Fields past common User model fields could be set in a key: value store for *general use* of the system. Preferably, field archetypes are defined by an admin, but behave somewhat like normal fields after this. Implementation ideas in [this thread](https://github.com/inonit/seraf/issues/9). However, for SERAFs use case, custom user fields are probably *not* needed.

### Vault app
The vault stores personally identifiable data like e-mail and phone number. It will be separated to a secure server if research councils dictate so. The vault is connected to the SMS app and sends out e-mails, but only does so at the request of the main system, and only by user ID.

### Tasker app
Handles scheduling of events, mainly triggering each day of the program and slip management. Scheduling is based on [Huey](https://github.com/coleifer/huey), it's simple and adequate.

To run the Huey consumer, install Redis:

    sudo apt-get install redis-server
    ./manage.py run_huey

### Events app
Contains receivers for Django signals that generate logging events for any and all information that may be of interest to the researchers.

### System app
Maintains a model of the Program, with the top level represented as a schedule of Parts, the path and logic of each Part as a graph of Content nodes, most of them Pages, and each Page as an ordered list of content items.

### Plumbing app
The administrator design of the Parts uses [jsPlumb](http://jsplumbtoolkit.com/demo/statemachine/jquery.html) and AngularJS. We intend to redesign this for general public use, help is appreciated.

### Content app
A simple content management system for snippets of Text, Media and Forms. Snippets of Content will likely handle how they are displayed, and in the case of Forms, save the information.

Content management is done through an Angular widget, and stored in a [JSONField](https://github.com/bradjasper/django-jsonfield). See [thoughts on content](https://github.com/inonit/seraf/blob/content/content/thoughts_on_content.md) for details.
