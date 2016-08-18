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
import threading as _td
from fjage import AgentID
from fjage import Message
from fjage import GenericMessage

currentTimeMillis = lambda: int(round(_time.time() * 1000))

class Action:
    AGENTS              = "agents"
    CONTAINS_AGENT      = "containsAgent"
    SERVICES            = "services"
    AGENT_FOR_SERVICE   = "agentForService"
    AGENTS_FOR_SERVICE  = "agentsForService"
    SEND                = "send"
    SHUTDOWN            = "shutdown"

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

    NON_BLOCKING = 0;
    BLOCKING = -1

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

            self.q = list()
            self.subscribers = list()
            self.s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
            self.s.connect((ip, port))
            self.recv = _td.Thread(target=self.__recv_proc, args=(self.q, self.subscribers, ))
            self.cv = _td.Condition();
            self.recv.daemon = True
            self.recv.start()
            #TODO: This has to be a blocking call with timeout
            if self.is_duplicate():
                self.s.close
                _sys.exit(0)

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
                    rsp["agentIDs"]     = [self.name]
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
                    print "ACTION: " + Action.SEND

                    # add message to queue only if:
                    # 1. if the recipient is same as gateway's name or
                    # 2. the message is for a topic in the subscribers list
                    try:
                        # print "name: " + self.name
                        msg = req["message"]
                        if msg["recipient"] == self.name:
                            q.append(msg)
                            self.cv.acquire();
                            self.cv.notify();
                            self.cv.release();

                        if self.is_topic(msg["recipient"]):
                            if self.subscribers.count(msg["recipient"].replace("#","")):
                                q.append(msg)
                                self.cv.acquire();
                                self.cv.notify();
                                self.cv.release();

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

        parenthesis_count = 0
        rmsg = ""

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
        msg.sender = self.name
        m_dict = self.to_json(msg)
        m_dict["msgType"] = "org.arl."+msg.__module__+"."+msg.__class__.__name__
        j_dict["message"] = m_dict

        # check for GenericMessage class and add "map" separately
        if msg.__class__.__name__ == GenericMessage().__class__.__name__:
            j_dict["map"] = msg.map

        # print "Sending: " + _json.dumps(j_dict) + "\n"

        self.s.sendall(_json.dumps(j_dict) + '\n')

        return True

    def _retrieveFromQueue(self, filter):
        rmsg = None
        try:
            if filter == None and len(self.q):
                rmsg = self.q.pop()

            # If filter is a Message, look for a Message in the
            # receive Queue which was inReplyto that message.
            elif isinstance(filter, Message):
                # print "inReplyto: " + filter.msgID
                if filter.msgID:
                    for i in self.q:
                        if "inReplyTo" in i and filter.msgID == i["inReplyTo"]:
                            try:
                                rmsg = self.q.pop(self.q.index(i))
                            except Exception, e:
                                print "Error: Getting item from list - " +  str(e)

            # If filter is a class, look for a Message of that class.
            elif type(filter) == type(Message):
                # print "msgType: " + filter.__name__
                for i in self.q:
                    if i['msgType'].split(".")[-1] == filter.__name__:
                        try:
                            rmsg = self.q.pop(self.q.index(i))
                        except Exception, e:
                            print "Error: Getting item from list - " +  str(e)

            # If filter is a lambda, look for a Message that on which the
            # lambda returns True.
            elif isinstance(filter, type(lambda:0)):
                # print "msgType: " + str(filter).split(".")[-1]
                for i in self.q:
                    if filter(i):
                        try:
                            rmsg = self.q.pop(self.q.index(i))
                        except Exception, e:
                            print "Error: Getting item from list - " +  str(e)

        except Exception, e:
            print "Error: Queue empty/timeout - " +  str(e)

        return rmsg

    def receive(self, filter=None, timeout=0):
        """Returns a message received by the gateway and matching the given filter."""

        rmsg = self._retrieveFromQueue(filter)

        if (rmsg == None and timeout != self.NON_BLOCKING):
            deadline = currentTimeMillis() + timeout

            while (rmsg == None and (timeout == self.BLOCKING or currentTimeMillis() < deadline)):

                if timeout == self.BLOCKING:
                    self.cv.acquire();
                    self.cv.wait();
                    self.cv.release();
                elif timeout > 0:
                    self.cv.acquire();
                    t = deadline - currentTimeMillis();
                    self.cv.wait(t/1000);
                    self.cv.release();

                rmsg = self._retrieveFromQueue(filter)

        # print "Received message: " + str(rmsg) + "\n"
        if not rmsg
            return None

        try:
            rsp = self.from_json(rmsg)

            found_map = False

            # add map if it is a Generic message
            if rsp.__class__.__name__ == GenericMessage().__class__.__name__:
                if "map" in rmsg:
                    map = _json.loads(rmsg)["map"]
                    rsp.putAll(map)
                    found_map = True

                if not found_map:
                    print "No map field found in Generic Message"

        except Exception, e:
            print "Exception: Class loading failed - " + str(e)
            return None

        return rsp

    def request(self, msg, timeout=1000):
        """Return received response message, null if none available."""
        self.send(msg)
        return self.receive(msg, timeout)

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
                #TODO: use list function
                for tp in self.subscribers:
                    if new_topic.name == tp:
                        print "Error: Already subscribed to topic"
                        return
                self.subscribers.append(new_topic.name)
        else:
            print "Invalid AgentID"

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
        else:
            print "Invalid AgentID"


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

        _time.sleep(5)

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
        dt = inst.__dict__.copy()

        for key in list(dt):
            if dt[key] == None:
                dt.pop(key)
            # if the last charactor of an attribute is "_", remove it in json message. E.g. from_
            elif list(key)[-1] == '_':
                dt[key[:-1]] = dt.pop(key)

            # remove map if its a GenericMessage class (to be added later)
            if key == 'map':
                dt.pop(key)

            #TODO: Any attribute ending with "_", remove it
        return dt

    def from_json(self, dt):
        """If possible, do class loading, else return the dict."""

        # for testing various incoming message types
        # dt['msgType'] = 'org.arl.fjage.shell.ShellExecReq'
        # dt['msgType'] = 'org.arl.fjage.messages.GenericMessage'
        # print dt['msgType']

        if 'msgType' in dt:
            class_name = dt['msgType'].split(".")[-1]
            module_name = dt['msgType'].split(".")
            module_name.remove(module_name[-1])
            module_name.remove("org")
            module_name.remove("arl")
            module_name = ".".join(module_name)
            # print class_name
            # print module_name

            try:
                module = __import__(module_name)
            except Exception, e:
                print "Exception in from_json, module: " + str(e)
                return dt
            try:
                class_ = getattr(module, class_name)
            except Exception, e:
                print "Exception in from_json, class: " + str(e)
                return dt
            # args = dict((key.encode('ascii'), value.encode('ascii')) for key, value in dt.items())
            args = dict((key.encode('ascii'), value if (isinstance(value, int) or isinstance(value, float)) else value.encode('ascii')) for key, value in dt.items())
            inst = class_(**args)
        else:
            inst = dt
        return inst

    def is_duplicate(self):
        rsp = dict()
        rsp["action"]   = Action.CONTAINS_AGENT
        rsp["id"]       = str(_uuid.uuid4())
        rsp["agentID"]  = self.name
        self.s.sendall(_json.dumps(rsp) + '\n')

        #TODO: Get the response from queue and return "answer" field
        return False

    def is_topic(self, recipient):
        if recipient[0] == "#":
            return True
        return False
