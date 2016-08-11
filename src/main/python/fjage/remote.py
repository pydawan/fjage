"""Remote: Support for gateway interface for remote containers using JSON over TCP/IP.

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

TODO:
    * Implement the following methods
    * rest of receive
    * topic
    * subscribe
    * unsubscribe
    * agent_for_service
    * agents_for_service

"""
import os as _os
import sys as _sys
import json as _json
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
    """

    def __init__(self, ip, port):

        try:
            # queue
            self.q = _mp.Queue()

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
                    q.put(r_dict["message"])

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
                        print "Received: " + rmsg

                        # parse incoming messages
                        msg = self.parse_incoming(rmsg, q)

                        # # TODO: Verify shutdown design
                        if msg == None:
                            print "Shutting down receive process"
                            break

                        # q.put(rmsg)
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

        print "Sending: " + _json.dumps(j_dict) + "\n"

        # send the message
        self.s.sendall(_json.dumps(j_dict) + '\n')

        return True

    # # TODO: Implement this
    # def receive_with_filter_tout (self, filter, tout):
    #     pass

    def receive(self):
        """Return received response message, None if none available."""
        return self.receive_with_tout(1)

    def receive_with_tout(self, tout):
        """Return received response message, None if none available."""
        try:
            rmsg = self.q.get(timeout=tout)
        except:
            print "Error: Queue empty/timeout"
            return None

        # print "Received message: " + str(rmsg) + "\n"

        try:
            #TODO: Verify whether we need to decode and encode to get Message json string?
            # rmsg1 = _json.dumps(_json.loads(rmsg)["message"])
            # rv = _json.loads(rmsg1, object_hook = self.from_json)
            rv = self.from_json(rmsg)

            # print rv.__module__ + "." + rv.__class__.__name__

            # add map to Generic message
            if rv.__class__.__name__ == _gmsg().__class__.__name__:
                map = _json.loads(rmsg)["map"]
                rv.putAll(map);

        except Exception, e:
            print "Exception: Class loading failed - " + str(e)
            return None # TODO: Verify whether the return value is correct

        return rv

    # # TODO: Implement this
    # def receive_with_class(self, class):
    #     pass

    # # TODO: Implement this
    # def receive_with_class_tout(self, class, tout):
    #     pass

    # # TODO: Implement this
    # def receive_with_message(self, message):
    #     pass

    # # TODO: Implement this
    # def receive_with_message_tout(self, message, tout):
    #     pass

    # return received response message, null if none available.
    def request(self, msg, tout):
        # send the message
        self.send(msg)

        # wait for the response
        return self.receive_with_tout(tout)

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
        
    def from_json(self, dt):
        """If possible, do class loading, else return the dict."""
        # print dt
        if 'msgType' in dt:

            #TODO: Do this programmatically
            class_name = 'Message'
            module_name = 'fjage.messages'
            module = __import__(module_name)
            # print 'MODULE: ' + str(module)
            class_ = getattr(module, class_name)
            # print 'CLASS :' + str(class_)
            args = dict((key.encode('ascii'), value.encode('ascii')) for key, value in dt.items())
            # print 'INSTANCE ARGS:', args
            inst = class_(**args)
        else:
            inst = dt
        return inst
