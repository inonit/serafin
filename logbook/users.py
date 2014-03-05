from logbook import LogBook
import datetime

logger_name = 'users_logger'
log_file_name = 'users.log'
log_level = 'DEBUG'

djangologbookentry = LogBook(logger_name=logger_name, log_file_name=log_file_name)
djangologbookentry.set_level(log_level)
djangologbookentry.info(str(datetime.datetime.now()), 'Logging Started')



#----------------------------------------
# You need to make sure this app is installed in your project (INSTALLED_APPS in settings.py).
# In any Django app, all you need to do is run the following import statement in the views.py file
# where APPNAME is the name of the file (app), since the file is to be named after the app
# It is also recommended that you keep the name djangologbookentry

# from PROJECTNAME.logbook.APPNAME import djangologbookentry




# To use the logger withinin your views, run any one of the following as appropriate

# djangologbookentry.debug(str(datetime.datetime.now()), 'Your DEBUG message')
# djangologbookentry.info(str(datetime.datetime.now()), 'Your INFO message')
# djangologbookentry.warning(str(datetime.datetime.now()), 'Your WARNING message')
# djangologbookentry.error(str(datetime.datetime.now()), 'Your ERROR message')
# djangologbookentry.critical(str(datetime.datetime.now()), 'Your CRITICAL message')

