'''
Puck: FreeBSD virtualization guest configuration server
Copyright (C) 2012  The Hotel Communication Network inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

class ModelCollection(object):
    def __init__(self):
        self._items = []
        self._post_init()

    def _post_init(self):
        pass

    def _before_add(self, entity):
        return True

    def table_definition(self):
        # To be implemented by sub class
        return None

    def all(self):
        return self._items

    def find(self, key, value):
        items = []
        for i in self._items:
            item = self._items[i]
            if getattr(item, key) == value:
                items.append(item)
        return items

    def first(self, key, value):
        for i in self._items:
            item = self._items[i]
            if getattr(item, key) == value:
                return item

    def new(self, **kwargs):
        return self._model(**kwargs)

    def add(self, entity):
        if not self._before_add(entity):
            return False

        return self._items.append(entity)


class Model(object):
    pass

class Migration(object):
    def __init__(self, connection, tables):
        self._connection = connection
        self._tables = tables

    def migrate(self):
        crs = self._connection.cursor()
        for table in self._tables:
            if self._table_exists(table.name):
                continue
            crs.execute(table)
        self._connection.commit()

    def _table_exists(self, table_name):
        crs = self._connection.cursor()
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        crs.execute(query, (table_name,))
        return crs.fetchone() is not None

class TableDefinition(object):
    template = "CREATE TABLE {name} ({fields})"

    class TextColumn(object):
        pass

    class IntColumn(object):
        pass

    def __init__(self, name, columns, primary_key = 'id'):
        self.primary_key = primary_key
        self.name = name
        self.columns = columns

        self._generate_string()

    def _generate_string(self):
        fields = ",".join("%s %s" % col for col in self.columns)
        self._string = self.template.format(name=self.name, fields=fields)

    def __str__(self):
        return self._string

