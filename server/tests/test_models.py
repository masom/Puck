import unittest
from models import *

class SQLTypeTest(unittest.TestCase):
    def testToVal(self):
        self.assertEqual(SQLType("sql").toVal(), "sql")
        self.assertEqual((SQLType("sql") | "attribute").toVal(), "sql attribute")

    def testRAND(self):
        fld = "field" & SQLType("sql")
        self.assertEqual(fld.__class__, SQLField)

class sqltableTest(unittest.TestCase):
    def testCall(self):
        Empty = sqltable("Empty")

        self.assertEqual(len(Empty._fields), 0)
        self.assertEqual(len(Empty._types), 0)
        self.assertEqual(len(Empty._columns), 0)
        self.assertEqual(Empty._name, 'Empty')

        Two = sqltable("Two",
                            "a" & Text,
                            "b" & Text
        )

        self.assertEqual(len(Two._fields), 2)
        self.assertEqual(len(Two._types), 2)
        self.assertEqual(len(Two._columns), 2)
        self.assertEqual(Two._name, "Two")

        two = Two(1,2)
        self.assertEqual(two.a, 1)
        self.assertEqual(two.b, 2)


class JailTest(unittest.TestCase):
    def testType(self):
        typ = Jail.Type("name", "ip")
        self.assertEqual(typ.name, "name")
        self.assertEqual(typ.ip, "ip")

        jail = Jail({})

        self.assertTrue(
            all(isinstance(jtype, Jail.Type) for jtype in jail.types())
        )

if __name__ == "__main__":
    import models
    print(dir(models))
    unittest.main()





