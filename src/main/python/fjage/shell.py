"""Shell: Support for interactive shell and command scripts.

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

"""
from messages import Message as _msg
from messages import Performative as _perf

class ShellExecReq(_msg):
    """Request to execute shell command/script.

    Attributes:
        cmd
        script
        args

    NOTE: We do not implement setters/getters as that is not the python style.
    Guidelines for directly operating on the attributes are as follows:
    1. IMPORTANT: ShellExecReq can either have a command or script, but not both
    2. cmd can be any command (str) supported by the shell
    3. script is a dictionary which contains the path to the script file. E.g. "script":{"path":"samples/01_hello.groovy"}
    4. script has to be accompanied with arguments. (This may change in future)
    5. args is a list containing arguments to the script. E.g. ['null']

    Example ShellExecReq json message: 
    "message":{"script":{"path":"samples/01_hello.groovy"},"args":[],"msgID":"9cba408c-76ef-4df3-a7b1 da5cf7ee40e9",
                "perf":"REQUEST","recipient":"shell","sender":"rshell","msgType":"org.arl.fjage.shell.ShellExecReq"}

    """

    def __init__(self, **kwargs):

        _msg.__init__(self)
        self.perf = _perf().REQUEST
        self.cmd = None
        self.script = None
        self.args = None

        # TODO: Verify whether the kwargs is used in a correct way.
        self.__dict__.update(kwargs)
