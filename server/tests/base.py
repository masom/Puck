import cherrypy
import unittest
import sqlite3
import os
from libs.model import Migration
import models


class PuckTestCase(unittest.TestCase):
    def setUp(self):
        tables = []
        collections = [
            'Jails', 'Environments', 'Images', 'JailTypes', 'Keys',
            'Users', 'VirtualMachines', 'YumRepositories'
        ]
        for c in collections:
            tables.append(getattr(models, c).table_definition())

        db = ':memory:'
        self._connection = sqlite3.connect(db)
        cherrypy.thread_data.db = self._connection
        cherrypy.thread_data.db.row_factory = sqlite3.Row

        m = Migration(self._connection, tables)
        m.migrate()
