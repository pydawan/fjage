"""Messages: Message class and all subclasses

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

TODO:
    * Resolve the various TODOs in the code

"""

import json as _json
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

class Message:
    """Base class for messages transmitted by one agent to another.

    This class provides the basic attributes of messages and is typically
    extended by application-specific message classes. To ensure that messages
    can be sent between agents running on remote containers, all attributes
    of a message must be serializable.

    Attributes:
        msgID
        perf
        recipient
        sender
        inReplyTo
    """

    def __init__(self, **kwargs):

        self.msgID = str(_uuid.uuid4())
        self.perf = None
        self.recipient = None
        self.sender = None
        self.inReplyTo = None
        self.__dict__.update(kwargs)

class GenericMessage(Message):
    """A message class that can convey generic messages represented by key-value pairs.

    NOTE: Since GenericMessage class is a special case, we have implemented getters and setters
    similar to that in java implementation of fjage. So, use them and do not operate directly
    on the attributes for GenericMessage. It may be removed in future.

    Attributes:
        map: Is a dictionary
    """

    def __init__(self, **kwargs):
        #TODO: Verify whether this is the way to call parent's constructor
        Message.__init__(self)
        self.map = dict()
        self.__dict__.update(kwargs)

    def clear(self):
        """Clears the map (dict)."""
        self.map.clear()

    def containsKey(self, key):
        """Returns true if this map (dict) contains a mapping for the specified key."""
        return self.map.has_key(key)

    def containsValue(self, value):
        """Returns true if this map (dict) contains a mapping for the specified value."""
        return value in self.map.values()

    def entrySet(self):
        """Returns a Set view of the mappings contained in this map (dict)."""
        s = set()
        for v in self.map.values():
            s.add(v)
        return s

    def isEmpty(self):
        """Returns true if this map (dict) contains no key-value mappings."""
        return not self.map

    def keySet(self):
        s = set()
        for v in self.map:
            s.add(v)
        return s

    def put(self, key, value):
        """Associates the specified value with the specified key in this map (dict)."""

        if key == "performative":
            self.perf = value
            return value

        if key == "recipient":
            self.recipient = value
            return value

        if key == "sender":
            return self.sender

        if key == "messageID":
            return self.msgID

        if key == "inReplyTo":
            return self.inReplyTo

        self.map[key] = value
        return value

    def get(self, key, defVal = None):
        """Returns the value to which the specified key is mapped, or None if this map (dict) contains no mapping for the key."""

        if key == "performative":
            value = self.perf
        elif key == "recipient":
            value = self.recipient
        elif key == "sender":
            value = self.sender
        elif key == "messageID":
            value = self.msgID
        elif key == "inReplyTo":
            value = self.inReplyTo
        elif key in self.map:
            value = self.map[key]
        else:
            return defVal

        if isinstance(defVal, str):
            return str(value)
        elif isinstance(defVal, int):
            return int(value)
        elif isinstance(defVal, long):
            return long(value)
        elif isinstance(defVal, float):
            return float(value)
        else:
            return value

    def putAll(self, in_map):
        """Copies all of the mappings from the specified map to this map (dict)."""
        if type(in_map) != type(self.map):
            return

        # TODO: Verify whether we need to clear map before the copying operation
        self.clear()
        self.map = in_map.copy()

    def remove(self, key):
        """Removes the mapping for the specified key from this map (dict) if present."""
        return self.map.pop(key, None)

    def size(self):
        """Returns the number of key-value mappings in this map (dict)."""
        return len(self.map)

    def values(self):
        """Returns a list of all the values contained in this map (dict)."""
        return self.map.values()

################# Special getters for GenericMessage

    def get_as_string(self, key, defVal):
        """Gets the string value associated with the key, or defVal if not found."""
        if key in self.map:
            return str(self.map[key])
        else:
            return defVal

    def get_as_int(self, key, defVal):
        """Gets the integer value associated with the key, or defVal if not found.
        Raises ValueError, if the value is not numeric.
        """

        if key in self.map:
            return int(self.map[key])
        else:
            return defVal

    def get_as_long(self, key, defVal):
        """Gets the long value associated with the key, or defVal if not found.
        Raises ValueError, if the value is not numeric.
        """

        if key in self.map:
            return long(self.map[key])
        else:
            return defVal

    def get_as_double(self, key, defVal):
        """Gets the double value associated with the key, or defVal if not found.
        Raises ValueError, if the value is not numeric.

        NOTE: Python's built-in float type has double precision (it's a C double in CPython, a Java double in Jython).
        """

        if key in self.map:
            return float(self.map[key])
        else:
            return defVal
