"""Messages: Message class and all subclasses

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

TODO:
    * Implement the classes

"""

import json as _json

class JsonMessage:
    """Class representing a JSON request/response message."""

    # Supported JSON keys
    keys = ["id", "action", "inResponseTo", "agentID", "agentIDs", "service", "services", "answer", "message", "relay"]

    # json message
    json_msg = dict()

    # constructor
    # def __init__(self):
        
    def to_jdict(self, msg):
        """ Convert message dictionary to json message dictionary."""

        #TODO: Implement the missing logic

        self.json_msg["action"] = "send"
        self.json_msg["relay"] = "true"
        self.json_msg["message"] = msg
        
        return self.json_msg

    def to_mdict(self, msg):
        """ Convert json message dictionary to message dictionary."""

        #TODO: Implement the missing logic to convert JsonMessage to Message by removing the json specific fields
        try:
            self.json_msg = _json.loads(msg)["message"]
            return self.json_msg
        except Exception, e:
            print "Exception: Key not found - " + str(e)

class Message:
    """Base class for messages transmitted by one agent to another.

    This class provides the basic attributes of messages and is typically
    extended by application-specific message classes. To ensure that messages
    can be sent between agents running on remote containers, all attributes
    of a message must be serializable.
    """

class GenericMessage:
    """A message class that can convey generic messages represented by key-value pairs."""
