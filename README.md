# SERAF Røykeslutt
_SERAF Smoke free_

[SERAF](http://www.med.uio.no/klinmed/english/research/centres/seraf/) is the Norwegian Centre for Addiction Research at the University of Oslo. SERAF Smoke free is a web application to help people quit smoking, while providing SERAF with research data.

## Prerequisites

    sudo apt-get install python python-virtualenv python-pip python-dev libjpeg8-dev zlib1g-dev

(or equivalent)

## Dependencies

    pip install -r requirements.txt

## Test database

TBA

## Project rules

- Follow the [Inonit Coding standards](http://inonit.no/media/Codingstandards.pdf)
- Follow the [Inonit Developer workflow routines](http://inonit.no/media/Developerworkflowroutines.pdf)

## Project description
Our priorities for this project is:

a. Build the functionality that SERAF needs to cover their needs for a program to help people quit smoking, and to monitor the results of participants as test subjects. Specifically, SERAF wants to see if "slip management" is effective, through e.g. automated SMS follow-up to participants in the test group who do not follow the program as intended.

b. Make it general enough for other mainly academic use in the future. Examples could include similar self-help programs, or e-learning and online courses. We intend to release the base software under a free software licence once it's done.

To accomplish this, the system will be built in a modular way, with a high degree of separation between components.

### Users app
Stores all non-identifiable user data (gender, education, habits) and handles login through generation of a personal login code for each user and part (day) of the program. Backup login through id and password.

Fields past common User model fields should be set in a key: value store. Preferably, the fields are specified in a settings file before first syncdb, but behave somewhat like normal fields after this.

### Vault app
The vault stores personally identifiable data like e-mail and phone number. It will be separated to a secure server if research councils dictate so. The vault is connected to the SMS app and sends out e-mails, but only does so at the request of the main system, and only by user ID.

### SMS app
We will likely build or incorporate an interface for [Twilio SMS](http://www.twilio.com/) for this part.

### Tasks app
Handles scheduling of events, mainly triggering each day of the program and slip management. Will be based on [Huey](https://github.com/coleifer/huey), it's simple and seems adequate.

### Events app
Contains receivers for Django signals that generate logging events for any and all information that may be of interest to the researchers.

### Content app
A simple content management system for snippets of Text, Media and Forms. Snippets of Content will likely handle how they are displayed, and in the case of Forms, save the information.

### System app
Maintains a model of the Program, with the top level represented as a schedule of Parts, the path and logic of each Part as a graph of nodes called Pages, and each Page as a list of Pagelets, each corresponding to a piece of Content. We intend to set up the administrator design of the Program with [jsPlumb](http://jsplumbtoolkit.com/demo/statemachine/jquery.html).

Some simple logic setup will be needed for Pages and Pagelets. Nodes may be abstracted to redefinable "building blocks"; display page, ask question, send SMS, etc.
