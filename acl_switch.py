# Author: Jarrod N. Bakker
# Part of an ENGR489 project at Victoria University of Wellington
# during 2015.
#
# This file manages the flow table and keeps an ACL. When we see
# a new flow, we check it against the ACL and decide if we allow
# or drop the packet from there.
#
# Because rules which block traffic are important to the security
# of a network, the priority of such rules should be higher than
# the rules which allow traffic to flow. Currently, the default
# priority value is used for rules which allow traffic and the max
# value is used for rules which block traffic. Later on it may be
# possible to specify custom priorities.
#
# The original license for simple_switch_13.py can be found below.
#
####################################################################
# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#####################################################################

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
# I have added the below libraries to this code
from ryu.lib.packet import ipv4
from collections import namedtuple

class ACLSwitch(app_manager.RyuApp):
    # Constants
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    OFP_MAX_PRIORITY = ofproto_v1_3.OFP_DEFAULT_PRIORITY*2 - 1
            # Default priority is defined to be in the middle (0x8000 in 1.3)
            # Note that for a priority p, 0 <= p <= MAX (i.e. 65535)
    ACL_ENTRY = namedtuple("ACL_ENTRY", "ip_src ip_dst port_src port_dst")

    # Fields
    access_control_list = []

    def __init__(self, *args, **kwargs):
        super(ACLSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        #self.rule_input()
        self.access_control_list.append(self.ACL_ENTRY(ip_src="10.0.0.1", ip_dst="10.0.0.3", port_src="", port_dst=""))
#        self.access_control_list.append(self.ACL_ENTRY(ip_src="10.0.0.1", ip_dst="10.0.0.2", port_src="12345", port_dst="12345"))
        print self.access_control_list
    
    def rule_input(self):
        # Continuously wait for the user to input rules for blocking
        # traffic.
        while True:
            rule = raw_input("Rule ::= Source IP, Destination IP\n ")
            print str(rule)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    # The incoming flow has IPv4. Search through the ACL for a match and 
    # return the correct OF match and actions.
    # @return - if a rule in the ACL is found: the matching rules and
    #           actions for the switches to follow, otherwise False.
    # TODO have a separate ACL for IPv4 ad IPv6
    # TODO instead of flows being installed here, have this function return the actions and match etc.
    def ipv4_match(self, ipv4_head, parser):
        print "[+] IPv4 Header: " + str(ipv4_head)
        ipv4_dst = ipv4_head.dst
        ipv4_src = ipv4_head.src
        for rule in self.access_control_list:
            if (ipv4_src == rule.ip_src and ipv4_dst == rule.ip_dst):
                # We have found flow which matches a rule in the ACL.
                print "\n[-] ACL Match found: creating action to block traffic.\n"
                priority = self.OFP_MAX_PRIORITY
                # Create the matching rule for OF switches
                # TODO investigate weird errors when including ip_type. See note book.
                match = parser.OFPMatch(eth_type = ethernet.ETH_TYPE_IP, ipv4_src = rule.ip_src, ipv4_dst = rule.ip_dst)
                # A match with empty actions means that the switch
                # should drop packets within the flow
                actions = []
                # Return 
                return (priority, match, actions)
        # A match was not found so return False
        return False

    # The incoming flow has IPv6. Search through the ACl for a match.
    # @return - if a match was found (True) or not (False)
    # TODO add support for IPv6
    def ipv6_flow(self, ipv6_head, datapath, match, actions, message, ofproto):
        ipv6_found_acl_match = False
        return ipv_found_acl_match

    # The incoming flow does not match any rule in the ACL. Therefore add a
    # rule which allows the traffic to flow through.
    # @return - if the buffer_id is valid (True) or not (False)
    # TODO does this function need the entire event message or just the 
    # buffer id? (just in case)
    def allow_flow(self, datapath, priority, match, actions, message, ofproto):
        # verify if we have a valid buffer_id, if yes avoid to send both
        # flow_mod & packet_out
        if message.buffer_id != ofproto.OFP_NO_BUFFER:
            self.add_flow(datapath, priority, match, actions, message.buffer_id)
            return False
        else:
            self.add_flow(datapath, priority, match, actions)
        return True

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth_head = pkt.get_protocols(ethernet.ethernet)[0]

        eth_dst = eth_head.dst
        eth_src = eth_head.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, eth_src, eth_dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][eth_src] = in_port

        if eth_dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][eth_dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=eth_dst)
            
            print ("\n[+] New flow detected: checking ACL.\n")
            priority = ofproto_v1_3.OFP_DEFAULT_PRIORITY
            # Assume IPv4 packets only
            # TODO add IPv6 support
            # TODO block traffic in one direction
            data = pkt.get_protocols(ipv4.ipv4)
            if (data):
                ipv4_head = data[0]
                pma = self.ipv4_match(ipv4_head, parser) # Priority Match Action
                print "[#] " + str(pma)
            #    found_acl_match = self.ipv4_flow(ipv4_head, datapath, match, actions, msg, ofproto);
            #    if found_acl_match == False:
            #        priority = 1
            #        if self.allow_flow(datapath, priority, match, actions, msg, ofproto) == False:
            #            return
            
                # If a match was found in the ACL, then the new flow must
                # have the associated match rules and actions assigned to it.
                if pma != False:
                    priority = pma[0]
                    match = pma[1]
                    actions = pma [2]
                    # TODO this makes an error happen: OFPET_BAD_MATCH code 9 (a prerequisite was not met)

            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, priority, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, priority, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
