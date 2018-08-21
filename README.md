# Serafin
_Logic-driven web content creation kit_

Serafin is a Django-based web platform that gives content builders a set of flexible building blocks for creating logic-driven sites. Examples include:

- Web forms and questionaires
- Self-help programs
- E-learning programs
- Dynamic websites with a complex underlying logic

Serafin was developed by [Inonit AS](http://inonit.no/) for [SERAF](http://www.med.uio.no/klinmed/english/research/centres/seraf/), the Norwegian Centre for Addiction Research at the University of Oslo, in order for them to create a program to help users stop smoking while gathering research data on the efficacy of therapeutic techniques. The program, Endre, and its content is [available here](https://github.com/inonit/serafin-endre).

Program flow is controlled on different levels. Sessions are built as a series of pages or other events (e-mail, SMS), allowing the users' path to be controlled by logic applied to their choices. Sessions may be put into sequence, where registered users are invited to follow the Program day by day, or sessions may be accessed manually. Pages and other content may present text, media, or forms for the user to fill out.


## Getting started

The preferred method for setting up Serafin for development is through docker-compose. A complete environment is provided, including PostgreSQL, Redis, and a Python container with a Django development server and a Huey task runner.

Install [docker](https://docs.docker.com/engine/installation/) and [docker-compose](https://docs.docker.com/compose/install/).

Run docker-compose to build the environment:

    $ docker-compose up

In a separate terminal, run database migrations (first time, but may be needed after model changes):

    $ docker-compose exec app ./manage.py migrate 

Create a local admin user (first time only):

    $ docker-compose exec app ./manage.py createsuperuser

Run tests with:

    $ docker-compose exec app ./manage.py test

You may run other Django management commands the same way.


## Contributing

Serafin has seen work on and off for several years. While it has seen production use in its current state, it may not meet everyones standards of a well-packaged open source project. We intend to improve this. Preparing the system for general use, software dependency updates, test coverage and documentation will be prioritized. 

See [issues](https://github.com/inonit/serafin/issues) or submit your own.

Pull requests are welcome.


## License

Copyright (C) 2018 Institute of Clinical Medicine, University of Oslo. All rights reserved. The source code for this project is licensed under the AGPL v3 license, see [LICENSE.txt](LICENSE.txt) for details.
