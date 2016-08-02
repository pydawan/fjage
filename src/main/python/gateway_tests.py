# -*- coding: UTF-8 -*-
"""Gateway Tests: Test file for Gateway.

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

"""

import fjage
import time, sys, json

try:
	g1 = fjage.remote.Gateway('localhost', 5081)
except Exception, e:
    print "Exception:" + str(e)
    sys.exit(0)

# data1 = {
#     'id' : '1',
#     'action':'containsAgent',
#     'agentID':'shell'
#     }
# print(g1.request(data1, 1))

# data2 = {
#     'action' : 'send',
#     'message' : {
#         'msgID' : 1,
#         'recipient' : '#abc',
#         'sender' : 'rshell',
#         'msgType' : 'org.arl.fjage.Message'
#         },
#     'relay' : 'true'
#   }

# send a message dict and the JsonMessage class does the conversion for us
msg = {
    'msgID' : 1,
    'recipient' : '#abc',
    'sender' : 'rshell',
    'msgType' : 'org.arl.fjage.Message'
    }
#print(g1.request(msg, 1))

# print json.dumps(msg)
# print json.loads(json.dumps(msg))['recipient']

g1.send(msg)
msg1 = g1.receive_with_tout(5)

print msg1
print msg1["recipient"]
print msg1["sender"]
print msg1["msgType"]
print msg1["msgID"]

g1.shutdown()
