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
from collections import OrderedDict
import uuid
import cherrypy

class ModelCollection(object):
    ''' Represents a collection of entities '''

    _model = None
    _table_name = None
    _table_definition = None

    def __init__(self):
        self._table_definition = self._generate_table_definition()
        self._items = []
        self._after_init()

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
        return self._table_definition

    def _generate_table_definition(self):
        ''' To be overloaded.'''
        return None

    def all(self):
        ''' Returns a list of all the entities. '''

        return self._items

    def find(self, **kwargs):
        ''' Returns a list of entities matching a value. '''

        # TODO List comprehension
        results = []
        for item in self._items:
            if not self._find(item, kwargs):
                continue
            results.append(item)
        return results

    def _find(self, item, fields):
        for f in fields:
            if not self._find_match(item, f, fields[f]):
                return False
        return True

    def _find_match(self, item, field, value):
        if not hasattr(item, field):
            return None
        if getattr(item, field) == value:
            return True
        return False

    def first(self, **kwargs):
        ''' Returns the first entity matching a value '''
        for item in self._items:
            if not self._find(item, kwargs):
                continue
            return item

    def new(self, **kwargs):
        ''' Creates a new entity '''
        entity = self._model(**kwargs)
        entity._collection = self
        return entity

    def add(self, entity, persist=True):
        ''' Add an entity to the collection '''

        if not self._before_add(entity):
            return False

        self._items.append(entity)
        if persist:
            self._insert(entity)
        return True

    def delete(self, entity):
        ''' Delete an entity from the collection. '''

        if not self._delete(entity):
            return False

        del self._items[entity]
        return True

    def _build(self, items):
        ''' Build model entities out of SQL rows. '''

        entities = []
        for r in items:
            entities.append(self.new(**r))
        return entities

    def _select_all(self):
        ''' Select all rows from the storage. '''
        crs = cherrypy.thread_data.db.cursor()
        crs.execute(self._generate_select_query())
        entities =  self._build(crs.fetchall())
        crs.close()
        return entities

    def _insert(self, entity):
        ''' Insert an entity into the storage.'''

        insert_data = self._generate_query_data(entity)

        if not len(insert_data):
            return False

        key = self._table_definition.primary_key
        if key:
            insert_data[key] = str(uuid.uuid1())
            setattr(entity, key, insert_data[key])

        query = self._generate_insert_query(insert_data)
        return self._execute_query(query, insert_data.values())

    def update(self, entity, fields):
        '''Update the persistent value(s) of an entity'''

        data = self._generate_query_data(entity, fields)

        #Prevent updating the primary key
        key = self._table_definition.primary_key
        if key in data:
            del(data[key])

        if not len(data):
            return False
        if not hasattr(entity, key):
            return False

        query = self._generate_update_query([getattr(entity, key)], data)
        return self._execute_query(query, data.values())

    def _update_all(self, entities, data):
        '''Update the persistent value(s) of a group of entities.'''
        pass

    def _delete(self, entity):
        key = self._table_definition.primary_key
        if not hasattr(entity, key):
            return False
        query = self._generate_delete_query(key)
        return self._execute_query(query, getattr(entity,key))

    def _execute_query(self, query, data):
        '''Execute a query.'''
        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query, data)
        cherrypy.thread_data.db.commit()
        crs.close()
        return True

    def _generate_query_data(self, entity, fields = []):
        query_data = OrderedDict()
        columns = self._table_definition.columns.keys()

        whitelist = len(fields)
        for k in columns:
            if not hasattr(entity, k):
                continue
            if whitelist and not k in fields:
                continue
            query_data[k] = getattr(entity, k)
        return query_data

    def _generate_select_query(self):
        template = '''SELECT * FROM {table}'''
        return template.format(table=self._table_definition.name)

    def _generate_insert_query(self, insert_data):
        template = '''INSERT INTO {table}({columns}) VALUES ({stub})'''

        return template.format(
            table = self._table_definition.name,
            columns = ','.join(k for k in insert_data.keys()),
            stub = ','.join('?' for i in xrange(len(insert_data)))
        )

    def _generate_update_query(self, keys, update_data):
        template = '''UPDATE {table} SET {stub} {where}'''

        args = {}
        key = self._table_definition.primary_key
        if key in update_data.keys():
            del(update_data[key])

        args['where'] = 'WHERE %s IN (%s)' % (key, ",".join('?' for k in keys))

        args['table'] = self._table_definition.name
        args['stub'] = ','.join('%s = ?' % c for c in update_data.keys())

        return template.format(**args)

    def _generate_delete_query(self, key):
        template = '''DELETE FROM {table} {where}'''
        key = self._table_definition.primary_key
        where = "WHERE %s = ?" % key
        return template.format(table=self._table_definition.name, where=where)


class Model(object):
    '''Represent an entity of a ModelCollection'''
    _collection = None

    def to_dict(self):
        keys = self._collection.table_definition().columns.keys()
        return OrderedDict([(k,getattr(self,k)) for k in keys])

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
            crs.execute(str(table))
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
        self._string = ""

        if not primary_key in columns:
            raise KeyError('Primary key not set')

        pk = "PRIMARY KEY"
        if columns[primary_key].find(pk) == -1:
            columns[primary_key] = "%s %s" % (columns[primary_key], pk)

        self._generate_string()

    def _generate_string(self):
        fields = ",".join("%s %s" % (col, self.columns[col]) for col in self.columns)
        self._string = self.template.format(name=self.name, fields=fields)

    def __str__(self):
        return self._string
