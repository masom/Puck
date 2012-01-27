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
    ''' Represents a collection of entities '''

    _model = None
    _table_name = None

    def __init__(self):
        self._items = []
        self._post_init()

    def _after_init(self):
        ''' Executed after the object has initialized.'''
        pass

    def _before_add(self, entity):
        '''
        Executed before an entity is added.
        If the return value is not True, the entity will not be added.
        '''
        return True

    def table_definition(self):
        ''' Should return the table definition for the collection. '''
        if self._table_definition:
            return self._table_definition
        self._table_definition = self._generate_table_definition()
        return self._table_definition

    def _generate_table_definition(self):
        ''' To be overloaded.'''
        pass

    def all(self):
        ''' Returns a list of all the entities. '''

        return self._items

    def find(self, key, value):
        ''' Returns a list of entities matching a value. '''

        items = []
        for i in self._items:
            item = self._items[i]
            if getattr(item, key) == value:
                items.append(item)
        return items

    def first(self, key, value):
        ''' Returns the first entity matching a value '''
        for i in self._items:
            item = self._items[i]
            if getattr(item, key) == value:
                return item

    def new(self, **kwargs):
        ''' Creates a new entity '''
        return self._model(**kwargs)

    def add(self, entity):
        ''' Add an entity to the collection '''
        if not self._before_add(entity):
            return False

        return self._items.append(entity)

    def delete(self, entity):
        ''' Delete the entity. '''

    def _build(self, items):
        entities = []
        for r in items:
            entities.append(self.new(**r))
        return entities

    def _select_all(self):
        query = "SELECT * from {table}"
        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query.format(table=self._table_name))
        return self._build(crs.fetchall())

    def _insert(self, entity):
        definition = self.table_definition()
        columns = definition.columns.keys()
        for k in columns:
            values.append(definition.columns[k])

class Model(object):
    pass

class Migration(object):
    ''' Handles migrating/creating the database. '''

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
        ''' Determine if a table exists in the database. '''

        crs = self._connection.cursor()
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        crs.execute(query, (table_name,))
        return crs.fetchone() is not None

class TableDefinition(object):
    ''' Represents a table. '''

    template = "CREATE TABLE {name} ({fields})"

    def __init__(self, name, columns, primary_key = 'id'):
        self.primary_key = primary_key
        self.name = name
        self.columns = columns

        self._generate_string()

    def _generate_string(self):
        fields = ",".join("%s %s" % (col, self.columns[col]) for col in self.columns)
        self._string = self.template.format(name=self.name, fields=fields)

    def __str__(self):
        return self._string
