from database import *
import json


# custom exception to use with database
class DB_Exception(Exception):
    pass


# CLASSES FOR PRIMITIVIVE COMMANDS
class Create_Prince_cmd(object):
    def __init__(self, _user, _pass):
        self.user = _user
        self.password = _pass

    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        result = _user_db.create_user(_user, self.user, self.password, _var_db)
        print 'create prince'
        if result == 'CREATE_PRINCIPAL':
            return ['{"status":"CREATE_PRINCIPAL"}']
        # elif result == 'NOPERM':
        #     raise DB_Exception("Create Principal: NO_PERM")
        # elif result == 'USER_ALREADY_EXISTS':
        #     raise DB_Exception("Create Principal: USER_ALREADY_EXISTS")
        else:
            raise (DB_Exception('Create Principal: Unexpected System State'))


class Change_Password_cmd(object):
    def __init__(self, _user, _pass):
        self.user = _user
        self.password = _pass
        self.command = 'change password'  # the command field holds the name of the command

    # This function is for debugging purposes, do not use it for actual DB interaction

    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        status_list = []
        status = '{status:'
        result = _user_db.change_password(_user, self.user, self.password)
        print 'change password'
        if result == 'CHANGE_PASSWORD':
            return ['{"status":"CHANGE_PASSWORD"}']
        # elif result == 'USER_NOT_FOUND':
        #     raise DB_Exception('Change Password: USER_NOT_FOUND')
        # elif result == 'TARGET_USER_NOT_FOUND':
        #     raise DB_Exception('Change Password: TARGET_USER_NOT_FOUND')
        # elif result == 'FAIL':
        #     raise DB_Exception('Change Password: FAIL')
        else:
            raise DB_Exception('Change Password: Unexpected System State')


# updates for locals
class Set_cmd(object):
    def __init__(self, _ident, _expr):
        self.ident = _ident  # string name of var
        self.expr = _expr

    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        # in local or global?
        print "in set"
        if self.ident in _locals:
            expr = self.expr.evaluate(_user, _locals, _var_db, _user_db)
            _locals[self.ident] = expr
            return ['{"status":"SET"}']
        else:
            expr = self.expr.evaluate(_user, _locals, _var_db, _user_db)
            if _var_db.set_variable(_user, self.ident, expr) == 'SET':
                return ['{"status":"SET"}']


class Append_to_cmd(object):
    def __init__(self, _ident, _expr):
        self.ident = _ident
        self.expr = _expr

    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        print "In append to"
        expr = self.expr.evaluate(_user, _locals, _var_db, _user_db)
        # check to see if the identifier is in locals or not
        if self.ident in _locals:
            lst = _locals[self.ident]
        else:
            lst = _var_db.get_variable(_user, self.ident)

        if isinstance(lst, list):
            if isinstance(expr, dict):  # records are appended to lists
                lst.append(expr)
            elif isinstance(expr, str):  # strings are appended to lists
                lst.append(expr)
            elif isinstance(expr, list):
                lst += expr
            else:
                raise DB_Exception('Append to reached an unexpected state')
            return ['{"status":"APPEND"}']
        else:
            raise DB_Exception('FAILED')  # we only append to lists


class Local_cmd(object):
    def __init__(self, _ident, _expr):
        self.ident = _ident
        self.expr = _expr
        self.command = 'local'

    # This function is for debugging purposes, do not use it for actual DB interaction

    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        print "in local"
        # check to see if this value is already global
        if self.ident in _locals or self.ident in _var_db.var_value_db:
            # print 'local found a duplicate'
            raise DB_Exception('FAILED')  # we have a duplicate
        else:
            expr = self.expr.evaluate(_user, _locals, _var_db, _user_db)
            _locals[self.ident] = expr
            return ['{"status":"LOCAL"}']


