# An interactive command-line based interface for rule management of the
# Stateless SDN Firewall application.
#
# The interface will perform syntax checking on the input before sending
# it to ACLSwitch.
#
# Note that this application must be run on the controller itself.
#
# This file contains the logic for starting the interface program and
# directing control to other interface functions.
#
# Author: Jarrod N. Bakker
#

# Libraries
import json
import requests

class ACLInterfaceRole:

    # Constants
    PROMPT_ROLE = "ACL Switch (role) > "
    PROMPT_ROLE_ASSIGN = "ACL Switch (role -> assign) > "
    PROMPT_ROLE_REMOVE = "ACL Switch (role -> remove) > "
    TEXT_ERROR_SYNTAX = "ERROR: Incorrect syntax, could not process given command."
    TEXT_ERROR_CONNECTION = "ERROR: Unable to establish a connection with ACLSwitch."
    TEXT_HELP_ROLE = "\tassign OR remove"
    TEXT_HELP_ROLE_ASSIGN = "\tRole to assign: switch_id role"
    TEXT_HELP_ROLE_REMOVE = "\tRole to remove: switch_id role"
    URL_ACLSWITCH_ROLE = "http://127.0.0.1:8080/acl_switch/switch_roles" # using loopback
    
    """
    Assign interface. The user can assign or remove a role from a switch.
    This allows the switch to block different ranges of traffic compared
    to other switches within the network.
    """
    def __init__(self):
        print self.TEXT_HELP_ROLE
        buf_in = raw_input(self.PROMPT_ROLE)
        if buf_in == "assign":
            self.role_assign()
        elif buf_in == "remove":
            self.role_remove()
        else:
            print(self.TEXT_ERROR_SYNTAX + "\n" + self.TEXT_HELP_ROLE) # syntax error
    

    """
    Assign a role to a switch.
    """
    def role_assign(self):
        print self.TEXT_HELP_ROLE_ASSIGN
        buf_in = raw_input(self.PROMPT_ROLE_ASSIGN)
        new_assign = buf_in.split(" ")
        try:
            int(new_assign[0])
            if int(new_assign[0]) < 1:
                print "Switch id should be a positive integer greater than 1."
                return
        except:
            print "Switch id should be a positive integer greater than 1."
            return
        if new_assign[1] != "df" and new_assign[1] != "gw":
            print "Invalid role provided. \'df\' or \'gw\' expected."
            return
        assign_req = json.dumps({"switch_id":new_assign[0],
                                 "new_role":new_assign[1]})
        try:
            resp = requests.put(URL_ACLSWITCH_ROLE, data=assign_req,
                                headers = {"Content-type":"application/json"})
        except:
            print self.TEXT_ERROR_CONNECTION
            return
        print resp.text

    """
    Remove an assigned role from a switch.
    """
    def role_remove(self):
        print self.TEXT_HELP_ROLE_REMOVE
        buf_in = raw_input(self.PROMPT_ROLE_REMOVE)
        removal = buf_in.split(" ")
        try:
            int(removal[0])
            if int(removal[0]) < 1:
                print "Switch id should be a positive integer greater than 1."
                return
        except:
            print "Switch id should be a positive integer greater than 1."
            return
        if removal[1] != "df" and removal[1] != "gw":
            print "Invalid role provided. \'df\' or \'gw\' expected."
            return
        remove_req = json.dumps({"switch_id":removal[0],
                                 "new_role":removal[1]})
        try:
            resp = requests.put(URL_ACLSWITCH_ROLE, data=remove_req,
                                headers = {"Content-type":"application/json"})
        except:
            print self.TEXT_ERROR_CONNECTION
            return
        print resp.text
