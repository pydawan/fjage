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

class Action:
    def __init__(self):
        self.AGENTS = "agents"
        self.CONTAINS_AGENT = "containsAgent"
        self.SERVICES = "services"
        self.AGENT_FOR_SERVICE = "agentForService"
        self.AGENTS_FOR_SERVICE = "agentsForService"
        self.SEND = "send"
        self.SHUTDOWN = "shutdown"

class Message:
    """Base class for messages transmitted by one agent to another.

    This class provides the basic attributes of messages and is typically
    extended by application-specific message classes. To ensure that messages
    can be sent between agents running on remote containers, all attributes
    of a message must be serializable.
    """

    def __init__(self):
        self.msgID = str(_uuid.uuid4())
        self.perf = None
        self.recipient = None   #TODO: Current assumption: if recipient is topic, the string will start with a '#'. Verify this
        self.sender = None
        self.inReplyTo = None

        self.m_dict = dict()

    def to_json(self):
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

        return self.m_dict

    def from_json(self, m_dict):
        """Converts message dictionary to Message object from json."""

        is_msgID = False

        for key in m_dict:

            if key == "perf":
                self.perf = m_dict["perf"]

            if key == "recipient":
                self.recipient = m_dict["recipient"]

            if key == "sender":
                self.sender = m_dict["sender"]

            if key == "msgID":
                self.msgID = m_dict["msgID"]
                is_msgID = True

            if key == "inReplyTo":
                self.inReplyTo = m_dict["inReplyTo"]

        if is_msgID != True:
            raise Exception("Missing msgID")

class GenericMessage(Message):
    """A message class that can convey generic messages represented by key-value pairs."""

    gmap = dict();

    def clear(self):
        """ Clears the dict."""
        self.gmap.clear()

    def containsKey(self, key):
        """Returns true if this map (dict) contains a mapping for the specified key."""
        return self.gmap.has_key(key)

    def containsValue(self, value):
        """Returns true if this map (dict) contains a mapping for the specified value."""
        return value in self.gmap.values()

    def entrySet(self):
        """Returns a Set view of the mappings contained in this map (dict)."""
        s = set()
        for v in self.gmap.values():
            s.add(v)
        return s

    def isEmpty(self):
        """Returns true if this map (dict) contains no key-value mappings."""
        return not self.gmap

    def keySet(self):
        s = set()
        for v in self.gmap:
            s.add(v)
        return s

    def put(self, key, value):
        """Associates the specified value with the specified key in this map (dict)."""

        # TODO: Why "perf" in Message and "performative" here. What will happen if its "perf"?
        if key == "performative":
            self.perf = value
            return value

        if key == "recipient":
            self.recipient = value
            return value

        if key == "sender":
            return self.sender

        # TODO: Why "msgID" in Message and "messageID" here. What will happen if its "msgID"?
        if key == "messageID":
            return self.msgID

        if key == "inReplyTo":
            return self.inReplyTo

        self.gmap[key] = value
        return value

    def get(self, key):
        """Returns the value to which the specified key is mapped, or None if this map (dict) contains no mapping for the key."""

        # TODO: Why "perf" in Message and "performative" here. What will happen if its "perf"?
        if key == "performative":
            return self.perf

        if key == "recipient":
            return self.recipient

        if key == "sender":
            return self.sender

        # TODO: Why "msgID" in Message and "messageID" here. What will happen if its "msgID"?
        if key == "messageID":
            return self.msgID

        if key == "inReplyTo":
            return self.inReplyTo

        if key in self.gmap:
            return self.gmap[key]
        else:
            return None

    def putAll(self, in_map):
        """Copies all of the mappings from the specified map to this map (dict)."""
        if type(in_map) != type(self.gmap):
            return

        # TODO: Verify whether we need to clear gmap before the copying operation
        self.clear()
        self.gmap = in_map.copy()

    def remove(self, key):
        """Removes the mapping for the specified key from this map (dict) if present."""
        return self.gmap.pop(key, None)

    def size(self):
        """Returns the number of key-value mappings in this map (dict)."""
        return len(self.gmap)

    def values(self):
        """Returns a list of all the values contained in this map (dict)."""
        return self.gmap.values()

################# Special getters

    def get_as_string(self, key, defVal):
        """Gets the string value associated with the key, or defVal if not found."""
        if key in self.gmap:
            return str(self.gmap[key])
        else:
            return defVal

    def get_as_int(self, key, defVal):
        """Gets the integer value associated with the key, or defVal if not found.
        Raises ValueError, if the value is not numeric.
        """

        if key in self.gmap:
            return int(self.gmap[key])
        else:
            return defVal

    def get_as_long(self, key, defVal):
        """Gets the long value associated with the key, or defVal if not found.
        Raises ValueError, if the value is not numeric.
        """

        if key in self.gmap:
            return long(self.gmap[key])
        else:
            return defVal

    def get_as_double(self, key, defVal):
        """Gets the double value associated with the key, or defVal if not found.
        Raises ValueError, if the value is not numeric.

        NOTE: Python's built-in float type has double precision (it's a C double in CPython, a Java double in Jython).
        """

        if key in self.gmap:
            return float(self.gmap[key])
        else:
            return defVal