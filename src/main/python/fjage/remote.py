"""Remote: Gateway interface for remote containers.

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
import sys as _sys
import json as _json
import socket as _socket
import multiprocessing as _mp
from messages import Action as _action
from messages import Message as _msg
from messages import GenericMessage as _gmsg

class Gateway:
    """Gateway to communicate with agents from python."""

    # Supported JSON keys
    json_msg_keys = ["id", "action", "inResponseTo", "agentID", "agentIDs", "service", "services", "answer", "message", "relay"]

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
            pass

    def __recv_proc(self, q):
        """Receive process."""

        self.s.setblocking(0)
        parenthesis_count = 0;
        rmsg = ""

        while 1:
            try:
                c = self.s.recv(1)
                rmsg = rmsg + c

                # count the number of '{' and use that to determine the end of json message
                if c == '{':
                    parenthesis_count += 1
                if c == '}':
                    parenthesis_count -= 1
                    if parenthesis_count == 0:
                        # print rmsg
                        # put incoming message to queue
                        q.put(rmsg)
                        rmsg = ""
            except:
                pass

    def __del__(self):
        try:
            self.s.close
            self.recv.terminate()
        except Exception, e:
            print "Exception: " + str(e)
            pass

    def shutdown(self):
        """Shutdown master container & closes the gateway.
        The gateway functionality shall no longer be accessed after this method is called.

        """

        j_dict = dict()
        j_dict["action"] = _action().SHUTDOWN
        self.s.sendall(_json.dumps(j_dict) + '\n')
        self.recv.terminate()

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

        m_dict = msg.to_json()

        class_name = msg.__class__.__name__

        # check for GenericMessage class and add "map"
        g = _gmsg()
        if class_name == g.__class__.__name__:
            j_dict["map"] = g.gmap

        # add msgType field to json
        # TODO: Get module name programatically : __name__ (- the file name)
        m_dict["msgType"] = "org.arl."+"fjage"+"."+class_name
        j_dict["message"] = m_dict

        # print _json.dumps(json_to_send)
        print _json.dumps(j_dict)

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
            print "Queue empty/timeout"
            return None

        print rmsg

        try:
            m_dict = dict()
            m_dict = _json.loads(rmsg)["message"]
        except Exception, e:
            print "Exception: Key not found - " + str(e)
            # TODO: Check valid return values instead of returning False
            return False

        #TODO: Implement class loading and do this based on 'msgType' field
        rv = _msg()

        #TODO: Investigate why printing json.loads prints a 'u' before each field

        # load the class with message fields
        rv.from_json(m_dict)

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
