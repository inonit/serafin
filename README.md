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

1. Install requirements
    
    `$ pip install -r requirements.txt`
    
2. Run docker-compose for required services

    `$ docker-compose up` (Optionally with `-d` flag to keep them running in the background)

3. Install javascript dependencies
    
    ```
    $ npm install
    $ ./node_modules/bower/bin/bower install
    ```

4. Write a `local_settings.py`

    ```
    $ cat << EOF >> serafin/local_settings.py
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': 'localhost',
            'PORT': 5432,
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
        },
        
        # Change these in order to keep the vault in a separate database!
        'vault': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': 'localhost',
            'PORT': 5432,
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
        }
    }
    EOF
    ```

    
5. Run migrations for both the serafin and the vault databases.

    ```
    $ python manage.py migrate
    $ python manage.py migrate --database vault
    ```

6. Create a local admin user

    `$ python manage.py createsuperuser`
    
7. Run the development server

    `$ python manage.py runserver`
