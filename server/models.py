'''
Puck: FreeBSD virtualization guest configuration server
Copyright (C) 2011  The Hotel Communication Network inc.

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
import uuid
import sqlite3
import cherrypy

from collections import namedtuple, OrderedDict, defaultdict, deque
from itertools import groupby
from operator import attrgetter

SQLField = namedtuple("SQLField", ["name", "type"])
class SQLType(object):
    def __init__(self, sqltype, attribute=None):
        self._sqltype = sqltype
        self._attribute = attribute
        
    def toVal(self):
        atts = '' if self._attribute is None else ' %s' % self._attribute
        return self._sqltype + atts

    def __rand__(self, other):
        return SQLField(other, self)

    def __or__(self, att):
        return SQLType(self._sqltype, attribute=att)
        
Text = SQLType("TEXT")


def sqltable(tablename, *cols, **config):
    from operator import itemgetter

    primaryKey = config.get("primaryKey", "id")

    field_names = tuple(col.name for col in cols)
    argtxt = repr(field_names).replace("'", "")[1:-1]

    template = """class %(tablename)s(tuple):
    _name = "%(tablename)s"
    __slots__ = ()
    _fields = %(field_names)r
    def __new__(_cls, %(argtxt)s):
        return _tuple.__new__(_cls, (%(argtxt)s))\n\n""" % locals()

    template += "\n".join("    %s = _property(_itemgetter(%d))" % (name, i)
                            for i, name in enumerate(field_names))

    namespace = dict(_itemgetter=itemgetter, _property=property, _tuple=tuple)

    exec template in namespace
    newcls = namespace[tablename]
    newcls._types = tuple(col.type for col in cols)
    newcls._columns = cols
    newcls._primaryKey = primaryKey
    return newcls

    
class Model(object):
    def __init__(self, config):
        pass

class SQLModel(Model):
    Table = None


    def new(self, data):
        key = self.Table(*tuple(data[key] for key in self.Table._fields))
        self._insert(key)

    def get(self, ref):
        query = "SELECT {fields} FROM {table} WHERE id=?".format(
            fields=','.join(self.Table._fields),
            table=self.Table._name
        )
        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query, (ref,))
        return self.Table(*crs.fetchone())

    def delete(self, ref):
        return self._delete(ids=[ref])

    @staticmethod
    def _newId():
        return str(uuid.uuid1())

    def _insert(self, row):
        add = 0
        if self.Table._primaryKey not in self.Table._fields:
            row = (self._newId(),) + row
            add = 1

        ncols = len(self.Table._columns) + add
        query = """
        INSERT INTO {table}
        VALUES ({stubs})
        """.format(table=self.Table._name, 
                   stubs=','.join('?' for i in xrange(ncols))
                   )

        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query, row)
        cherrypy.thread_data.db.commit()


    def _select(self, fields=None, orderBy=[]):
        query = "SELECT {fields} FROM {table}\n"

        fields = fields if fields is not None else self.Table._fields
        fields = (self.Table._primaryKey,) + fields

        if orderBy:
            query += "ORDER BY {orderCols}\n"


        query = query.format(table=self.Table._name, 
                             fields=','.join(fields),
                             orderCols=' ,'.join(orderBy))
        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query)
        return ((row[0], self.Table(*row[1:])) for row in crs.fetchall())


    def _delete(self, ids=[]):
        query = "DELETE FROM {table}\n"
        params = ()
        if ids:
            params += tuple(ids)

            query += "WHERE {primaryKey} in ({idStubs})"
        query = query.format(table=self.Table._name,
                             primaryKey=self.Table._primaryKey,
                             idStubs=','.join('?' for i in xrange(len(ids)))
                            )
        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query, params)
        crs = cherrypy.thread_data.db.commit()

    def _update(self, key, column, value):
        query = """
            UPDATE {table}
            SET {column} = ?
            WHERE {primaryKey} = ?
        """.format(table=self.Table._name, 
                   column=column,
                   primaryKey=self.Table._primaryKey
        )

        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query, (value, key))
        crs = cherrypy.thread_data.db.commit()


    @staticmethod
    def _fieldgetter(fld):
        fldget = attrgetter(fld)
        return lambda (rowId, row): fldget(row)
        


class Jail(SQLModel):
    Table = sqltable("jails", 
                        "name" & Text, 
                        "url" & Text,
                        "type" & Text,
                        "ip" & Text,
                        "environment" & Text
                    )
    Type = namedtuple("Type", ["name", "ip"])

    def jails(self):
        jails = self._select(orderBy=["environment", "type", "name"])

        section = defaultdict(dict)

        type_ = self._fieldgetter('type')
        environment = self._fieldgetter('environment')
        for env, envJails in groupby(jails, environment):
            subsection = section[env]
            for typ, typJails in groupby(envJails, key=type_):
                subsection[typ] = list(typJails)
            
        return section

    def types(self):
        return [
            self.Type("content", "10.0.0.10"), 
            self.Type("database", "10.0.0.11"),
            self.Type("support", "10.0.0.12")
            ]



class Key(SQLModel):
    Table = sqltable("keys", 
                        "name" & Text,
                        "key" & Text
                    )

    def keys(self):
        return list(self._select(orderBy=["name"]))

class VM(SQLModel):
    Table = sqltable("vms",
                        "name" & (Text | "PRIMARY KEY"),
                        "ip" & Text,
                        "status" & Text,
                        "config" & Text
                    , primaryKey="name"
                    )

    def __init__(self, config):
        Model.__init__(self, config)

        wordlist = ["apple", "banana", "carrot", "pepper", "orange",
        "eggplant", "squash", ]
        self._wordlist = deque(wordlist)


    def _newId(self):
        word = self._wordlist.pop()
        self._wordlist.appendleft(word)
        return word
        

    def register(self, ip, name=None):
        if name is None:
            name = self._newId()
        vm = self.Table(name, ip, None, None)
        return name

    def setStatus(self, vmId, status):
        self._update(vmId, 'status', status)
        

    def statuses(self):
        return list(self._select(fields=["status"]))

class Environment(Model):
    def __init__(self, config):
        Model.__init__(self, config)
        self._envs = OrderedDict([
            ('dev','Development'),
            ('testing', 'Testing'),
            ('qa', 'Quality Assurance'),
            ('staging', 'Staging'),
            ('prod', 'Production')
        ])

    def get(self):
        return self._envs

        

        
def migrate(conn, models):
    crs = conn.cursor()

    tables = [model.Table for model in models]
    for table in tables:
        crs.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table._name,)
        )
        exists = crs.fetchone() is not None
        if not exists:
            if table._primaryKey not in table._fields:
                cols = (table._primaryKey & (Text | "PRIMARY KEY"),) + table._columns
            query = "CREATE TABLE {name} {fields}".format(
                name=table._name,
                fields="(%s)" % ','.join("%s %s" % (col.name, col.type.toVal())
                                            for col in cols)
            )
            crs.execute(query)
    conn.commit()

            


if __name__ == "__main__":
    import sqlite3
    conn = sqlite3.connect("/tmp/example.db3")
    migrate(conn, [Jail, Key])
