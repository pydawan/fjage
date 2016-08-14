"""Remote: Support for gateway interface for remote containers using JSON over TCP/IP.

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

TODO:
    * Implement the following methods:
        * topic
        * subscribe
        * unsubscribe
        * agent_for_service
        * agents_for_service

"""
import os as _os
import sys as _sys
import json as _json
import uuid as _uuid
import time as _time
import socket as _socket
import multiprocessing as _mp
from messages import Action as _action
from messages import GenericMessage as _gmsg

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

    Changes from Java implementation
        1. In Java implementation, when a message is received, it is automatically class loaded since
        fjage has  knowledge of the UnetStack extended classes. In python, we do this with kwargs. But
        this may not be extensible for external apps which uses custom messages. So, if classloading
        fails in python, we simply return a "Message" dictionary.
        2. Since Python handles message dict rather than objects, MessageFilter Class<?> does not make
        sense and the methods receive_with_class_tout() and receive_with_class() is not implemented.
    """

    def __init__(self, ip, port, name = None):
        """NOTE: If name is assigned during __init__, the developer must make sure it is not a duplicate."""

        try:
            if name == None:
                self.name = "PythonGW-"+str(_uuid.uuid4())
            else:
                try:
                    self.name = name
                except Exception, e:
                    print "Exception: Cannot assign name to gateway: " + str(e)
                    _sys.exit(0)

            # NOTE: q is implemented using a list since we need to iterate over items. Following java implementation.
            self.q = _mp.Manager().list()
            self.subscribers = _mp.Manager().list()

            # create socket
            self.s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)

            # connect to fjage master container
            self.s.connect((ip, port))

            # start the receive process as another process
            self.recv = _mp.Process(target=self.__recv_proc, args=(self.q, self.subscribers, ))
            self.recv.start()

        except Exception, e:
            print "Exception: " + str(e)
            _sys.exit(0)

    def parse_incoming(self, rmsg, q):
        """Parse incoming messages and respond to them"""

        #TODO: Verify the logic of all responses
        r_dict = _json.loads(rmsg)

        for key, value in r_dict.items():
            if key == 'action':

                if value == _action().AGENTS:
                    print "ACTION: " + _action().AGENTS
                    # respond with self.name
                    rsp = dict()
                    rsp["inResponseTo"] = r_dict["action"]
                    rsp["id"] = r_dict["id"]
                    #TODO: Confirm this field is a list
                    l = list()
                    l.append(self.name)
                    rsp["agentIDs"] = l

                    # send the message
                    self.s.sendall(_json.dumps(rsp) + '\n')

                elif value == _action().CONTAINS_AGENT:
                    print "ACTION: " + _action().CONTAINS_AGENT

                    rsp = dict()
                    rsp["inResponseTo"] = r_dict["action"]
                    rsp["id"] = r_dict["id"]

                    # check against gateway's agentID/name
                    answer = False
                    if r_dict["agentID"]:
                        if r_dict["agentID"] == self.name:
                            answer = True
                    rsp["answer"] = answer

                    # send the message
                    self.s.sendall(_json.dumps(rsp) + '\n')

                elif value == _action().SERVICES:
                    print "ACTION: " + _action().SERVICES

                    rsp = dict()
                    rsp["inResponseTo"] = r_dict["action"]
                    rsp["id"] = r_dict["id"]
                    # no services offered by gateway
                    rsp["services"] = []

                    # send the message
                    self.s.sendall(_json.dumps(rsp) + '\n')

                elif value == _action().AGENT_FOR_SERVICE:
                    print "ACTION: " + _action().AGENT_FOR_SERVICE

                    rsp = dict()
                    rsp["inResponseTo"] = r_dict["action"]
                    rsp["id"] = r_dict["id"]
                    # no gateway agent will offer a service
                    rsp["agentID"] = []

                    # send the message
                    self.s.sendall(_json.dumps(rsp) + '\n')

                elif value == _action().AGENTS_FOR_SERVICE:
                    print "ACTION: " + _action().AGENTS_FOR_SERVICE

                    rsp = dict()
                    rsp["inResponseTo"] = r_dict["action"]
                    rsp["id"] = r_dict["id"]
                    # no gateway agent will offer a service
                    rsp["agentIDs"] = []

                    # send the message
                    self.s.sendall(_json.dumps(rsp) + '\n')

                elif value == _action().SEND:
                    #TODO: add message to queue only if:
                        # 1. if the aid is same as gateway's id/name or
                        # 2. the message is for a topic in the subscribers list
                    print "ACTION: " + _action().SEND
                    try:
                        #TODO: There is a broken pipe error when the server tries to send a message. Investigate
                        q.append(r_dict["message"])
                    except Exception, e:
                        print "Exception: Error adding to queue - " + str(e)

                elif value == _action().SHUTDOWN:
                    print "ACTION: " + _action().SHUTDOWN
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

                # count the number of '{' and use that to determine the end of json message
                if c == '{':
                    parenthesis_count += 1
                if c == '}':
                    parenthesis_count -= 1
                    if parenthesis_count == 0:
                        # print "Received: " + rmsg

                        # parse incoming messages
                        msg = self.parse_incoming(rmsg, q)

                        # # TODO: Verify shutdown design
                        if msg == None:
                            print "Shutting down"
                            break

                        rmsg = ""
            except:
                pass

        #TODO: Do we need a _sys.exit(0) here?

    def __del__(self):
        try:
            self.s.close
            #TODO: Do we need this here?
            # self.recv.terminate()
        except Exception, e:
            print "Exception: " + str(e)

    def shutdown(self):
        """Shutdown master container.
        The gateway functionality shall no longer be accessed after this method is called.

        How shutdown works:
        When an applications calls shutdown method, it sends a shutdown json message
        to the master container. The master container responds with a shutdown message.
        While processing an incoming shutdown message, the receive process (child) breaks
        from its while loop and the program exits.

        """

        j_dict = dict()
        j_dict["action"] = _action().SHUTDOWN
        self.s.sendall(_json.dumps(j_dict) + '\n')

        # now wait for the child to quit the receive while loop
        #TODO: Verify whether the parent process need to wait for the child to join or 
        # simply break the child's while loop?
        # self.recv.join()
        # self.recv.terminate()

    def send(self, msg):
        """Send the json message.
        Sends a message to the recipient indicated in the message. The recipient
        may be an agent or a topic.

        """

        #TODO: Verify the logic (compare to send in SlaveContainer.java)
        if not msg.recipient:
            return False

        # create json message dict
        j_dict = dict()
        m_dict = dict()

        j_dict["action"] = _action().SEND
        j_dict["relay"] = True

        # convert object attributes to dict and add to json message
        m_dict = self.to_json(msg)
        j_dict["message"] = m_dict

        # add msgType field to json
        # TODO: Get module name programatically : __name__ (- the file name)
        m_dict["msgType"] = "org.arl."+msg.__module__+"."+msg.__class__.__name__

        # check for GenericMessage class and add "map" separately
        if msg.__class__.__name__ == _gmsg().__class__.__name__:
            j_dict["map"] = msg.map

        # print "Sending: " + _json.dumps(j_dict) + "\n"

        # send the message
        self.s.sendall(_json.dumps(j_dict) + '\n')

        return True

    # TODO: In general, timeout is not implemented for any of the following functions
    def receive_with_filter_tout (self, filter, tout, filter_type):
        """Returns a message received by the gateway and matching the given filter."""
        try:
            # rmsg = self.q.get(timeout=tout)
            #TODO: Implement wait with timeout using signals. NOTE: If we use signals, this will be a UNIX only implementation.
            if tout:
                _time.sleep(tout)
            else:
                _time.sleep(0.1)

            # if no filter, simply pop an element from the head
            if filter == None:
                rmsg = self.q.pop()

            #TODO: Verify whether usage of filter_type OK or should we use isinstanceof()
            # match the msgID to incoming message's inReplyTo field
            elif filter_type == "msg":
                # parse list and look for matching msgID
                if filter.msgID:

                    # print "msgID: " + str(filter.msgID)
                    for i in self.q:
                        if filter.msgID == i["inReplyTo"]:
                            try:
                                rmsg = self.q.pop(self.q.index(i))
                            except Exception, e:
                                print "Error: Getting item from list - " +  str(e)

            # match the msgType to incoming message's msgType field
            elif filter_type == "cls":
                # parse list and look for matching msgType
                print "msgType: " + str(filter)
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
                
        except Exception, e:
            print "Error: Queue empty/timeout - " +  str(e)
            return None

        # print "Received message: " + str(rmsg) + "\n"

        try:
            # decode rmsg to object
            rv = self.from_json(rmsg)

            found_map = False

            # add map if it is a Generic message
            if rv.__class__.__name__ == _gmsg().__class__.__name__:
                for key in rmsg:
                    if key == "map":
                        map = _json.loads(rmsg)["map"]
                        rv.putAll(map)
                        found_map = True

                if not found_map:
                    print "No map field found in Generic Message"

        except Exception, e:
            print "Exception: Class loading failed - " + str(e)
            return None # TODO: Verify whether the return value is correct

        return rv

    def receive(self):
        """Return received response message, None if none available."""
        return self.receive_with_filter_tout(None, 0.1, None)

    def receive_with_tout(self, tout):
        """Return received response message, None if none available."""
        return self.receive_with_filter_tout (None, tout, None)

    def receive_with_class(self, kls):
        """Returns a message of a given class received by the gateway. This method is non-blocking."""
        return self.receive_with_filter_tout (kls, 0.1, "cls")

    def receive_with_class_tout(self, kls, tout):
        """Returns a message of a given class received by the gateway. This method blocks until timeout if no message available."""
        return self.receive_with_filter_tout (kls, tout, "cls")

    def receive_with_message(self, msg):
        """Returns a response message received by the gateway. This method is non-blocking."""
        return self.receive_with_filter_tout(msg, 0.1, "msg")

    def receive_with_message_tout(self, msg, tout):
        """Returns a response message received by the gateway. This method blocks until timeout."""
        return self.receive_with_filter_tout(msg, tout, "msg")

    def request(self, msg, tout):
        """Return received response message, null if none available."""
        self.send(msg)
        return self.receive_with_filter_tout(msg, tout, "msg")

    def topic_string(self, topic):
        """Returns an object representing the named topic."""
        if isinstance(topic, str):
            return AgentID(topic, True)
        return None

    #TODO: Verify enums in python: If we use a custom package, how will it affect other systems?
    # def topic_enum(self, topic):
    #     """Returns an object representing the named topic."""
    #     if isinstance(topic, Enum):
    #         return AgentID(topic.__class__.__name__+"."+topic.name, True)
    #     return None

    def topic_agentID(self, topic):
        if isinstance(topic, AgentID):
            if topic.is_topic:
                return topic
        return AgentID(topic.name+"__ntf", True)

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


    def agentForService_string(self, service):
        """ Finds an agent that provides a named service. If multiple agents are registered
            to provide a given service, any of the agents' id may be returned.
        """

        if isinstance(service, str):

            # create json message dict
            j_dict = dict()
            j_dict["action"] = _action().AGENT_FOR_SERVICE
            j_dict["service"] = service
            j_dict["id"] = str(_uuid.uuid4())

            # send the message
            self.s.sendall(_json.dumps(j_dict) + '\n')

        #TODO: Get the response from queue and return it

    #TODO: Verify enums in python
    # def agentForService_enum(self, service):
    #     """ Finds an agent that provides a named service. If multiple agents are registered
    #         to provide a given service, any of the agents' id may be returned.
    #     """

    #     if isinstance(service, Enum):

    #         # create json message dict
    #         j_dict = dict()
    #         j_dict["action"] = _action().AGENT_FOR_SERVICE
    #         j_dict["service"] = service.__class__.__name__+"."+str(service)
    #         j_dict["id"] = str(_uuid.uuid4())

    #         # send the message
    #         self.s.sendall(_json.dumps(j_dict) + '\n')

    #     #TODO: Get the response from queue and return it

    def agentsForService_string(self, service):
        """Finds all agents that provides a named service."""

        if isinstance(service, str):

            # create json message dict
            j_dict = dict()
            j_dict["action"] = _action().AGENTS_FOR_SERVICE
            j_dict["service"] = service
            j_dict["id"] = str(_uuid.uuid4())

            # send the message
            self.s.sendall(_json.dumps(j_dict) + '\n')

        #TODO: Get the response from queue and return it

    #TODO: Verify enums in python
    # def agentsForService_enum(self, service):
    #     """Finds all agents that provides a named service."""

    #     if isinstance(service, Enum):

    #         # create json message dict
    #         j_dict = dict()
    #         j_dict["action"] = _action().AGENTS_FOR_SERVICE
    #         j_dict["service"] = service.__class__.__name__+"."+str(service)
    #         j_dict["id"] = str(_uuid.uuid4())

    #         # send the message
    #         self.s.sendall(_json.dumps(j_dict) + '\n')

    #     #TODO: Get the response from queue and return it

########### Private stuff
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
