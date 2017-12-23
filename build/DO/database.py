from Commands import DB_Exception

class USER_DB:
    def __init__(self):
        print "user database init"
        self.user_db = {}
        self.default_delegator = "anyone"

    def set_default_delegator(self, username, default_del_username):
        if default_del_username not in self.user_db:
            raise DB_Exception("set default del error: delegate user not found")
            # raise DB_Exception("FAILED")
        elif username != "admin":
            raise DB_Exception("set default del: NOPERM")
            # raise DB_Exception("DENIED")
        else:
            self.default_delegator = default_del_username
            return "SUCCESS"

    def get_default_delegator(self):
        return self.default_delegator

    '''
        create_user: function to create new user (principal)
        Parameters:
            username = name of new principal
            password = password for principal
        Returns:
            "NOPERM" if user is not admin (only admin can create users)
            "CREATE_PRINCIPAL" if user creation successfull
            "USER_ALREADY_EXISTS" if user already exists
    '''
    def INIT_user(self, currentuser, username, password):
        if currentuser != "admin":
            #return "NOPERM"
            #TODO: Change to DENIED
            #raise DB_Exception("Create Principal: NO_PERM")
            raise DB_Exception("DENIED")
        elif username not in self.user_db:
            # if username not already in the database, add new user
            self.user_db[username] = password
            return "CREATE_PRINCIPAL"
        else:
            # username is already in use
            #return "USER_ALREADY_EXISTS"
            #raise DB_Exception("Create Principal: USER_ALREADY_EXISTS")
            raise DB_Exception("FAILED")

    def create_user(self, currentuser, username, password, var_db):
        if self.default_delegator not in self.user_db:
            #raise DB_Exception("Create principal: def del does not exist")
            raise DB_Exception("FAILED")
        if currentuser != "admin":
            #return "NOPERM"
            #TODO: Change to DENIED
            #raise DB_Exception("Create Principal: NO_PERM")
            raise DB_Exception("DENIED")
        elif username not in self.user_db:
            # if username not already in the database, add new user
            self.user_db[username] = password
            var_db.default_delegate(currentuser, self.default_delegator, username)
            #var_db.default_delegate(currentuser, username, self.default_delegator)
            return "CREATE_PRINCIPAL"
        else:
            # username is already in use
            #return "USER_ALREADY_EXISTS"
            #raise DB_Exception("Create Principal: USER_ALREADY_EXISTS")
            raise DB_Exception("FAILED")

    '''
        check_user_auth: function to check authentication for given user
        Parameters:
            username = username of principal to check password for
            given_password = password given by script to authenticate with
        Returns:
            "USER_NOT_FOUND" if the user whom we are authenticating does not exist
            "SUCCESS" if the given password matches the user's real password
            "FAIL" if the given password does not match the user's real password 
    '''
    def check_user_auth(self, username, given_password):
        if username not in self.user_db:
            # if username is not in database
            #return "USER_NOT_FOUND"
            #raise DB_Exception('Check User Auth: USER_NOT_FOUND')
            raise DB_Exception("FAILED")
        elif self.user_db[username] == given_password:
            # if the provided password matches the password on file for username
            return "SUCCESS"
        else:
            # authentication failure
            #return "FAIL"
            #raise DB_Exception('Check User Auth: FAIL')
            raise DB_Exception("DENIED")

    '''
        change_password: function to change a user (principal's) password
        Parameters:
            username = name of user (principal) currently running script
            target_username = name of user who will have their password changed
            new_password = new password you want changed to 
        Returns:
            "USER_NOT_FOUND" if the user whom we are changing password does not exist
            "TARGET_USER_NOT_FOUND" if the target user is not found in the user database
            "CHANGE_PASSWORD" if password was successfully changed
            "FAIL" if password change was unsuccessful
    '''
    def change_password(self, username, target_username, new_password):
        if username not in self.user_db:
            # if username is not found in database
            #return "USER_NOT_FOUND"
            #raise DB_Exception('Change Password: USER_NOT_FOUND')
            raise DB_Exception("FAILED")
        elif target_username not in self.user_db:
            #return "TARGET_USER_NOT_FOUND"
            #raise DB_Exception('Change Password: TARGET_USER_NOT_FOUND')
            raise DB_Exception("FAILED")
        elif username == target_username or username == "admin":
            # if the username is changing its own password, or admin is changing the username's password
            self.user_db[target_username] = new_password
            return "CHANGE_PASSWORD"
        else:
            # authentication failure
            #return "FAIL"
            #raise DB_Exception('Change Password: FAIL')
            raise DB_Exception("DENIED")


