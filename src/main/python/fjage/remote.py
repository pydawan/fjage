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
import time as _time
import socket as _socket
import multiprocessing as _mp
from messages import Action as _action
from messages import Message as _msg
from messages import GenericMessage as _gmsg

class Gateway:
    """Gateway to communicate with agents from python.

    NOTE: Create only one object of Gateway class at a time. Else, there will be multiple receive threads

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

    def __init__(self, ip, port):

        try:
            # NOTE: q is implemented using a list since we need to iterate over items. Following java implementation.
            self.q = _mp.Manager().list()

            # create socket
            self.s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)

            # connect to fjage master container
            self.s.connect((ip, port))

            # start the receive process as another process
            self.recv = _mp.Process(target=self.__recv_proc, args=(self.q,))
            self.recv.start()

        except Exception, e:
            print "Exception: " + str(e)
            _sys.exit(0)

    def parse_incoming(self, rmsg, q):
        """Parse incoming messages"""

        #TODO: Complete this method for other actions
        r_dict = _json.loads(rmsg)

        for key, value in r_dict.items():
            if key == 'action':
                if value == _action().AGENTS:
                    print "ACTION: " + _action().AGENTS

                elif value == _action().CONTAINS_AGENT:
                    print "ACTION: " + _action().CONTAINS_AGENT

                elif value == _action().SERVICES:
                    print "ACTION: " + _action().SERVICES

                elif value == _action().AGENT_FOR_SERVICE:
                    print "ACTION: " + _action().AGENT_FOR_SERVICE

                elif value == _action().AGENTS_FOR_SERVICE:
                    print "ACTION: " + _action().AGENTS_FOR_SERVICE

                elif value == _action().SEND:
                    # add message to queue
                    print "ACTION: " + _action().SEND
                    try:
                        q.append(r_dict["message"])
                    except Exception, e:
                        print "Exception: Error adding to queue - " + str(e)

                elif value == _action().SHUTDOWN:
                    print "ACTION: " + _action().SHUTDOWN
                    return None

                else:
                    print "Invalid message, discarding"

        return True

    def __recv_proc(self, q):
        """Receive process."""

        self.s.setblocking(0)
        parenthesis_count = 0;
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
    def receive_with_filter_tout (self, filter, tout):
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

            # match the msgID to incoming message's inReplyTo field
            else:
                # parse list and look for matching msgID
                if filter.msgID:

                    # print "msgID: " + str(filter.msgID)
                    for i in self.q:
                        if filter.msgID == i["inReplyTo"]:
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
                        rv.putAll(map);
                        found_map = True

                if not found_map:
                    print "No map field found in Generic Message"

        except Exception, e:
            print "Exception: Class loading failed - " + str(e)
            return None # TODO: Verify whether the return value is correct

        return rv

    def receive(self):
        """Return received response message, None if none available."""
        return self.receive_with_filter_tout(None, 0.1)

    def receive_with_tout(self, tout):
        """Return received response message, None if none available."""
        return self.receive_with_filter_tout (None, tout)

    #TODO: Verify whether we need to implement methods which take in Class<?> as filter
    # def receive_with_class(self, kls):
    #     """Returns a message of a given class received by the gateway. This method is non-blocking."""
    #     return self.receive_with_filter_tout (kls, 0.1)

    # def receive_with_class_tout(self, kls, tout):
    #     """Returns a message of a given class received by the gateway. This method blocks until timeout if no message available."""
    #     return self.receive_with_filter_tout (kls, tout)

    def receive_with_message(self, msg):
        """Returns a response message received by the gateway. This method is non-blocking."""
        return self.receive_with_filter_tout(msg, 0.1)

    def receive_with_message_tout(self, msg, tout):
        """Returns a response message received by the gateway. This method blocks until timeout."""
        return self.receive_with_filter_tout(msg, tout)

    # return received response message, null if none available.
    def request(self, msg, tout):
        # send the message
        self.send(msg)

        # wait for the response
        return self.receive_with_filter_tout(msg, tout)

    # # TODO: Implement this
    # def topic_string(self, topic):
    #   pass

    # # TODO: Implement this
    # def topic_enum(self, topic):
    #   pass

    # # TODO: Implement this
    # def topic_agentID(self, topic):
    #   pass

    # # TODO: Implement this
    # def subscribe(self, topic):
    #   pass

    # # TODO: Implement this
    # def unsubscribe(self, topic):
    #   pass

    # # TODO: Implement this
    # def agentForService_string(self, service):
    #   pass

    # # TODO: Implement this
    # def agentForService_enum(self, service):
    #   pass

    # # TODO: Implement this
    # def agentsForService_string(self, service):
    #   pass

    # # TODO: Implement this
    # def agentsForService_enum(self, service):
    #   pass

########### Private stuff
    def is_topic(self, msg):
        if msg.recipient[0] == "#":
            return True
        return False

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
        

    #TODO: Figure out why class loading for ShellExecReq doesn't work
    def from_json(self, dt):
        """If possible, do class loading, else return the dict."""
        # print dt
        if 'msgType' in dt:

            #TODO: Do this programmatically
            # parse class name
            class_name = dt['msgType'].split(".")[-1]

            # parse module name
            module_name = dt['msgType'].split(".")  # split the full name
            module_name.remove(module_name[-1])     # remove class name
            #TODO: remove org and arl in future
            module_name.remove('org')               # remove org
            module_name.remove('arl')               # remove arl
            module_name = ".".join(module_name)     # join whats left

            try:
                module = __import__(module_name)
            except Exception, e:
                print "Exception in from_json, module: " + str(e)
                return
            # print 'MODULE: ' + str(module)
            try:
                class_ = getattr(module, class_name)
            except Exception, e:
                print "Exception in from_json, class: " + str(e)
            # print 'CLASS :' + str(class_)
            args = dict((key.encode('ascii'), value.encode('ascii')) for key, value in dt.items())
            # print 'INSTANCE ARGS:', args
            inst = class_(**args)
        else:
            inst = dt
        return inst
