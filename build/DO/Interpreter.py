import ply.lex as lex
import ply.yacc as yacc
from Commands import *
from database import *

#CLASSES FOR VALUES/EXPRESSIONS/FIELDVALS..

#type can be identifier,access,string
class Value(object):
    def __init__(self,_data,_type):
        self.data = _data
        self.type = _type

    def evaluate(self,_user,_locals,_var_db,_user_db):
        #This function evaluates a Value and returns what ever it is
        #Value := identifier, string, access
        if self.type == 'string':
            return self.data
        
        elif self.type == 'identifier':
            #is this identifier in local or global?
            if self.data in _locals:
                return _locals[self.data]
            else:
                return _var_db.get_variable(_user,self.data)
        elif self.type == 'access':
            #can only operate on records.. is it in global or local?
            if self.data[0] in _locals:
                rec = _locals[self.data[0]]
            else:
                rec = _var_db.get_variable(_user,self.data[0])#grab from db
            
            if isinstance(rec,dict):
                if self.data[1] in rec:
                    return rec[self.data[1]]
                else:
                    print 'value (no entry)'
                    raise DB_Exception('FAILED') #no entry for access
            else:
                print 'value (no entry)'
                raise DB_Exception('FAILED') #not a record
        else:
            raise DB_Exception('VALUE: Unexepected state in evaluate')

#type can be value,list,record
class Expression(object):
    def __init__(self,_data,_type):
        self.data = _data
        self.type = _type

    #this function is used for the foreach statement.
    #_var_name is a special case, {foreach x in y repalce with x.p}
    #_var_name is x and checks if the access in use with this var
    def expr_in_dict(self,_dict,_var_name):
        #print "in expr_in_dict"
        #print self.type
        #print self.data.data
        if self.type == 'record':
            ret_dict = {}
            for i in self.data:
                #print i
                if i in _dict:
                    return _dict[i]
            return False
        if self.type == 'value':
            val = self.data
            #identifier or access
            if val.type == 'identifier':
                if val.data in _dict:
                    return _dict[val.data]
                else:
                    return False
            elif val.type == 'access':
                val_tup = val.data
                #print val.data
                #print val_tup
                if val_tup[0] == _var_name and val_tup[1] in _dict:
                    return _dict[val_tup[1]]
                else:
                    return False
            elif val.type == 'string':
                return False
        raise DB_Exception('EXPR_IN_DICT reached an unexpected state')


    def evaluate(self,_user,_locals,_var_db,_user_db):
        #This function evaluates an expression and returns what ever it is
        #Expression := value, [], record
        if self.type == 'value':
            expr = self.data.evaluate(_user,_locals,_var_db,_user_db)

        elif self.type == 'record':
            #record fields can only contain labels and strings
            #TODO: keeping order, and uniqueness..
            record_dict = {}
            if len([x[0].data for x in self.data]) != len(set([x[0].data for x in self.data])): raise DB_Exception('FAILED') #multiple entries
            for value_tuple in self.data:
                if value_tuple[0].type == 'identifier':
                    #fetch the other value
                    val = value_tuple[1].evaluate(_user,_locals,_var_db,_user_db)
                    if isinstance(val,str):
                        record_dict[value_tuple[0].data] = val
                    else:
                        raise DB_Exception('FAILED') #not a string
                else:
                    raise DB_Exception('FAILED') #not an identifier
            expr = record_dict
        elif self.type == 'list':
            expr = []
        else:
            raise DB_Exception('EXPR: Unexpected state in evaluate')
        return expr


