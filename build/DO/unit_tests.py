import database
from Commands import DB_Exception

def UNIT_TESTS():




    try:
        userdb = database.USER_DB()
        vardb = database.VARIABLE_DB()
        testindex = 0
        # USER DB TESTS
        res = userdb.create_user("admin", "admin", "password")
        print "init createuser " + str(testindex) + " " + str(res)
        testindex += 1

        res = userdb.create_user("admin", "admin", "shouldntbeabletodothis")
        print "check no duplicates " + str(testindex) + " " + str(res)
        testindex += 1

        res = userdb.check_user_auth("admin", "potato")
        print "auth falsepassword " + str(testindex) + " " + str(res)
        testindex += 1

        res = userdb.check_user_auth("admin", "password")
        print "auth truepassword " + str(testindex) + " " + str(res)
        testindex += 1

        res = userdb.create_user("admin", "bob", "bobpass")
        print "create new user " + str(testindex) + " " + str(res)
        testindex += 1

        res = userdb.change_password("bob", "admin", "newpass")
        print "false change password " + str(testindex) + " " + str(res)
        testindex += 1

        res = userdb.change_password("admin", "admin", "password2")
        print "true change password " + str(testindex) + " " + str(res)
        testindex += 1

        res = userdb.change_password("admin", "bob", "bobsnewpassword")
        print "true change password sub " + str(testindex) + " " + str(res)
        testindex += 1


        # VAR DB TESTS
        res = vardb.set_variable("admin", "x", 5)
        print "setvar " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.set_variable("admin", "x", 6)
        print "reset var " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.get_variable("admin", "x")
        print "get var " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.get_variable("bob", "x")
        print "false getvar " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.set_delegation("admin", "bob", "read", "x")
        print "set read bob " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.get_variable("bob", "x")
        print "bob true getvar " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.set_variable("bob", "x", 7)
        print "false bob setvar " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.set_delegation("admin", "bob", "write", "x")
        print "set bob write x " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.set_variable("bob", "x", 7)
        print "bob write true " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.remove_delegation("admin", "bob", "read", "x")
        print "remove bob read " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.get_variable("bob", "x")
        print "getvar false " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.set_variable("admin", "y", ["one", "two", "three"])
        print "set list " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.append_to_variable("admin", "y", "EIGHT")
        print "append list " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.get_variable("admin", "y")
        print "get list " + str(testindex) + " " + str(res) + " type is : " + str(type(res))
        testindex += 1

        testdict = {"town": 5}
        res = vardb.set_variable("admin", "z", testdict)
        print "set dict " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.get_variable("admin", "z")
        print "get dict " + str(testindex) + " " + str(res) + " type is " + str(type(res))
        testindex += 1

        res = vardb.append_to_variable("admin", "z", {"mike": "1-1-90"})
        print "append a dict to dict " + str(testindex) + " result is " + str(res)
        testindex += 1

        res = vardb.get_variable("admin", "z")
        print " result of dict get: " + str(testindex) + " res is :: " + str(res)
        testindex += 1

        res = vardb.append_to_variable("admin", "x", 1)
        res = vardb.get_variable("admin", "x")
        print "should be 8 " + str(testindex) + " " + str(res)
        testindex += 1


        res = vardb.set_variable("admin", "listTest", [{"testkey": 500}])
        print "after setting empty list" + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.append_to_variable("admin", "listTest", {"KEYTWO": 900})
        print "after append... " + str(testindex) + " " + str(res)
        testindex += 1

        res = vardb.get_variable("admin", "listTest")
        print "got the list of dicts:: " + str(testindex) + " " + str(res)
        testindex += 1

    except DB_Exception as err:
        print "got err: " + str(err)
        pass

    try:
        print "Now testing for default delegation... "
        userdb2 = database.USER_DB()
        vardb2 = database.VARIABLE_DB()
        res = userdb2.create_user("admin", "USEX", "pass")
        res = userdb2.create_user("admin", "USEY", "pass")
        print "users created. "
        res = vardb2.set_variable("USEX", "delvarx", 1)
        res = vardb2.set_variable("USEX", "delvary", 2)
        res = vardb2.set_variable("USEX", "delvarz", 3)
        print "vars set. "
        res = vardb2.default_delegate("admin", "USEX", "USEY")
        print "set delegation. "
        res = vardb2.get_variable("USEY", "delvarx")
        print "RES is... " + str(res)
    except DB_Exception as err:
        print "got err " + str(err)
        pass

	exit(0)