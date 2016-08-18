"""Messages: Message class and all subclasses

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

TODO:
    * Resolve the various TODOs in the code

"""

import uuid as _uuid

class AgentID:
    """An identifier for an agent or a topic."""
    def __init__(self, name, is_topic = False):
            self.name = name
            if is_topic:
                self.is_topic = True
            else:
                self.is_topic = False

class Performative:
    """An action represented by a message."""
    REQUEST             = "REQUEST"             # Request an action to be performed.
    AGREE               = "AGREE"               # Agree to performing the requested action.
    REFUSE              = "REFUSE"              # Refuse to perform the requested action.
    FAILURE             = "FAILURE"             # Notification of failure to perform a requested or agreed action.
    INFORM              = "INFORM"              # Notification of an event.
    CONFIRM             = "CONFIRM"             # Confirm that the answer to a query is true.
    DISCONFIRM          = "DISCONFIRM"          # Confirm that the answer to a query is false.
    QUERY_IF            = "QUERY_IF"            # Query if some statement is true or false.
    NOT_UNDERSTOOD      = "NOT_UNDERSTOOD"      # Notification that a message was not understood.
    CFP                 = "CFP"                 # Call for proposal.
    PROPOSE             = "PROPOSE"             # Response for CFP.
    CANCEL              = "CANCEL"              # Cancel pending request.

class Message(object):
    """Base class for messages transmitted by one agent to another."""
    def __init__(self, **kwargs):

        self.msgID = str(_uuid.uuid4())
        self.perf = None
        self.recipient = None
        self.sender = None
        self.inReplyTo = None
        self.__dict__.update(kwargs)

    def __str__(self):
        p = self.perf if self.perf else "MESSAGE";
        if self.__class__ == Message:
            return p;
        return p + ": " + str(self.__class__.__name__);


class GenericMessage(Message):
    """A message class that can convey generic messages represented by key-value pairs."""
    def __init__(self, **kwargs):
        #TODO: Verify whether this is the way to call parent's constructor
        Message.__init__(self)
        self.map = dict()
        self.__dict__.update(kwargs)

from remote import *
from shell import *