###### VARIABLE DATABASE CLASS OBJECT
'''
    This object contains variables, their values, and permissions.
'''
class VARIABLE_DB_OLD:
    def __init__(self):
        print "variable database init"
        self.perm_db = {}
        self.var_value_db = {}

    '''
        set_variable: function to set a variable with a given value. can either be creating a new variable,
            or overwriting the value of a variable already present. 
        Parameters:
            username = username of principal currently running script
            variablename = name of variable to set
            value = value you want to set variable to 
        Returns
            "SET" if the variable was set successfully 
            "NOPERM_FOR_USER" if the variable was not set successfully (requesting user does not have valid permissions)
            
    '''
    def set_variable(self, username, variablename, value):
        if len(value) > 65000:
            raise DB_Exception("FAILED")
        if len(variablename) > 255:
            raise DB_Exception("FAILED")
        # handle if the variable is not set yet
        if variablename not in self.perm_db and variablename not in self.var_value_db:
            # init permission dictionary for perm db
            self.perm_db[variablename] = {}
            # set initial perms for creator
            self.perm_db[variablename][username] = ["read", "write", "append", "delegate"]
            # set initial value for var
            #Also give admin rights.
            self.perm_db[variablename]['admin'] = ["read", "write", "append", "delegate"]
            self.var_value_db[variablename] = value
            return "SET"
        else:
            # handle if the variable is already set
            if len(value) > 65000:
                raise DB_Exception("FAILED")
            # if username is registered for the variable
            if username in self.perm_db[variablename] or "anyone" in self.perm_db[variablename]:
                # if username has write permission
                if "write" in self.perm_db[variablename][username]:
                    # set the variable content and return
                    self.var_value_db[variablename] = value
                    return "SET"
                else:
                    # return error: user does not have write permission
                    #return "NOPERM_FOR_USER"
                    #raise DB_Exception("Set: NOPERM_FOR_USER")
                    raise DB_Exception("DENIED")
            elif username == 'admin':
                self.var_value_db[variablename] = value
                return "SET"
            else:
                # return error: user does not have any permissions for variable
                #return "NOPERM_FOR_USER"
                #raise DB_Exception("Set: NOPERM_FOR_USER")
                raise DB_Exception("DENIED")

    '''
        append_to_variable: whenever a user requests an append operation, call this.
        Parameters:
            username = username of principal currently running script
            variablename = variable you want to append info to 
            value = value you want to append to variable
        Returns:
            "APPEND" on successful append operation
            "NOPERM_FOR_USER" if append operation was unsuccessful (issuing user did not have valid permissions)
            "VARTYPE_NOT_SUPPORTED" if append operation was issued on variable type that is not currently supported by database
            
    '''
    def append_to_variable(self, username, variablename, value):

        # handle if the variable is not set yet
        if variablename not in self.perm_db and variablename not in self.var_value_db:
            # init permission dictionary for perm db
            self.perm_db[variablename] = {}
            # set initial perms for creator
            self.perm_db[variablename][username] = ["read", "write", "append", "delegate"]
            # set initial value for var
            self.var_value_db[variablename] = value
            return "APPEND"
        else:
            # handle if the variable is already set

            # if username is registered for the variable
            if username in self.perm_db[variablename] or "anyone" in self.perm_db[variablename]:
                # if username has append permission
                if "append" in self.perm_db[variablename][username]:
                    # append the given value to current value

                    # have to check what type of data structure it is to append correctly
                    if isinstance(self.var_value_db[variablename], (int, long, float, complex, basestring, str)):
                        if isinstance(self.var_value_db[variablename], (basestring, str)) and len(self.var_value_db[variablename]) + len(value) > 65000:
                            raise DB_Exception("FAILED")
                        self.var_value_db[variablename] += value
                    elif isinstance(self.var_value_db[variablename], list):
                        self.var_value_db[variablename].append(value)
                    elif isinstance(self.var_value_db[variablename], dict):
                        self.var_value_db[variablename].update(value)
                    else:
                        #return "VARTYPE_APPEND_NOT_SUPPORTED"
                        raise DB_Exception('Append To: VARTYPE_NOT_SUPPORTED')
                        # raise DB_Exception("FAILED")
                    return "APPEND"
                else:
                    # user does not have append permissions
                    #return "NOPERM_FOR_USER"
                    #raise DB_Exception('Append To: NOPERM_FOR_USER')
                    raise DB_Exception("DENIED")
            elif username == 'admin':
                # have to check what type of data structure it is to append correctly
                if isinstance(self.var_value_db[variablename], (int, long, float, complex, basestring, str)):
                    if isinstance(self.var_value_db[variablename], (basestring, str)) and len(
                            self.var_value_db[variablename]) + len(value) > 65000:
                        raise DB_Exception("FAILED")
                    self.var_value_db[variablename] += value
                elif isinstance(self.var_value_db[variablename], list):
                    self.var_value_db[variablename].append(value)
                elif isinstance(self.var_value_db[variablename], dict):
                    self.var_value_db[variablename].update(value)
                else:
                    # return "VARTYPE_APPEND_NOT_SUPPORTED"
                    raise DB_Exception('Append To: VARTYPE_NOT_SUPPORTED')
                    # raise DB_Exception("FAILED")
                return "APPEND"
            else:
                # user does not have any permissions for variable
                #return "NOPERM_FOR_USER"
                #raise DB_Exception('Append To: NOPERM_FOR_USER')
                raise DB_Exception("DENIED")

    '''
        get_variable: get the value for a given variable.
        Parameters:
            username = username of principal currently running script
            variablename = name of variable you want to get value from 
        Returns:
            "VAR_DOESNT_EXIST" if the requested variable does not exist
            "NOPERM" if user does not have valid (read) permission, or get was unsuccessful for any reason
            **The value of the variable** if the variable exists and the user has valid permissions
    '''
    def get_variable(self, username, variablename):

        if variablename not in self.perm_db or variablename not in self.var_value_db:
            # variable does not exist
            #return "VAR_DOESNT_EXIST"
            #raise DB_Exception('Get: VAR_DOESNT_EXIST')
            raise DB_Exception("FAILED")
        else:
            # if variable does exist
            if username in self.perm_db[variablename] or "anyone" in self.perm_db[variablename]:
                # if the user has permissions for the variable
                if "read" in self.perm_db[variablename][username]:
                    # if the user has READ permission for the variable, return value
                    return self.var_value_db[variablename]
                else:
                    # user does not have read permission
                    #return "NOPERM"
                    #raise DB_Exception("Get: NOPERM")
                    raise DB_Exception("DENIED")
            elif username == 'admin':
                return self.var_value_db[variablename]
            else:
                # user has no permissions for variable
                #return "NOPERM_FOR_USER"
                #raise DB_Exception("Get: NOPERM_FOR_USER")
                raise DB_Exception("DENIED")

    '''
        set_delegation: use this if a current principal wants to give another principal permissions. 
        Parameters:
            current_username = the username of the principal currently running script
            target_username = username of target principal to give permissions to
            permission = type of permission. can be "read" "write" "append" or "delegate"
            variablename = name of variable you want to delegate permissions for 
        Returns:
            "BAD_PERMISSION_GIVEN" if the user tries to give an invalid permission to a user (not read, write, append, delegate)
            "VAR_DOESNT_EXIST" if the requested variable to delegate does not exist
            "PERM_ALREADY_GIVEN" if the permission being delegated is already held by the target user
            "SET_DELEGATION" if the delegation operation was completed successfully 
            "NOPERM" if the issuing user does not have valid permissions to delegate
    '''
    def set_delegation(self, running_username, current_username, target_username, permission, variablename):

        if current_username != 'admin' and permission not in ["read", "write", "append", "delegate"]:
            #return "BAD_PERMISSION_GIVEN"
            #raise DB_Exception('Set Delegation: BAD_PERMISSION_GIVEN')
            raise DB_Exception("FAILED")
        if variablename not in self.perm_db or variablename not in self.var_value_db:
            # if variable does not exist
            #return "VAR_DOESNT_EXIST"
            #raise DB_Exception('Set Delegation: VAR_DOESNT_EXIST')
            raise DB_Exception("FAILED")
        else:
            # variable exists



            if running_username == current_username or running_username == 'admin':

                if current_username not in self.perm_db[variablename]:
                    raise DB_Exception("FAILURE")
                if permission not in self.perm_db[variablename][current_username]:
                    raise DB_Exception("DENIED")
                # current user has permissions for variable
                if "delegate" in self.perm_db[variablename][current_username] and permission in self.perm_db[variablename][current_username]:
                    # current user has DELEGATE permissions
                    if target_username in self.perm_db[variablename]:
                        #if target user already has permissions for variable
                        if permission in self.perm_db[variablename][target_username]:
                            # if target user already has specific permission for var
                            #return "PERM_ALREADY_GIVEN"
                            #raise DB_Exception('Set Delegation: PERM_ALREADY_GIVEN') 
                            return "SET_DELEGATION"
                            # raise DB_Exception("FAILED")
                        else:
                            # target user does not have permission for var
                            self.perm_db[variablename][target_username].append(permission)
                            return "SET_DELEGATION"
                    else:
                        # target user has never obtains perms for variable before
                        self.perm_db[variablename][target_username] = [permission]
                        return "SET_DELEGATION"
                elif running_username == 'admin':
                    if current_username in self.perm_db[variablename]:
                        if permission not in self.perm_db[variablename][current_username]:
                            # cant give permission they dont have
                            raise DB_Exception("FAILED")
                        elif target_username in self.perm_db[variablename]:
                            self.perm_db[variablename][target_username].append(permission)
                            return "SET_DELEGATION"
                        else:
                            self.perm_db[variablename][target_username] = [permission]
                            return "SET_DELEGATION"
                    else:
                        # USER can't give permission because they dont exist
                        raise DB_Exception("FAILED")
                else:
                    # current user cannot delegate
                    #return "NOPERM"
                    #raise DB_Exception('Set Delegation: NOPERM')
                    raise DB_Exception("DENIED")

            else:
                # current user has no perms for variable
                #return "NOPERM"
                #raise DB_Exception('Set Delegation: NOPERM')
                raise DB_Exception("DENIED")

    '''
        remove_delegation: use this if a current principal wants to remove permissions from another principal 
        Parameters:
            current_username = the username of the principal currently running script
            target_username = username of target principal to remove permissions from
            permission = type of permission. can be "read" "write" "append" or "delegate"
            variablename = name of variable you want to delete permissions for 
        Returns:
            "BAD_PERMISSION_GIVEN" if invalid permission was requested to remove (not read, write, append, delegate)
            "VAR_DOESNT_EXIST" if the requested variable does not exist
            "DELETE_DELEGATION" if the deletion of the permission delegation was completed successfully
            "PERMISSION_NOT_GIVEN" if the target user does not hold the requested permission to delete
            "NOPERM" if the current user does not have permissions to delegate
    '''
    def remove_delegation(self, running_username, current_username, target_username, permission, variablename):

        if permission not in ["read", "write", "append", "delegate"]:
            #return "BAD_PERMISSION_GIVEN"
            raise DB_Exception('Delete Delegation: BAD_PERMISSION_GIVEN')
            # raise DB_Exception("FAILED")
        if variablename not in self.perm_db or variablename not in self.var_value_db:
            # variable does not exist
            #return "VAR_DOESNT_EXIST"
            #raise DB_Exception('Delete Delegation: VAR_DOESNT_EXIST')
            raise DB_Exception("FAILED")
        else:
            # variable exists
            if current_username in self.perm_db[variablename] and "delegate" in self.perm_db[variablename][current_username]:
                # if current user has perms for var, and DELEGATE is one of them
                if target_username in self.perm_db[variablename]:
                    # if target user has perms for var
                    if permission in self.perm_db[variablename][target_username]:
                        # if the permission you want to remove is given to target user, remove it
                        self.perm_db[variablename][target_username].remove(permission)
                        return "DELETE_DELEGATION"
                    else:
                        # target user did not have the permission you want to revoke
                        #return "PERMISSION_NOT_GIVEN"
                        #raise DB_Exception('Delete Delegation: PERMISSION_NOT_GIVEN')
                        raise DB_Exception("DENIED")
                else:
                    # target user does not have any perms over variable
                    #return "PERMISSION_NOT_GIVEN"
                    #raise DB_Exception('Delete Delegation: PERMISSION_NOT_GIVEN')
                    raise DB_Exception("DENIED")
            elif running_username == 'admin':
                if current_username not in self.perm_db[variablename]:
                    raise DB_Exception("FAILED")
                elif 'delegate' not in self.perm_db[variablename][current_username] or permission not in self.perm_db[variablename][current_username]:
                    raise DB_Exception("FAILED")
                elif target_username not in self.perm_db[variablename] or permission not in self.perm_db[variablename][target_username]:
                    raise DB_Exception("FAILED")
                else:
                    self.perm_db[variablename][target_username].remove(permission)
                    return "DELETE_DELEGATION"

            else:
                # current user has no perms over variable
                #return "NOPERM"
                #raise DB_Exception('Delete Delegation: NOPERM')
                raise DB_Exception("DENIED")



    '''
        findall_vars_with_delegate_perm: find all variables that the given username has delegate permissions over
    '''
    def findall_vars_with_delegate_perm(self, username):
        vars_with_delegate_perm = []
        for variables in self.perm_db:
            if username in self.perm_db[variables] and username in self.perm_db[variables] and "delegate" in self.perm_db[variables][username]:
                vars_with_delegate_perm.append(variables)
        return vars_with_delegate_perm

    '''
        default_delegate: call this whenever admin calls default_delegation operation.
            When this occurs...
                for all vars that permsfrom_username has delegate permission on - 
                    give all perms that permsfrom_username has for var to delegate_username 
    '''
    def default_delegate(self, current_username, permsfrom_username, delegate_username):
        if current_username != "admin":
            #raise DB_Exception('Default Delegate: NOPERM')
            raise DB_Exception('DENIED')
        vars_to_delegate = self.findall_vars_with_delegate_perm(permsfrom_username)
        #print "found variables to delegate... :: " + str(vars_to_delegate)
        for var in vars_to_delegate:
            if permsfrom_username not in self.perm_db[var]:
                #raise DB_Exception('fatal error occurred, target user not in db?')
                raise DB_Exception("FAILED")
            if delegate_username not in self.perm_db[var]:
                self.perm_db[var][delegate_username] = self.perm_db[var][permsfrom_username]
            else:
                # merge permissions that the delegate user already has, with the perms that target_user has
                var_perms = self.perm_db[var][permsfrom_username] # permissions target user has to delegate
                delegate_varperms = self.perm_db[var][delegate_username] # permissions delegate already has
                result_varperms = var_perms
                result_varperms.extend(x for x in delegate_varperms if x not in result_varperms)
                self.perm_db[var][delegate_username] = result_varperms

        return "SUCCESS"

    def var_split(self, username, varname, split_index):
        var = self.get_variable(username, varname)
        if isinstance(var, basestring):
            return {"fst": var[:split_index], "snd": var[split_index:]}

    def var_concat(self, username, s1varname, s2varname):
        s1 = self.get_variable(username, s1varname)
        s2 = self.get_variable(username, s2varname)
        if type(s1) == type(s2) and isinstance(s1, basestring):
            return s1 + s2

    def tolower(self, username, varname):
        var = self.get_variable(username, varname)
        if isinstance(var, basestring):
            return var.lower()







