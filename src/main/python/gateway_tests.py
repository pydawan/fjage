# -*- coding: UTF-8 -*-
"""Gateway Tests: Test file for Gateway.

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

"""

import fjage
import time, sys, json, uuid

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
#     'relay' : True
#   }

#############################
# send a message dict and the JsonMessage class does the conversion for us
# msg = {
#     'msgID' : 1,
#     'recipient' : '#abc',
#     'sender' : 'rshell',
#     'msgType' : 'org.arl.fjage.Message'
#     }
#print(g1.request(msg, 1))

# g1.send(msg)
# msg1 = g1.receive_with_tout(5)

# print msg1
# print msg1["recipient"]
# print msg1["sender"]
# print msg1["msgType"]
#############################

# m1 = fjage.messages.Message()
# #m1 = fjage.shell.ShellExecReq()

# m1.setRecipient('#abc')
# m1.setSender('rshell')

# g1.send(m1)
# print g1.receive_with_tout(1)

####################################

# msg to send
m2 = fjage.messages.Message()

m2.setRecipient('#abc')
m2.setSender('rshell')

# received message
m3 = fjage.messages.Message()
# m3 = g1.request(m2, 1)

g1.send(m2)
m3 = g1.receive()

if m3:
    print m3.getMessageID()
    print m3.getRecipient()
    print m3.getSender()
    print m3.getPerformative()
    print m3.getInReplyTo()

g1.shutdown()
