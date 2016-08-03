"""Messages: Message class and all subclasses

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

TODO:
    * Implement the classes

"""

import json as _json
import uuid as _uuid

class JsonMessage:
    """Class representing a JSON request/response message."""

    # Supported JSON keys
    json_msg_keys = ["id", "action", "inResponseTo", "agentID", "agentIDs", "service", "services", "answer", "message", "relay"]

    def __init__(self):
        # json message dictionary
        self.j_dict = dict()

        # message dictionary
        self.m_dict = dict()
        
    def to_jdict(self, msg):
        """ Convert message dictionary to json message dictionary before sending out."""

        #TODO: Implement the missing logic

        self.j_dict["action"] = "send"
        self.j_dict["relay"] = True
        self.j_dict["message"] = msg
        
        return self.j_dict

    def to_mdict(self, msg):
        """ Convert the received json message dictionary from gateway to message dictionary."""

        #TODO: Implement the missing logic to convert JsonMessage to Message by removing the json specific fields
        #TODO: Investigate why printing json.loads prints a 'u' before each field
        try:
            self.m_dict = _json.loads(msg)["message"]
            return self.m_dict
        except Exception, e:
            print "Exception: Key not found - " + str(e)

class Message:
    """Base class for messages transmitted by one agent to another.

    This class provides the basic attributes of messages and is typically
    extended by application-specific message classes. To ensure that messages
    can be sent between agents running on remote containers, all attributes
    of a message must be serializable.
    """

    msg_keys = ["msgID", "msgType", "perf", "recipient", "sender", "inReplyTo"]

    def __init__(self):
        self.msgID = str(_uuid.uuid4())
        self.perf = None
        self.recipient = None
        self.sender = None
        self.inReplyTo = None

        self.m_dict = dict()
        self.m_dict["msgID"] = self.msgID

    def setPerformative(self, perf):
        """Sets the performative for this message."""
        self.perf = perf

    def getPerformative(self):
        """Gets the performative for this message."""
        return self.perf

    def setRecipient(self, aid):
        """Sets the recipient of this message."""
        self.recipient = aid

    def getRecipient(self):
        """Gets the recipient of this message."""
        return self.recipient

    def setSender(self, aid):
        """Sets the sender of this message."""
        self.sender = aid

    def getSender(self):
        """Gets the sender of this message."""
        return self.sender

    def setMessageID(self, msgID):
        """Sets the unique identifier for this message."""
        self.msgID = msgID

    def getMessageID(self):
        """Gets the unique identifier for this message."""
        return self.msgID

    def setInReplyTo(self, msgID):
        """Sets the message id of the associated request message."""
        self.inReplyTo = msgID

    def getInReplyTo(self):
        """Gets the message id of the associated request message."""
        return self.inReplyTo

    def to_dict(self):
        """Converts Message object to a message dictionary to be converted to json later."""

        if self.perf:
            self.m_dict["perf"] = self.perf

        if self.recipient:
            self.m_dict["recipient"] = self.recipient

        if self.sender:
            self.m_dict["sender"] = self.sender

        self.m_dict["msgID"] = self.msgID

        if self.inReplyTo:
            self.m_dict["inReplyTo"] = self.inReplyTo

        # TODO: Figure out how to get module name (fjage) dynamically
        self.m_dict["msgType"] = "org.arl."+"fjage"+"."+self.__class__.__name__

        return self.m_dict

    def to_class(self, m_dict):

        is_msgID = False

        for key in m_dict:

            if key == "perf":
                self.setPerformative(m_dict["perf"])

            if key == "recipient":
                self.setRecipient(m_dict["recipient"])

            if key == "sender":
                self.setSender(m_dict["sender"])

            if key == "msgID":
                self.setMessageID(m_dict["msgID"])
                is_msgID = True

            if key == "inReplyTo":
                self.setInReplyTo(m_dict["inReplyTo"])

        if is_msgID != True:
            raise Exception("Missing msgID")

class GenericMessage:
    """A message class that can convey generic messages represented by key-value pairs."""
