"""
Django command for wait for db to be available
"""
import time

from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management import BaseCommand

class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Waiting for database...')
        db_up = False
        count = 0
        while db_up is False:
            count+=1
            try:
                self.check(databases=['default'])
                db_up = True
            except(Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
                if count == 10:
                    self.stdout.write('Unable to establish conection with DB')
                    exit()

        self.stdout.write('Database available!')
