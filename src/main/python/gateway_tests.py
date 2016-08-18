"""Gateway Tests: Test file for Gateway class.

Copyright (c) 2016, Manu Ignatius

This file is part of fjage which is released under Simplified BSD License.
See file LICENSE.txt or go to http://www.opensource.org/licenses/BSD-3-Clause
for full license details.

"""

import fjage
import time, sys, json, uuid

try:
	g1 = fjage.remote.Gateway('localhost', 5081, "PythonGW")
except Exception, e:
    print "Exception:" + str(e)
    sys.exit(0)

############ Test Message formats

# data1 = {
#     'id' : '1',
#     'action':'containsAgent',
#     'agentID':'shell'
#     }
# print(g1.request(data1, 1000))

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

############ Gateway Test - Message

# # msg to send
# m1 = fjage.Message()

# m1.recipient = '#abc'
# m1.sender = 'rshell'

# # received message
# m2 = fjage.Message()

# # m2 = g1.request(m1, 1000)
# if g1.send(m1):
#     m2 = g1.receive()

# if m2:
#     print m2.msgID
#     print m2.recipient
#     print m2.sender
#     print m2.perf
#     print m2.inReplyTo

# m1.recipient = '#def'
# m1.sender = 'rshell'

# # m2 = g1.request(m1, 1000)
# if g1.send(m1):
#     m2 = g1.receive()

# if m2:
#     print m2.msgID
#     print m2.recipient
#     print m2.sender
#     print m2.perf
#     print m2.inReplyTo

############ Gateway Test - Generic Message

# msg to send
# m1 = fjage.GenericMessage()
# m1.recipient = '#mno'

# # map
# m1.map["map1"] = "mapValue1"
# m1.map["map2"] = "mapValue2"
# m1.map["map3"] = "mapValue3"
# m1.map["map4"] = "mapValue4"

# # received message
# m2 = fjage.GenericMessage()
# # m2 = g1.request(m1, 1000)

# if g1.send(m1):
#     m2 = g1.receive(fjage.Message)

# if m2:
#     print m2.msgID
#     print m2.recipient
#     print m2.sender
#     print m2.perf
#     print m2.inReplyTo

############ ShellExecReq Message Tests

# msg to send
m3 = fjage.shell.ShellExecReq()

m3.recipient = 'shell'
m3.sender = 'rshell'
m3.script = {"path":"samples/01_hello.groovy"}
m3.args = []

# received message
m4 = fjage.shell.ShellExecReq()

if g1.send(m3):
    m4 = g1.receive(fjage.Message, 10000)

if m4:
    print m4.msgID
    print m4.recipient
    print m4.sender
    print m4.perf
    print m4.inReplyTo

# time.sleep(2)

m5 = fjage.shell.ShellExecReq()
m5.recipient = 'shell'
m5.sender = 'rshell'
# NOTE: Make sure either cmd or script has a value
m5.script = None
m5.args = None
m5.cmd = 'services'
m5.msgID = str(uuid.uuid4())

m6 = fjage.shell.ShellExecReq()
# received message
m6 = g1.request(m5, 10000)

if m6:
    print m6.msgID
    print m6.recipient
    print m6.sender
    print m6.perf
    print m6.inReplyTo

############# AgentID Tests
# a1 = g1.topic("manu")
# print a1.name
# print a1.is_topic

# a2 = g1.topic(1)
# print a2.name
# print a2.is_topic

# a3 = fjage.remote.AgentID("Daisy")
# a4 = g1.topic(a3)
# print a4.name
# print a4.is_topic

# a5 = fjage.remote.AgentID("Elle", True)
# a6 = g1.topic(a5)
# print a6.name
# print a6.is_topic

############## subscribe/unsubscribe test

# g1.subscribe(g1.topic("abc"))
# print g1.subscribers

# a1 = fjage.remote.AgentID("manu")

# g1.subscribe(a1)
# a1.is_topic = True
# g1.subscribe(a1)

# a1 = fjage.remote.AgentID("Daisy")
# g1.subscribe(a1)

# print "subscribers"
# for i in g1.subscribers:
#     print i

# a2 = fjage.remote.AgentID("Daisy")
# g1.unsubscribe(a2)

# # g1.unsubscribe("a1")

# # g1.unsubscribe(a1)

# print "updated subscribers"
# for i in g1.subscribers:
#     print i

############## agentForService ... test
# g1.agentForService("shell")
# g1.agentsForService("shell")

# g1.agentForService(True)
# time.sleep(2)
# g1.agentsForService(20)
