"""Shell: Support for command scripts.

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

TODO:
    * Implement the various methods

"""
from messages import Message
from messages import Performative

class ShellExecReq(Message):
    """Request to execute shell command/script."""

    def __init__(self, **kwargs):
        Message.__init__(self)
        self.perf = "request"

        self.cmd = None
        # self.script = file()
        # TODO: Figure out how this will appear in the json
        self.args = list()

        # TODO: Verify whether the kwargs is used in a correct way.
        self.__dict__.update(kwargs)

    def setCommand(self, cmd):
        """Set the command to execute."""
        # if (self.cmd != null && self.script != null):
        #     raise Exception('ShellExecReq can either have a command or script, but not both')
        # self.cmd = cmd
        pass

    def getCommand(self):
        """Get the command to execute."""
        # return self.cmd
        pass

    def setScript(self, script):
        """Set the command to execute."""
        # if (self.cmd != null && self.script != null):
        #     raise Exception('ShellExecReq can either have a command or script, but not both')
        # self.script = script
        pass

    def setScript_with_args(self, script, args):
        """Set the command to execute."""
        # if (self.cmd != null && self.script != null):
        #     raise Exception('ShellExecReq can either have a command or script, but not both')
        # self.script = script;
        # self.args = args;
        pass

    def getScriptFile():
        # """Get the script to execute."""
        # return self.script;
        pass

    def getScriptArgs():
        """Get the script arguments."""
        # return self.args
        pass

    def isScript():
        """Check if the request is for a script."""
        # return self.script
        pass
