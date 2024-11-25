# Adapted from https://forum.djangoproject.com/t/django-db-utils-interfaceerror-connection-already-closed-when-updating-from-django-3-0-to-3-1/12708/21

import django.db
from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper
from psycopg2 import InterfaceError


class DatabaseWrapper(DatabaseWrapper):
    def create_cursor(self, name=None):
        try:
            return super().create_cursor(name=name)
        except InterfaceError:
            django.db.close_old_connections()
            django.db.connection.connect()
            return super().create_cursor(name=name)
