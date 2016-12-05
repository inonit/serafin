class VaultRouter(object):
    '''
    A router to direct all operations on the vault app to the 'vault' database.
    If vault is contained on another system, this may be disabled.
    '''
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'vault':
            return 'vault'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'vault':
            return 'vault'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'vault' or \
           obj2._meta.app_label == 'vault':
           return True
        return None

    def allow_migrate(self, db, model):
        if db == 'vault':
            return model._meta.app_label == 'vault'
        elif model._meta.app_label == 'vault':
            return True
        return None
