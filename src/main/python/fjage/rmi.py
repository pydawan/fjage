"""RMI: RMI interface for remote containers.

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

class Gateway:
    """Gateway to communicate with agents from python."""

    # supported json keys
    keys = ["id", "action", "inResponseTo", "agentID", "agentIDs", "service", "services", "answer", "message", "relay"]

    # constructor
    def __init__(self, ip, port):
        # connect to fjage master container
        try:
            # json message
            self.json_msg = dict()

            # queue
            self.q = _mp.Queue()

            # create socket
            self.s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
            self.s.connect((ip, port))

            # start the receive process as another process
            self.recv = _mp.Process(target=self.recv_proc, args=(self.q,))
            self.recv.start()
        except Exception, e:
            print "Exception:" + str(e)
            _sys.exit(0)
            pass

    # receive process
    def recv_proc(self, q):
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

    # destructor
    def __del__(self):
        try:
            self.s.close
        except:
            pass

        try:
            self.recv.terminate()
        except:
            pass

    # create json message
    def create_msg(self, key, value):
        # sanity check
        if key not in self.keys:
            return
        # add to json message
        self.json_msg[key] = value

    def get_msg(self):
        return self.json_msg

##################

    def shutdown(self):
        """Shutdown master container & closes the gateway.
        The gateway functionality shall no longer be accessed after this method is called.

        """
        msg = {"action": "shutdown"}
        #TODO: Do this only if there is something to dump
        self.s.sendall(_json.dumps(msg) + '\n')
        self.recv.terminate()

    def send(self):
        """Send the json message.
        Sends a message to the recipient indicated in the message. The recipient
        may be an agent or a topic.

        """
        #msg = {"id": message.id, "action": message.action, "agentID": message.agentID}
        print _json.dumps(self.json_msg)
        self.s.sendall(_json.dumps(self.json_msg) + '\n')

    # # TODO: Implement this
    # def receive_with_filter_tout (self, filter, tout):
    #     pass

    # return received response message, null if none available.
    def receive(self):
        if self.q.empty():
            return "null"
        else:
            return self.q.get()

    # return received response message, null if none available.
    def receive_with_tout(self, tout):
        try:
            rmsg = self.q.get(timeout=tout)
        except:
            print "Queue timeout"
            return
        return rmsg

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
        print _json.dumps(self.json_msg)
        self.s.sendall(_json.dumps(msg) + '\n')
        try:
            rmsg = self.q.get(timeout=tout)
        except:
            print "Queue timeout"
            return
        return rmsg

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
