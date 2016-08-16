"""Remote: Support for gateway interface for remote containers using JSON over TCP/IP.

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

TODO:
    * Resolve TODOs in the code

"""
import os as _os
import sys as _sys
import json as _json
import uuid as _uuid
import time as _time
import socket as _socket
import multiprocessing as _mp
from messages import Action
from messages import Message
from messages import GenericMessage

class AgentID:
    """An identifier for an agent or a topic."""

    def __init__(self, name, is_topic = False):
            self.name = name
            if is_topic:
                self.is_topic = True
            else:
                self.is_topic = False

class Gateway:
    """Gateway to communicate with agents from python.

    Supported JSON keys:
        id
        action
        inResponseTo
        agentID
        agentIDs
        service
        services
        answer
        message
        relay
    """

    def __init__(self, ip, port, name = None):
        """NOTE: Developer must make sure a duplicate name is not assigned to the Gateway."""

        try:
            if name == None:
                self.name = "PythonGW-"+str(_uuid.uuid4())
            else:
                try:
                    self.name = name
                except Exception, e:
                    print "Exception: Cannot assign name to gateway: " + str(e)
                    _sys.exit(0)

            self.q = _mp.Manager().list()
            self.subscribers = _mp.Manager().list()
            self.s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
            self.s.connect((ip, port))
            self.recv = _mp.Process(target=self.__recv_proc, args=(self.q, self.subscribers, ))
            self.recv.start()

        except Exception, e:
            print "Exception: " + str(e)
            _sys.exit(0)

    def parse_incoming(self, rmsg, q):
        """Parse incoming messages and respond to them"""

        req = _json.loads(rmsg)
        rsp = dict()

        for key, value in req.items():
            rsp.clear()
            if key == 'action':

                if value == Action.AGENTS:
                    print "ACTION: " + Action.AGENTS
                    
                    rsp["inResponseTo"] = req["action"]
                    rsp["id"]           = req["id"]
                    rsp["agentIDs"]     = self.name
                    self.s.sendall(_json.dumps(rsp) + '\n')

                elif value == Action.CONTAINS_AGENT:
                    print "ACTION: " + Action.CONTAINS_AGENT

                    rsp["inResponseTo"] = req["action"]
                    rsp["id"]           = req["id"]
                    answer = False
                    if req["agentID"]:
                        if req["agentID"] == self.name:
                            answer = True
                    rsp["answer"]       = answer
                    self.s.sendall(_json.dumps(rsp) + '\n')

                elif value == Action.SERVICES:
                    print "ACTION: " + Action.SERVICES

                    rsp["inResponseTo"] = req["action"]
                    rsp["id"]           = req["id"]
                    rsp["services"]     = []
                    self.s.sendall(_json.dumps(rsp) + '\n')

                elif value == Action.AGENT_FOR_SERVICE:
                    print "ACTION: " + Action.AGENT_FOR_SERVICE

                    rsp["inResponseTo"] = req["action"]
                    rsp["id"]           = req["id"]
                    rsp["agentID"]      = ""
                    self.s.sendall(_json.dumps(rsp) + '\n')

                elif value == Action.AGENTS_FOR_SERVICE:
                    print "ACTION: " + Action.AGENTS_FOR_SERVICE

                    rsp["inResponseTo"] = req["action"]
                    rsp["id"]           = req["id"]
                    rsp["agentIDs"]     = []
                    self.s.sendall(_json.dumps(rsp) + '\n')

                elif value == Action.SEND:
                    #TODO: add message to queue only if:
                        # 1. if the aid is same as gateway's id/name or
                        # 2. the message is for a topic in the subscribers list
                    print "ACTION: " + Action.SEND
                    try:
                        #TODO: There is a broken pipe error when the server tries to send a message. Investigate
                        q.append(req["message"])
                    except Exception, e:
                        print "Exception: Error adding to queue - " + str(e)

                elif value == Action.SHUTDOWN:
                    print "ACTION: " + Action.SHUTDOWN
                    return None

                else:
                    print "Invalid message, discarding"

        return True

    def __recv_proc(self, q, subscribers):
        """Receive process."""

        self.s.setblocking(0)
        parenthesis_count = 0
        rmsg = ""

        #TODO: Avoid polling to reduce CPU load?
        while True:
            try:
                c = self.s.recv(1)
                rmsg = rmsg + c

                if c == '{':
                    parenthesis_count += 1
                if c == '}':
                    parenthesis_count -= 1
                    if parenthesis_count == 0:
                        # print "Received: " + rmsg
                        msg = self.parse_incoming(rmsg, q)

                        if msg == None:
                            break

                        rmsg = ""
            except:
                pass

    def __del__(self):
        try:
            self.s.close
            self.recv.terminate()
        except Exception, e:
            print "Exception: " + str(e)

    def shutdown(self):
        """Shutdown master container."""

        j_dict = dict()
        j_dict["action"] = Action.SHUTDOWN
        self.s.sendall(_json.dumps(j_dict) + '\n')

    def send(self, msg):
        """Sends a message to the recipient indicated in the message. The recipient may be an agent or a topic."""

        #TODO: Verify the logic (compare to send in SlaveContainer.java)
        if not msg.recipient:
            return False

        j_dict = dict()
        m_dict = dict()
        j_dict["action"] = Action.SEND
        j_dict["relay"] = True
        m_dict = self.to_json(msg) #TODO: Merge this and next line?
        j_dict["message"] = m_dict

        # add msgType field to json
        # TODO: Get module name programatically : __name__ (- the file name)
        m_dict["msgType"] = "org.arl."+msg.__module__+"."+msg.__class__.__name__

        # check for GenericMessage class and add "map" separately
        if msg.__class__.__name__ == GenericMessage().__class__.__name__:
            j_dict["map"] = msg.map

        # print "Sending: " + _json.dumps(j_dict) + "\n"

        # send the message
        self.s.sendall(_json.dumps(j_dict) + '\n')

        return True

    # TODO: Implement timeout (using condition variables)
    def receive(self, filter=None, tout=0.1):
        """Returns a message received by the gateway and matching the given filter."""
        try:
            if tout:
                _time.sleep(tout)
            else:
                _time.sleep(0.1)

            if filter == None:
                rmsg = self.q.pop()
                
            elif isinstance(filter, Message):
                # print "inReplyto: " + filter.msgID
                if filter.msgID:
                    for i in self.q:
                        if filter.msgID == i["inReplyTo"]:
                            try:
                                rmsg = self.q.pop(self.q.index(i))
                            except Exception, e:
                                print "Error: Getting item from list - " +  str(e)
                        else:
                            return None
                else:
                    return None

            elif type(Gateway) == type(filter):
                # print "msgType: " + str(filter)
                for i in self.q:
                    #TODO: Use proper class name, not hardcoded class name
                    # if i["msgType"] == str(filter):
                    if i["msgType"] == "org.arl.fjage.Message":
                        try:
                            rmsg = self.q.pop(self.q.index(i))
                        except Exception, e:
                            print "Error: Getting item from list - " +  str(e)
                    else:
                        return None
            else:
                return None

            if rmsg == None:
                return None
                
        except Exception, e:
            print "Error: Queue empty/timeout - " +  str(e)
            return None

        # print "Received message: " + str(rmsg) + "\n"

        try:
            rsp = self.from_json(rmsg)

            found_map = False

            # add map if it is a Generic message
            if rsp.__class__.__name__ == GenericMessage().__class__.__name__:
                for key in rmsg:
                    if key == "map":
                        map = _json.loads(rmsg)["map"]
                        rsp.putAll(map)
                        found_map = True

                if not found_map:
                    print "No map field found in Generic Message"

        except Exception, e:
            print "Exception: Class loading failed - " + str(e)
            return None

        return rsp

    def request(self, msg, tout):
        """Return received response message, null if none available."""
        self.send(msg)
        return self.receive(msg, tout)

    def topic(self, topic):
        """Returns an object representing the named topic."""
        if isinstance(topic, str):
            return AgentID(topic, True)
            
        elif isinstance(topic, AgentID):
            if topic.is_topic:
                return topic
            return AgentID(topic.name+"__ntf", True)

        else:
            return AgentID(topic.__class__.__name__+"."+str(topic), True)

    def subscribe(self, topic):
        """Subscribes the gateway to receive all messages sent to the given topic."""
        if isinstance(topic, AgentID):
            if topic.is_topic == False:
                new_topic = AgentID(topic.name+"__ntf", True)
            else:
                new_topic = topic

            if len(self.subscribers) == 0:
                self.subscribers.append(new_topic.name)
            else:
                # check whether this topic is already subscribed to
                for tp in self.subscribers:
                    if new_topic.name == tp:
                        print "Error: Already subscribed to topic"
                        return
                self.subscribers.append(new_topic.name)

    def unsubscribe(self, topic):
        """Unsubscribes the gateway from a given topic."""
        if isinstance(topic, AgentID):
            if topic.is_topic == False:
                new_topic = AgentID(topic.name+"__ntf", True)

            if len(self.subscribers) == 0:
                return False

            try:
                self.subscribers.remove(new_topic.name)
            except:
                print "Exception: No such topic subscribed: " + new_topic.name

            return True


    def agentForService(self, service):
        """ Finds an agent that provides a named service. If multiple agents are registered
            to provide a given service, any of the agents' id may be returned.
        """
        j_dict = dict()
        j_dict["action"] = Action.AGENT_FOR_SERVICE
        j_dict["id"] = str(_uuid.uuid4())
        if isinstance(service, str):
            j_dict["service"] = service
        else:
            j_dict["service"] = service.__class__.__name__+"."+str(service)
        self.s.sendall(_json.dumps(j_dict) + '\n')

        #TODO: Get the response from queue and return it


    def agentsForService(self, service):
        """Finds all agents that provides a named service."""
        j_dict = dict()
        j_dict["action"] = Action.AGENTS_FOR_SERVICE
        j_dict["id"] = str(_uuid.uuid4())
        if isinstance(service, str):
            j_dict["service"] = service
        else:
            j_dict["service"] = service.__class__.__name__+"."+str(service)
        self.s.sendall(_json.dumps(j_dict) + '\n')

        #TODO: Get the response from queue and return it

    def to_json(self, inst):
        """Convert the object attributes to a dict."""
        # copying object's attributes from __dict__ to convert to json
        dt = inst.__dict__.copy()

        # removing empty attributes
        for key in list(dt):
            if dt[key] == None:
                dt.pop(key)
            # remove map if its a GenericMessage class (to be added later)
            if key == 'map':
                dt.pop(key)
        return dt
        
    def from_json(self, dt):
        """If possible, do class loading, else return the dict."""
        # print dt
        if 'msgType' in dt:

            # for testing various incoming message types
            # dt['msgType'] = 'org.arl.fjage.shell.ShellExecReq'
            dt['msgType'] = 'org.arl.fjage.messages.GenericMessage'
            # print dt['msgType']

            #TODO: Do this programmatically
            # parse class name
            class_name = dt['msgType'].split(".")[-1]
            # print class_name

            # parse module name
            module_name = dt['msgType'].split(".")  # split the full name
            module_name.remove(module_name[-1])     # remove class name
            #TODO: remove org and arl in future
            module_name.remove('org')               # remove org
            module_name.remove('arl')               # remove arl
            module_name = ".".join(module_name)     # join whats left
            # print module_name

            try:
                module = __import__(module_name)
            except Exception, e:
                print "Exception in from_json, module: " + str(e)
                return dt
            # print 'MODULE: ' + str(module)
            try:
                class_ = getattr(module, class_name)
            except Exception, e:
                print "Exception in from_json, class: " + str(e)
                return dt
            # print 'CLASS :' + str(class_)
            args = dict((key.encode('ascii'), value.encode('ascii')) for key, value in dt.items())
            # print 'INSTANCE ARGS:', args
            inst = class_(**args)
        else:
            inst = dt
        return inst