class DB_Interpreter(object):
    def __init__(self,_user_db,_var_db,_lex_debug_level=0,_yacc_debug_level=0):
        #token place holder for parsing the lexer
        self.last_token = None #debugging value, should never be called in DB interaction (it is temporory)
        self.lex_debug_level = _lex_debug_level #optional debugging values, default to 0, for debugging use 1
        self.yacc_debug_level = _yacc_debug_level
        self.is_correct_grammar = None #boolean for if the grammar is valid. this gets set and returned when we call parse()
        self.data = None
        self.cmd_obj = cmd() #cmd object is used to hold all the info about the program we parsed
        self.user_db = _user_db
        self.var_db = _var_db
        self.status_list = [] #holds the status of each command that is executed.
        self.local_vals = {} #local dictionary to hold temporary local vars
        self.parse_error = None
    #build the lexer and interp
    def build(self):
        self.lexer = lex.lex(object=self,debug=self.lex_debug_level)
        self.interpreter = yacc.yacc(module=self,debug=self.yacc_debug_level,start='prog')
        self.temp_list = []
        self.status_list = []
        self.cmd_obj = cmd()
    #set the input for the lexer and interpreter
    def input(self,_input):
        self.lexer.input(_input)
        self.data = _input

    #parses the tokens from lexer, returns true if the grammar was correct.
    def parse(self,_input):
        self.interpreter.parse(_input,lexer=self.lexer)
        return self.is_correct_grammar

    def print_tokens(self,input):
        self.lexer.input(input)
        tok_list = []
        for tok in iter(self.lexer.token,None):
            tok_list.append(tok)
        return tok_list

    def fetch_status_list(self):
        return self.status_list

    def refresh(self):
        self.status_list = [] #holds the status of each command that is executed.
        self.local_vals = {} #local dictionary to hold temporary local vars
        self.cmd_obj = cmd()
        self.temp_list = []

    def execute_commands(self):
        command_list = self.cmd_obj.prim_cmd
        #reverse the command list to execution order
        command_list.reverse()
        #print command_list
        for command in command_list:
            self.status_list.append(command.execute(self.user,self.password,self.user_db,self.var_db,self.local_vals)) 
        #print "Status list:%s\n"%(self.status_list)
        #print "Variables after commands:%s\n"%(self.var_db.var_value_db)
        #print "Local varialbes after commands: %s"%(self.local_vals)
        #print "Varialbe Delegation after commands:%s\n"%(self.var_db.perm_db)
        #print "Users after commands:%s\n"%(self.user_db.user_db)

        return self.user_db, self.var_db



    #Private members that are used for parsing and lexical tokenization

    #Reserved special names
    reserved_keywords = {
        'all' : 'ALL',
        'append' : 'APPEND',
        'as' : 'AS',
        'change' : 'CHANGE',
        'create' : 'CREATE',
        'default' : 'DEFAULT',
        'delegate' : 'DELEGATE',
        'delegation' : 'DELEGATION',
        'delegator' : 'DELEGATOR',
        'delete' : 'DELETE_',
        'do' : 'DO',
        'exit' : 'EXIT',
        'foreach' : 'FOREACH',
        'in' : 'IN',
        'local' : 'LOCAL',
        'password' : 'PASSWORD',
        'principal' : 'PRINCIPAL',
        'read' : 'READ',
        'replacewith' : 'REPLACEWITH',
        'return' : 'RETURN',
        'set' : 'SET',
        'to' : 'TO',
        'write' : 'WRITE',
        #Extra Credit
        'split' : 'SPLIT',
        'concat' : 'CONCAT',
        'tolower' : 'TOLOWER',
        'notequal' : 'NOTEQUAL',
        'equal' : 'EQUAL',
        'filtereach' : 'FILTEREACH',
        'with' : 'WITH',
        'let' : 'LET',
    }

    tokens = [
        'STRING_CONSTANT',
        'ASSIGN',
        'APPEND_TO',
        'RIGHT',
        'IDENTIFIER',
        'EQUALSIGN',
        'NEWLINE',
        'COMMENT',
        'LBRACKET',
        'RBRACKET',
        'LCURLYBRACE',
        'RCURLYBRACE',
        'COMMA',
        'DOT',
        'RIGHTARROW',
        'ENDPROG',
        ] + list(reserved_keywords.values())

    #REGEX rules for tokens

    def t_STRING_CONSTANT(self,t):
        r'\"[ A-Za-z0-9_,;\\.?!-]*\"' #set string limit
        if len(t.value) > 65537:
            raise DB_Exception('FAILED')
        return t
    t_EQUALSIGN = r'\='
    t_NEWLINE = r'\n'
    t_ASSIGN = r'\-\>'

    #instead of consuming comments we replace them with a newline
    def t_COMMENT(self,t):
        r'//.*\n'
        t.type = 'NEWLINE'
        t.value = '\n'
        return t

    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LCURLYBRACE = r'\{'
    t_RCURLYBRACE = r'\}'
    t_RIGHTARROW = r'\-\>'
    t_COMMA = r'\,'
    t_DOT = r'\.'
    t_ENDPROG = r'\*\*\*'


    #Ignore whitespace
    t_ignore = ' \t'

    def t_APPEND_TO(self,t):
        r'append[ ]+to'
        t.type = 'APPEND_TO'
        t.value = 'append to'
        return t

    
    def t_RIGHT(self,t):
        r'read|write|append|delegate'
        #t.type = 'RIGHT'
        return t
    #Insure that a potential identifier is not in the reserved keywords set. If it is
    #set the appropriate type, if not then we have an identifier.
    def t_IDENTIFIER(self,t):
        r'[A-Za-z][A-Za-z0-9_]*' #limit length to 255 
        if len(t.value) > 255:
            raise DB_Exception('FAILED')
        if t.value in self.reserved_keywords:
            t.type = self.reserved_keywords.get(t.value,self.reserved_keywords[t.value])
        return t

    #TODO: Check this works as intended.
    def t_error(self,t):                        
        print "Illegal character: %s" %(t.value[0])
        t.lexer.skip(1)

    #Grammar rules to check if the tokenized values follow the defined grammar
    #Creates AST and traverses it. In the process of traversal it creates prim-cmd/expr objects 
    #and puts them into the prim_cmd list.


    def p_prog(self,p):
        'prog : AS PRINCIPAL IDENTIFIER PASSWORD STRING_CONSTANT DO NEWLINE cmd ENDPROG NEWLINE'
        #If yacc gets to this point then the entire program is in the correct format
        self.is_correct_grammar = True
        self.user = p[3]
        self.password = p[5]
        self.local_vals = {} #Each time a program is run the local vars should all go out of scope./
        self.cmd_obj.add_cmd(Login_cmd(self.user,self.password))
        # self.cmd_obj.user = p[3]
        # self.cmd_obj.password = p[5]

    def p_prog_with_newline(self,p):
            'prog : NEWLINE AS PRINCIPAL IDENTIFIER PASSWORD STRING_CONSTANT DO NEWLINE cmd ENDPROG NEWLINE'
            #If yacc gets to this point then the entire program is in the correct format
            self.is_correct_grammar = True
            self.user = p[4]
            self.password = p[6]
            self.local_vals = {} #Each time a program is run the local vars should all go out of scope./
            self.cmd_obj.add_cmd(Login_cmd(self.user,self.password))
            # self.cmd_obj.user = p[3]
            # self.cmd_obj.password = p[5]


    def p_cmd_exit(self,p):
        'cmd : EXIT NEWLINE'
        self.cmd_obj.add_cmd(Exit_cmd())

    def p_cmd_return(self,p):
        'cmd : RETURN expr NEWLINE'
        self.cmd_obj.add_cmd(Return_cmd(p[2]))

    def p_cmd_primcmd_cmd(self,p):
        'cmd : prim_cmd NEWLINE cmd'
        self.cmd_obj.add_cmd(p[1])

    #Expression here is a string
    def p_expr_value(self,p):
        'expr : value'
        #print "(expr:=value[%s])"%(p[1].str())
        p[0] = Expression(p[1],'value')

    def p_expr_brackets(self,p):
        'expr : LBRACKET RBRACKET' #TODO nothing done for this yet
        p[0] = Expression('[]','list') #empty list

    def p_expr_fieldvals(self,p):
        'expr : LCURLYBRACE fieldvals RCURLYBRACE'
        self.temp_list.reverse() #reverse the list so it is in the correct order
        #print "EXPR GOT:%s"%(self.temp_list)
        p[0] = Expression(self.temp_list,'record')


    def p_fieldvars_val_eq_val(self,p):
        'fieldvals : IDENTIFIER EQUALSIGN value'
        #print "(fieldval:=ident=val)"
        self.temp_list = [] #this is the deepest node in the tree so we clear the list here.
        self.temp_list.append((Value(p[1],'identifier'),p[3]))

    def p_fieldvars_val_eq_val_comma_fieldvars(self,p):
        'fieldvals : IDENTIFIER EQUALSIGN value COMMA fieldvals'
        #fieldvals = Fieldvals()
        if p[1] != None and p[3] != None:
            self.temp_list.append((Value(p[1],'identifier'),p[3]))


    def p_value_ident(self,p):
        'value : IDENTIFIER'
        p[0] = Value(p[1],'identifier')

    def p_value_ident_dot_ident(self,p):
        'value : IDENTIFIER DOT IDENTIFIER'
        p[0] = Value([p[1],p[3]],'access')

    def p_value_string(self,p):
        'value : STRING_CONSTANT'
        p[0] = Value(p[1],'string')

    def p_prim_cmd_create_principal(self,p):
        'prim_cmd : CREATE PRINCIPAL IDENTIFIER STRING_CONSTANT'
        p[0] = Create_Prince_cmd(p[3],p[4])

    def p_prim_cmd_change_password(self,p):
        'prim_cmd : CHANGE PASSWORD IDENTIFIER STRING_CONSTANT'
        p[0] = Change_Password_cmd(p[3],p[4])

    def p_prim_cmd_set(self,p):
        'prim_cmd : SET IDENTIFIER EQUALSIGN expr'
        p[0] = Set_cmd(p[2],p[4])

    def p_prim_cmd_append(self,p):
        'prim_cmd : APPEND_TO IDENTIFIER WITH expr'
        p[0] = Append_to_cmd(p[2],p[4])

    def p_prim_local_set(self,p):
        'prim_cmd : LOCAL IDENTIFIER EQUALSIGN expr'
        p[0] = Local_cmd(p[2],p[4])

    #TODO check if we have to use expr and identifier
    def p_prim_foreach_replace(self,p):
        'prim_cmd : FOREACH IDENTIFIER IN IDENTIFIER REPLACEWITH expr'
        p[0] = Foreach_cmd(p[2],p[4],p[6])

    def p_prim_set_del_all(self,p):
        'prim_cmd : SET DELEGATION ALL IDENTIFIER RIGHT RIGHTARROW IDENTIFIER'
        p[0] = Set_Delegation_cmd(p[3],p[4],p[5],p[7])

    def p_prim_set_del(self,p):
        'prim_cmd : SET DELEGATION IDENTIFIER IDENTIFIER RIGHT RIGHTARROW IDENTIFIER'
        p[0] = Set_Delegation_cmd(p[3],p[4],p[5],p[7])

    def p_prim_del_del(self,p):
        'prim_cmd : DELETE_ DELEGATION IDENTIFIER IDENTIFIER RIGHT RIGHTARROW IDENTIFIER'
        p[0] = Delete_Delegation_cmd(p[3],p[4],p[5],p[7])

    def p_prim_del_del_all(self,p):
        'prim_cmd : DELETE_ DELEGATION ALL IDENTIFIER RIGHT RIGHTARROW IDENTIFIER'
        p[0] = Delete_Delegation_cmd(p[3],p[4],p[5],p[7])

    def p_def_def(self,p):
        'prim_cmd : DEFAULT DELEGATOR EQUALSIGN IDENTIFIER'
        p[0] = Default_Delegator_cmd(p[4])

    def p_error(self,p):
        if p:
            self.parse_error = "Syntax error at '%s:%s:%s'" % (p.value,p.lineno,p.lexpos)
            print "Syntax error at '%s:%s:%s'" % (p.value,p.lineno,p.lexpos)

        else:
            self.parse_error = "Error without P\n"
        self.is_correct_grammar = False #TODO: Do we need more informatin here?>
        raise DB_Exception("FAILED")