class Foreach_cmd(object):
    def __init__(self, _ident1, _ident2, _expr):
        self.ident1 = _ident1  # y
        self.ident2 = _ident2  # x
        self.expr = _expr  # do

    # for every element y in list x: y = expr()
    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        # expr := <value:= identifier, string, access> | record
        print 'in foreach'
        output_list = []
        if self.ident2 in _locals:
            lst = _locals[self.ident2]
        else:
            lst = _var_db.get_variable(_user, self.ident2)
        # check if we have a list
        if isinstance(lst, list):
            # work on it
            # print "in_foreach with:%s"%(lst)
            for elem in lst:
                # print elem
                if isinstance(elem, dict):
                    val = self.expr.expr_in_dict(elem, self.ident1)
                    # print 'got value:%s'%(val)
                    output_list.append(val)
                elif isinstance(elem, str):
                    if self.expr.type == 'record':
                        record_dict = {}
                        # print 'expression record:%s'%(self.expr.data)
                        for tup in self.expr.data:
                            # print 'for %s,%s'%(tup[0].type,tup[1].type)
                            if tup[1].type == 'identifier':  # the case expression is {m = a}
                                # check scope
                                if tup[1].data == self.ident1:
                                    record_dict[tup[0].data] = elem
                                else:
                                    record_dict[tup[0].data] = tup[1].evaluate(_user, _locals, _var_db, _user_db)
                            else:  # the case {m = "string"}
                                record_dict[tup[0].data] = tup[1].data

                        output_list.append(record_dict)

            # set the output list
            if self.ident2 in _locals:
                _locals[self.ident2] = output_list
            else:
                _var_db.set_variable(_user, self.ident2, output_list)
        else:
            DB_Exception('FAILED')  # x must be a list
        return ['{"status":"FOREACH"}']


# The target, identifers and rights are set in the order as described in the design document
# Template: set delegation <target> q <right> -> p
class Set_Delegation_cmd(object):
    def __init__(self, _tgt, _ident1, _right, _ident2):
        self.target = _tgt
        self.ident1 = _ident1
        self.right = _right
        self.ident2 = _ident2

    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        # check that all users exist
        print 'in set del'
        if _user not in _user_db.user_db or self.ident1 not in _user_db.user_db or self.ident2 not in _user_db.user_db:
            raise DB_Exception('FAILED')  # one of the users does not exist
        # is the target all then we have seperate logic
        if self.target == 'all':
            # do this for all variables that q has delegate rights for
            # TODO: logic for if this is empty for some reason...
            vars_with_del = _var_db.findall_vars_with_delegate_perm(self.ident1)
            for var in vars_with_del:
                result = _var_db.set_delegation(_user, self.ident1, self.ident2, self.right, var)
                # an exception is thrown in database if theres a permission error
            if result == 'SET_DELEGATION':
                return ['{"status":"SET_DELEGATION"}']
                # for var in _var_db.perm_db:
                #     # usr = _var_db.perm_db[var] #all of the users with access to var
                #     # if _user in usr:
                #     #     #The user issuing this command has the following rights to the variable var
                #     #     user_rights = usr[_user]
                #     #     #print 'User:%s has rights:%s to variable:%s'%(_user,user_rights,var)
                #     #     if 'delegate' in user_rights:
                #     #         #User has delegate rights to this variable
                #     #         result = _var_db.set_delegation(_user,self.ident2,self.right,var)
                #     #         #print "Result: %s"%(result)
                #     #         if result == 'SET_DELEGATION':
                #     #             #Expected
                #     #             return ['{"status":"SET_DELEGATION"}']

                #     #         else:
                #     #             #Should not occur
                #     #             raise DB_Exception('Set Delegation (all): Unexpected System State')
                # return status_list
        else:
            # just do it for the one variable
            # TODO: should we perform the logic check prior to trying?
            result = _var_db.set_delegation(_user, self.ident1, self.ident2, self.right, self.target)
            if result == 'SET_DELEGATION':
                # Expected
                return ['{"status":"SET_DELEGATION"}']
            else:
                # Should not occur
                raise DB_Exception('Set Delegation : Unexpected System State')


# The target, identifers and rights are set in the order as described in the design document
class Delete_Delegation_cmd(object):
    def __init__(self, _tgt, _ident1, _right, _ident2):
        self.target = _tgt
        self.ident1 = _ident1
        self.right = _right
        self.ident2 = _ident2
        self.command = 'delete delegation'

    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        print 'delete del'
        status = '{status:'
        status_list = []
        # is the target all then we have seperate logic
        if _user not in _user_db.user_db or self.ident1 not in _user_db.user_db or self.ident2 not in _user_db.user_db:
            raise DB_Exception('FAILED')  # one of the users does not exist

        if self.target == 'all':
            # do this for all variables that q has delegate rights for
            # TODO: logic for if this is empty for some reason...
            vars_with_del = _var_db.findall_vars_with_delegate_perm(self.ident1)
            for var in vars_with_del:
                result = _var_db.remove_delegation(_user, self.ident1, self.ident2, self.right, var)
                # an exception is thrown in database if theres a permission error
            if result == 'DELETE_DELEGATION':
                return ['{"status":"DELETE_DELEGATION"}']
                # for var in _var_db.perm_db:
                #     usr = _var_db.perm_db[var] #all of the users with access to var
                #     if _user in usr:
                #         #The user issuing this command has the following rights to the variable var
                #         user_rights = usr[_user]
                #         #print 'User:%s has rights:%s to variable:%s'%(_user,user_rights,var)
                #         if 'delegate' in user_rights:
                #             #User has delegate rights to this variable
                #             result = _var_db.remove_delegation(_user,self.ident2,self.right,var)
                #             #print "Result: %s"%(result)
                #             if result == 'DELETE_DELEGATION':
                #                 #Expected
                #                 status_list.append(status + result + '}')
                #             else:
                #                 #Should not occur
                #                 raise DB_Exception('Delete Delegation (all): Unexpected System State')
                # return status_list

        else:
            # just do it for the one variable
            # TODO: should we perform the logic check prior to trying?
            result = _var_db.remove_delegation(_user, self.ident1, self.ident2, self.right, self.target)
            if result == 'DELETE_DELEGATION':
                return ['{"status":"DELETE_DELEGATION"}']

            else:
                # Should not occur
                raise DB_Exception('Delete Delegation: Unexpected System State')

                # return status_list