''' ####################################################################### '''

###### VARIABLE DATABASE CLASS OBJECT
'''
    This object contains variables, their values, and permissions.
'''


class VARIABLE_DB:


    def __init__(self):
        print "variable database init"
        self.perm_db = {}
        self.symlink_db = {}
        self.var_value_db = {}

    def permdb_chkaccess(self, username, variablename, perm):
        # see if variablename is valid
        if variablename in self.perm_db:
            # see if username has direct access over variable
            if username in self.perm_db[variablename]:
                # check permissions
                if perm in self.perm_db[variablename][username]:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def symlink_chkaccess(self, username, variablename, perm):
        # check symlink status (permission granted by someone else)
        # verify variable in symlink table
        if variablename in self.symlink_db:
            # get table of symlinks for variable
            for entries in self.symlink_db[variablename]:
                # [GRANTEDFROM, PERM, GRANTEDTO]
                if entries[1] == perm and entries[2] == username:
                    return True

            return False
        else:
            return False

    def chkaccess(self, username, variablename, perm):
        if not self.permdb_chkaccess(username, variablename, perm) and not self.symlink_chkaccess(username, variablename, perm):
            return False
        else:
            return True


    def set_variable(self, username, variablename, value):
        # TODO
        #check varname constraints
        if len(variablename) > 255:
            raise DB_Exception("FAILED")
        elif isinstance(value, (str, basestring)) and len(value) > 65000:
            raise DB_Exception("FAILED")
        else:
            if variablename in self.var_value_db and variablename in self.perm_db:
                if self.chkaccess(username, variablename, 'write'):
                    self.var_value_db[variablename] = value
                    return "SET"
                else:
                    raise DB_Exception("DENIED")
            else:
                if variablename not in self.var_value_db:
                    self.var_value_db[variablename] = value
                # set default access
                if variablename not in self.perm_db:
                    self.perm_db[variablename] = {}

                self.perm_db[variablename][username] = ['read', 'write', 'append', 'delegate']
                self.perm_db[variablename]['admin'] = ['read', 'write', 'append', 'delegate']
                return "SET"


    def append_to_variable(self, username, variablename, value):
        # TODO
        if len(variablename) > 255:
            raise DB_Exception("FAILED")
        elif isinstance(value, (str, basestring, list, dict)) and len(value) > 6500:
            raise DB_Exception("FAILED")
        else:
            if variablename in self.var_value_db:
                if self.chkaccess(username, variablename, 'append'):
                    # verify append length will not exceed max
                    if len(self.var_value_db[variablename]) + len(value) > 6500:
                        raise DB_Exception("FAILED")

                    # verify types are the same
                    if type(self.var_value_db[variablename]) != type(value):
                        raise DB_Exception("FAILED")

                    if isinstance(self.var_value_db[variablename], (str, basestring)):
                        self.var_value_db[variablename] += value
                        return "APPEND"
                    elif isinstance(self.var_value_db[variablename], list):
                        self.var_value_db[variablename].append(value)
                        return "APPEND"
                    elif isinstance(self.var_value_db[variablename], dict):
                        self.var_value_db[variablename].update(value)
                        return "APPEND"
                    else:
                        print "unknown types requested. "
                        raise DB_Exception("FAILED")
                else:
                    raise DB_Exception("DENIED")
            else:
                raise DB_Exception("FAILED")

    def get_variable(self, username, variablename):
        # TODO
        if len(variablename) > 255 or len(username) > 255:
            raise DB_Exception("FAILED")
        else:
            if variablename in self.var_value_db:
                if self.chkaccess(username, variablename, 'read'):
                    return self.var_value_db[variablename]
                else:
                    raise DB_Exception("DENIED")
            else:
                raise DB_Exception("FAILED")


    def set_delegation(self, uname_running, uname_permfrom, uname_permto, permission, variablename):
        # TODO
        if len(uname_running) > 255 or len(uname_permfrom) > 255 or len(uname_permto) > 255 or len(variablename) > 255:
            raise DB_Exception("FAILED")
        elif permission not in ['read', 'write', 'append', 'delegate']:
            raise DB_Exception("FAILED")
        else:
            if uname_running == 'admin':
                # he can give perms even if a user doesnt have delegate perm
                if variablename not in self.symlink_db:
                    self.symlink_db[variablename] = []

                delegate_entry = [uname_permfrom, permission, uname_permto]
                if delegate_entry not in self.symlink_db[variablename]:
                    self.symlink_db[variablename].append(delegate_entry)
                    return "SET_DELEGATION"
                else:
                    return "SET_DELEGATION"
            elif uname_running == uname_permfrom:
                # check if delegation perm over variable is available for user
                if self.chkaccess(uname_permfrom, variablename, 'delegate'):
                    if variablename not in self.symlink_db:
                        self.symlink_db[variablename] = []

                    # has this perm already been given?
                    delegate_entry = [uname_permfrom, permission, uname_permto]
                    if delegate_entry not in self.symlink_db[variablename]:
                        self.symlink_db[variablename].append(delegate_entry)
                        return "SET_DELEGATION"
                    else:
                        return "SET_DELEGATION"
                else:
                    raise DB_Exception("DENIED")
            else:
                raise DB_Exception("DENIED")



    def remove_delegation(self, uname_running, uname_permfrom, uname_permto, permission, variablename):
        # TODO
        if len(uname_running) > 255 or len(uname_permfrom) > 255 or len(uname_permto) > 255 or len(variablename) > 255:
            raise DB_Exception("FAILED")
        elif permission not in ['read', 'write', 'append', 'delegate']:
            raise DB_Exception("FAILED")
        else:
            symlink_to_remove = [uname_permfrom, permission, uname_permto]
            if uname_running == 'admin':

                if variablename not in self.symlink_db:
                    return "DELETE_DELEGATION"

                if symlink_to_remove in self.symlink_db[variablename]:
                    self.symlink_db[variablename].remove(symlink_to_remove)
                    return "DELETE_DELEGATION"
                else:
                    return "DELETE_DELEGATION"

            elif uname_running == uname_permfrom:
                # if no symlinks exist for this variable, just return success
                if variablename not in self.symlink_db:
                    return "DELETE_DELEGATION"

                if self.chkaccess(uname_permfrom, variablename, permission):
                    if symlink_to_remove in self.symlink_db[variablename]:
                        self.symlink_db[variablename].remove(symlink_to_remove)
                        return "DELETE_DELEGATION"
                    else:
                        return "DELETE_DELEGATION"
                else:
                    raise DB_Exception("DENIED")
            else:
                raise DB_Exception("DENIED")

    def findall_vars_with_delegate_perm(self, username):
        #TODO
        vars_with_delegate_perm = []
        for vars in self.var_value_db:
            # check for any kind of delegate perm
            if self.chkaccess(username, vars, 'delegate'):
                vars_with_delegate_perm.append(str(vars))

        return vars_with_delegate_perm


    def default_delegate(self, current_username, permsfrom_username, permsto_username):
        # TODO
        if len(current_username) > 255 or len(permsfrom_username) > 255 or len(permsto_username) > 255:
            raise DB_Exception("FAILED")
        elif current_username != 'admin':
            print "only admin can run this function!"
            raise DB_Exception("DENIED")
        else:

            vars_w_delegate = self.findall_vars_with_delegate_perm(permsfrom_username)
            for v in vars_w_delegate:
                if self.chkaccess(permsfrom_username, v, 'read'):
                    self.set_delegation(current_username, permsfrom_username, permsto_username, 'read', v)
                if self.chkaccess(permsfrom_username, v, 'write'):
                    self.set_delegation(current_username, permsfrom_username, permsto_username, 'write', v)
                if self.chkaccess(permsfrom_username, v, 'append'):
                    self.set_delegation(current_username, permsfrom_username, permsto_username, 'append', v)
                if self.chkaccess(permsfrom_username, v, 'delegate'):
                    self.set_delegation(current_username, permsfrom_username, permsto_username, 'delegate', v)

    def var_split(self, username, varname, split_index):
        var = self.get_variable(username, varname)
        if isinstance(var, basestring):
            return {"fst": var[:split_index], "snd": var[split_index:]}

    def var_concat(self, username, s1varname, s2varname):
        s1 = self.get_variable(username, s1varname)
        s2 = self.get_variable(username, s2varname)
        if type(s1) == type(s2) and isinstance(s1, basestring):
            return s1 + s2

    def tolower(self, username, varname):
        var = self.get_variable(username, varname)
        if isinstance(var, basestring):
            return var.lower()

