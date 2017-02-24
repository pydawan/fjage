#!/usr/bin/env python

import sys
sys.path.insert(0, "src/main/python")

import fjage
from IPython import embed


quick_guide = """\
?         -> Introduction and overview of the shell's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.
"""

banner_parts = [
    'Fjage python shell {version} -- An interactive shell for Fjage.\n\n'.format(
        version=fjage.version,
        ),
    quick_guide]

banner = ''.join(banner_parts)

header="Welcome to Fjage python shell"
exit_msg="Thank you for using Fjage shell. See you soon!"

embed(header=header, banner1=banner, exit_msg=exit_msg)
