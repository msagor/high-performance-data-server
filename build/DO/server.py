#!/usr/bin/python
import sys
import socket
import database
import unit_tests
import Interpreter #interpreter file
from Commands import DB_Exception
import json
import copy
import signal
import os
import time


def sigterm_handler(signal, frame):
    # save the state here or do whatever you want
    print('booyah! bye bye')
    SRV_CONNECTION.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

print "given args: " + str(sys.argv)
RESERVED_WORDS = ["all", "append", "as", "change", "create", "default", "delegate", "delegation", "delegator", "delete", "do", "exit", "foreach", "in", "local", "password", "principal", "read", "reaplacewith", "return", "set", "to", "write", "***"]
RESERVED_EXTRA_WORDS = ["split", "concat", "tolower", "notequal", "equal", "filtereach", "with", "let"]


PERFORM_UNIT_TESTS = False


if PERFORM_UNIT_TESTS:
    # perform tests for database
    unit_tests.UNIT_TESTS()



###### PORT HANDLING
if len(sys.argv) != 2 and len(sys.argv) != 3:
    print "invalid argument length given. shutting down. "
    print "usage: python server.py PORT [PASSWORD] "
    exit(1)
if not sys.argv[1].isdigit():
    print "given port argument is not an integer. shutting down. "
    exit(1)
SRV_PORT = int(sys.argv[1])
if SRV_PORT < 1024 or SRV_PORT > 65535:
    print "given port is out of acceptable range. shutting down. "
    exit(1)



###### PASSWORD HANDLING
SRV_PASSWORD = "\"admin\""
if len(sys.argv) == 3:
    SRV_PASSWORD = sys.argv[2]
    print SRV_PASSWORD

print "RESULT: server port(" + str(SRV_PORT) + ") server password(" + SRV_PASSWORD + ")"


###### INITIALIZE GLOBAL VARIABLE DATABASE
VAR_DATABASE = database.VARIABLE_DB()


###### INITIALIZE GLOBAL USER DATABASE, ADD ADMIN
USER_DATABASE = database.USER_DB()
USER_DATABASE.INIT_user("admin", "anyone", SRV_PASSWORD)
USER_DATABASE.INIT_user("admin", "admin", SRV_PASSWORD)


###### CONNECTION HANDLING FOR CLIENTS (RECV THE REQUESTED CODE TO EXECUTE)
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SRV_ADDRESS = ('localhost', SRV_PORT)
SOCKET.bind(SRV_ADDRESS)

print "starting server... please wait"

SOCKET.listen(1)

server_alive = True

#Create, and build an interpreter to handle the incoming commands
user_db = None
global_program = ""
while True:
    # wait for a connection
    try:
        print "waiting for a connection... "
        SRV_CONNECTION, CLIENT_ADDR = SOCKET.accept()
        terminating_code = "***\n"

        print "connection established from address " + str(CLIENT_ADDR)
        input_program = ""
        while server_alive:

            data = SRV_CONNECTION.recv(4096)

            if data:
                #print "GOT THE FOLLOWING INFORMATION:  \n|" + str(data) + "|"
                print str(data)
                input_program += data
                if data == "***" or data == "***\n":
                    break #TODO doesn't always find the end.
                else:
                    break #TODO fix this logic, used for catting files of NC
            else:
                print "No more data from " + str(CLIENT_ADDR)
                break

        #input_program = input_program[:-1] #TODO: Remove me, this line is for handling files that are catted via netcat
        # print "the following program was received: \n" + str(input_program)
        parsed_programs = []
        parse_string = ""
        program_list = [x for x in input_program.split("\n")]
        for i in program_list:
            if i != '':
                parse_string += i + '\n'
                if i == '***':
                    parsed_programs.append(parse_string)
                    parse_string = ""

    #################################################
    ########## PROCESS REQUEST INFORMATION HERE #####
        for i in parsed_programs:

            global_program = i
            user_db_copy = copy.deepcopy(USER_DATABASE)
            var_db_copy = copy.deepcopy(VAR_DATABASE)

            command_interpreter = Interpreter.DB_Interpreter(user_db_copy,var_db_copy)
            command_interpreter.build()

            command_interpreter.input(i)
            print command_interpreter.user_db.user_db

            if command_interpreter.parse(i):
                #program is in a valid format
                user_db ,var_db = command_interpreter.execute_commands()
                #Get Status List:
                status = command_interpreter.fetch_status_list()

                status = status[1:]
                #status = [x[0] for x in status] #UNCOMMENT WHEN DELETING WHAT IS BELOW

                for s in status:
                    #TODO Delete this it is only for debugging
                    if isinstance(s,list):
                        s = s[0]
                    SRV_CONNECTION.send(s+'\n')


                ##If there were no exceptions then change the states
                if user_db:
                    print "copying data"
                    USER_DATABASE = user_db
                    VAR_DATABASE = var_db

                else:
                    print "There was an error processing the input from the network.\n"

        SRV_CONNECTION.close()

    except KeyboardInterrupt:
        #TODO close the server
        print "\nkeyboard interrupt detected. exiting... "
        exit(0)
    except DB_Exception as err:
        print "Got DB_Exception: %s\n"%(err.args)
        user_db_copy = copy.deepcopy(USER_DATABASE) #roll back just in case something wonky happens
        var_db_copy = copy.deepcopy(VAR_DATABASE) #roll back just in case something wonky happens
        user_db = None
        if err.args[0] == 'FAILED':
            SRV_CONNECTION.send('{"status":"FAILED"}\n')
            command_interpreter.refresh()
            SRV_CONNECTION.close()
        elif err.args[0] == 'DENIED':
            SRV_CONNECTION.send('{"status":"DENIED"}\n')
            command_interpreter.refresh()
            SRV_CONNECTION.close()
        else:
            print err.args
            parse_error = command_interpreter.parse_error
            print "Got Parse Error:%s"%(parse_error)
            if parse_error:
                SRV_CONNECTION.send(parse_error + '\n')
            #Probably a parser error
            bad_program = command_interpreter.print_tokens(global_program)
            for i in bad_program:
                print i
                SRV_CONNECTION.send("%s"%(i)+'\n')
            SRV_CONNECTION.close()
        #TODO: Proper error handeling if needed...(Deined vs Failed..)
        #command_interpreter.print_tokens(input_program)

print "server exiting. have a good day. "
sys.exit(0)
