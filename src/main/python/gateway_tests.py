"""Gateway Tests: Test file for Gateway.

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

"""

import fjage
import time, sys, json

try:
	g1 = fjage.rmi.Gateway('localhost', 5081)
except:
	print "Cannot connect to server"
	sys.exit(0)

# g1.create_msg("id", 1)
# g1.create_msg("action", "containsAgent")
# g1.create_msg("agentID", "shell")
# g1.send()
# time.sleep(1)
# print(g1.receive())

# g1.create_msg("id", 1)
# g1.create_msg("action", "containsAgent")
# g1.create_msg("agentID", "shell")
# print(g1.request(g1.get_msg(), 1))

data = {
    'action' : 'send',
    'message' : {
        'msgID' : 1,
        'recipient' : '#abc',
        'sender' : 'rshell',
        'msgType' : 'org.arl.fjage.Message'
        },
    'relay' : 'true'
}

print json.dumps(data)
print(g1.request(data, 1))

print(g1.receive_with_tout(5))

g1.shutdown()