# TODO: find the best way to implement this within the database, involves changing create principal logic.
class Default_Delegator_cmd(object):
    def __init__(self, _ident):
        self.ident = _ident
        self.command = 'default delegator'

    # This function is for debugging purposes, do not use it for actual DB interaction
    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        print 'default delegator'
        _user_db.set_default_delegator(_user, self.ident)
        # if no exception is thrown:
        return ['{"status":"DEFAULT_DELEGATOR"}']


# CLASSES FOR COMMANDS
class cmd(object):  # more than one prim command supported
    def __init__(self):
        self.prim_cmd = []  # list of primitive commands that are run over the course of the programs
        self.password = None
        self.user = None

    def add_cmd(self, t):
        self.prim_cmd.append(t)

    def get_commands(self):  # returnts the prim_cmd list
        commands = self.prim_cmd
        commands.reverse()  # commands need to be reversed due to the way that the AST is parsed.
        return commands

    def get_credentials(
            self):  # returns two strings containg the username and password of the user who started the prog
        return self.user, self.password

        # username, password = get_credentials()


class Exit_cmd(object):
    def __init__(self):
        self.command = 'exit'

    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        # TODO: Should we append anything? Probably should. (are we admin?)
        print 'exit'
        if _user == 'admin':
            exit(0)
        else:
            raise DB_Exception('DENIED')


class Login_cmd(object):
    def __init__(self, _user, _pass):
        self.user = _user
        self.password = _pass

    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        print 'in login'
        result = _user_db.check_user_auth(self.user, self.password)
        return ['Login:%s' % (self.user)]


class Return_cmd(object):
    def __init__(self, _expr):
        self.command = 'return'
        self.expr = _expr

    def execute(self, _user, _pass, _user_db, _var_db, _locals):
        print 'return'
        expr = self.expr.evaluate(_user, _locals, _var_db, _user_db)
        # if isinstance(expr,list):
        #     return ['{"status":"RETURNING","output":' + '[' + json.dumps(expr).replace('\\"','') + ']' + '}']
        # else:
        print expr
        print json.dumps(expr).replace('\\"', '')
        return ['{"status":"RETURNING","output":' + json.dumps(expr).replace('\\"', '')  + '}']
        # ret = ""
        # if isinstance(expr,list):
        #     for index,keyword in enumerate(expr):
        #         if isinstance(keyword,dict):
        #             for vals in keyword:
        #                 if isinstance(keyword[vals],str) and keyword[vals][0] == '"':
        #                     keyword[vals] = keyword[vals][1:-1]

        #         elif isinstance(keyword,str) and keyword[0] == '"':
        #             keyword = keyword[1:-1]
        #         if index < len(expr)-1:
        #             ret += json.dumps(keyword)
        #             ret += ',' #comma seperated values in list
        #         else:
        #             ret += json.dumps(keyword)
        #     return ['{"status":"RETURNING","output":' + '[' + ret + ']' + '}']
        # elif isinstance(expr,dict):
        #     for index,keyword in enumerate(expr):
        #         if keyword and keyword[0] == '"':
        #             keyword = keyword[1:-1]
        #     ret += json.dumps(expr)
        #     return ['{"status":"RETURNING","output":' + ret  + '}']
        # else:
        #     #string
        #     if expr[0] == '"':
        #         ret = json.dumps(expr[1:-1])
        #         return ['{"status":"RETURNING","output":' + ret  + '}']
