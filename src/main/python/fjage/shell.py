"""Shell: Support for command scripts.

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

TODO:
    * Implement the classes

"""
from messages import Message

class ShellExecReq(Message):
    """Request to execute shell command/script."""