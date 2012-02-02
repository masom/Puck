import cherrypy
import unittest
import sqlite3
import os
from libs.model import Migration
import models

class PuckTestCase(unittest.TestCase):
    def setUp(self):
        self._tables = []
        collections = [
            'Jails', 'Environments', 'Images', 'JailTypes', 'Keys',
            'Users', 'VirtualMachines', 'YumRepositories'
        ]
        for c in collections:
            self._tables.append(getattr(models, c).table_definition())

        db = ':memory:'
        self._connection = sqlite3.connect(db)
        cherrypy.thread_data.db = self._connection
        cherrypy.thread_data.db.row_factory = sqlite3.Row

        self.setMigration()
        self._migrate()

    def setMigration(self):
        pass

    def _migrate(self):
        m = Migration(self._connection, self._tables)
        m.migrate()
