import uuid
import sqlite3
import cherrypy

from collections import namedtuple, defaultdict
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


def sqltable(tablename, *cols):
    from operator import itemgetter

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
    return newcls

    
class VM(object):
    def __init__(self, ip):
        self._ip = ip
        self._id = uuid.uuid1()
        self.config = {}
        self.status = ''
        
    @property
    def id(self):
        return str(self._id).replace('-', '')

class Model(object):
    Table = None

    def new(self, data):
        key = self.Table(*tuple(data[key] for key in self.Table._fields))
        self._insert(key)

    def get(self, ref):
        query = "SELECT * FROM {table} WHERE id=?".format(table=self.Table._name)
        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query, (ref,))
        return self.Table(*crs.fetchone()[1:])

    def delete(self, ref):
        return self._delete(ids=[ref])

    @staticmethod
    def _newId():
        return uuid.uuid1()

    def _insert(self, row):
        rowId = self._newId()

        ncols = len(self.Table._columns) + 1 # add 1 for id 
        query = """
        INSERT INTO {table}
        VALUES ({stubs})
        """.format(table=self.Table._name, 
                   stubs=','.join('?' for i in xrange(ncols))
                   )

        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query, (str(rowId),) + row)
        cherrypy.thread_data.db.commit()


    def _select(self, orderBy=[]):
        query = "SELECT * FROM {table}\n"
        if orderBy:
            query += "ORDER BY {orderCols}\n"

        query = query.format(table=self.Table._name, 
                             orderCols=' ,'.join(orderBy))
        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query)
        return ((row[0], self.Table(*row[1:])) for row in crs.fetchall())


    def _delete(self, ids=[]):
        query = "DELETE FROM {table}\n"
        params = ()
        if ids:
            params += tuple(ids)

            query += "WHERE id in ({idStubs})"
        query = query.format(table=self.Table._name,
                             idStubs=','.join('?' for i in xrange(len(ids)))
                            )
        crs = cherrypy.thread_data.db.cursor()
        crs.execute(query, params)
        crs = cherrypy.thread_data.db.commit()


    @staticmethod
    def _fieldgetter(fld):
        fldget = attrgetter(fld)
        return lambda (rowId, row): fldget(row)
        


class Jail(Model):
    Table = sqltable("jail", 
                        "name" & Text, 
                        "url" & Text,
                        "type" & Text,
                        "environment" & Text
                    )

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



class Key(Model):
    Table = sqltable("key", 
                        "name" & Text,
                        "key" & Text
                    )

    def keys(self):
        return self._select(orderBy=["name"])


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
            cols = ("id" & (Text | "PRIMARY KEY"),) + table._columns
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
