# Copyright 2015 Jarrod N. Bakker
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###########################################################################
# An interactive command-line based interface for rule management of the
# Stateless SDN Firewall application.
#
# The interface will perform syntax checking on the input before sending
# it to ACLSwitch.
#
# Note that this application must be run on the controller itself.
#
# This file contains the logic for fetching and displaying state from
# ACL. This is limited to the contents of the ACL and switches with
# their currently assigned roles.
#
# Author: Jarrod N. Bakker
#

# Libraries
import json
from prettytable import PrettyTable
import requests

class ACLInterfaceShow:

    # Constants
    PROMPT_SHOW = "ACL Switch (show) > "
    TEXT_ERROR_SYNTAX = "ERROR: Incorrect syntax, could not process given command."
    TEXT_ERROR_CONNECTION = "ERROR: Unable to establish a connection with ACLSwitch."
    TEXT_HELP_SHOW = "\tinfo, role, rule OR switch"
    URL_ACLSWITCH_INFO = "http://127.0.0.1:8080/acl_switch" # using loopback
    URL_ACLSWITCH_ROLE = "http://127.0.0.1:8080/acl_switch/switch_roles" # using loopback
    URL_ACLSWITCH_RULE = "http://127.0.0.1:8080/acl_switch/acl_rules" # using loopback
    URL_ACLSWITCH_SWITCH = "http://127.0.0.1:8080/acl_switch/switches" # using loopback

    """
    Show interface. The user has the option to either view the contents of the
    ACL or view the currently connected switches and the roles associated with
    each one.
    """
    def __init__(self):
        print self.TEXT_HELP_SHOW
        buf_in = raw_input(self.PROMPT_SHOW)
        if buf_in == "rule":
            self.get_acl()
        elif buf_in == "role":
            self.get_role()
        elif buf_in == "switch":
            self.get_switch()
        elif buf_in == "info":
            self.get_info()
        else:
            print(self.TEXT_ERROR_SYNTAX + "\n" + self.TEXT_HELP_SHOW) # syntax error

    """
    Fetch the current contents of the ACL and display it to the user.
    The ACL is requested using a REST API and should be returned as JSON.
    """
    def get_acl(self):
        print("Fetching ACL...")
        try:
            resp = requests.get(self.URL_ACLSWITCH_RULE)
        except:
            print self.TEXT_ERROR_CONNECTION
            return
        if resp.status_code != 200:
            print("Error fetching resource, HTTP " + str(resp.status_code)
                  + " returned.")
            return
        acl = resp.json()
        table = PrettyTable(["Rule ID", "Source Address", "Destination Address",
                             "Transport Protocol", "Source Port",
                             "Destination Port", "Role"])
        for rule in acl:
            table.add_row([rule["rule_id"], rule["ip_src"], rule["ip_dst"],
                           rule["tp_proto"], rule["port_src"], rule["port_dst"],
                           rule["role"]])
        print table

    """
    Fetch information from ACLSwitch on the number of roles, the number
    of rules, the number of switches and the current time (approximate)
    of the machine ACLSwitch is running on.
    """
    def get_info(self):
        print("Fetching ACLSwitch information...")
        try:
            resp = requests.get(self.URL_ACLSWITCH_INFO)
        except:
            print self.TEXT_ERROR_CONNECTION
            return
        if resp.status_code != 200:
            print("Error fetching resource, HTTP " + str(resp.status_code)
                  + " returned.")
            return
        info = resp.json()
        table = PrettyTable(["Number of Roles","Number of Rules",
                             "Number of Switches",
                             "Current ACLSwitch time (approx.)"])
        table.add_row([info["num_roles"], info["num_rules"],
                       info["num_switches"], info["controller_time"]])
        print table

    """
    Fetch a list of the currently available roles from the ACLSwitch.
    """
    def get_role(self):
        print("Fetching role information...")
        try:
            resp = requests.get(self.URL_ACLSWITCH_ROLE)
        except:
            print self.TEXT_ERROR_CONNECTION
            return
        if resp.status_code != 200:
            print("Error fetching resource, HTTP " + str(resp.status_code)
                  + " returned.")
            return
        roles = resp.json()
        table = PrettyTable(["Roles"])
        for entry in roles["Roles"]:
            table.add_row(entry.split())
        print table

    """
    Fetch a list of the current switches and the roles associated with
    them from the ACLSwitch.
    """
    def get_switch(self):
        print("Fetching switch information...")
        try:
            resp = requests.get(self.URL_ACLSWITCH_SWITCH)
        except:
            print self.TEXT_ERROR_CONNECTION
            return
        if resp.status_code != 200:
            print("Error fetching resource, HTTP " + str(resp.status_code)
                  + " returned.")
            return
        switches = resp.json()
        table = PrettyTable(["Switch Datapath ID", "Roles"])
        for entry in switches:
            table.add_row([entry, ','.join(switches[entry])])
        print table

