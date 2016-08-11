"""Gateway Tests: Test file for Gateway class.

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


############ Test Message formats

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

############ Gateway Test - Message

# # msg to send
# m1 = fjage.messages.Message()

# m1.recipient = '#abc'
# m1.sender = 'rshell'

# # received message
# m2 = fjage.messages.Message()

# # m2 = g1.request(m1, 1)
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

# # m2 = g1.request(m1, 1)
# if g1.send(m1):
#     m2 = g1.receive()

# if m2:
#     print m2.msgID
#     print m2.recipient
#     print m2.sender
#     print m2.perf
#     print m2.inReplyTo

# g1.shutdown()

############ Gateway Test - Generic Message

# # msg to send
# m1 = fjage.messages.GenericMessage()

# m1.recipient = '#mno'
# m1.sender = 'rshell'

# # map
# m1.put("map1", "mapValue1")
# m1.put("map2", "mapValue2")
# m1.put("map3", "mapValue3")
# m1.put("map4", "mapValue4")

# # received message
# m2 = fjage.messages.GenericMessage()
# # m2 = g1.request(m1, 1)

# if g1.send(m1):
#     m2 = g1.receive()

# if m2:
#     print m2.msgID
#     print m2.recipient
#     print m2.sender
#     print m2.perf
#     print m2.inReplyTo

# g1.shutdown()

############ ShellExecReq Message Tests

# msg to send
m3 = fjage.shell.ShellExecReq()

m3.recipient = 'shell'
m3.sender = 'rshell'
m3.script = {"path":"samples/01_hello.groovy"}
m3.args = []

# received message
m4 = fjage.shell.ShellExecReq()
# m4 = g1.request(m3, 1)

if g1.send(m3):
    m4 = g1.receive()

time.sleep(5)

m3.recipient = 'shell'
m3.sender = 'rshell'
# NOTE: Make sure either cmd or script has a value
m3.script = None
m3.args = None
m3.cmd = 'services'

# received message
m4 = g1.request(m3, 1)

############# GenericMessage Tests

# g = fjage.messages.GenericMessage()

# print g.gmap                                # {}

# # init values
# g.put("map1", "mapValue1")
# g.put("map2", "mapValue2")
# g.put("map3", "mapValue3")
# g.put("map4", "mapValue4")

# print g.gmap                                # {'map2': 'mapValue2', 'map3': 'mapValue3', 'map1': 'mapValue1', 'map4': 'mapValue4'}

# print g.containsKey('map1')                 # True
# print g.containsKey('4')                    # False
# print g.containsValue('mapValue2')          # True
# print g.containsValue('s')                  # False
# print g.entrySet()                          # set(['mapValue4', 'mapValue2', 'mapValue3', 'mapValue1'])
# print g.isEmpty()                           # False
# print g.keySet()                            # set(['map2', 'map3', 'map1', 'map4'])
# g.clear()
# print g.isEmpty()                           # True
# print g.gmap                                # {}
# print g.entrySet()                          # set([])
# print g.keySet()                            # set([])

# print g.recipient                           # None
# print g.put("recipient", "#pqr")            # #pqr
# print g.put("sender", "123")                # None
# print g.put("messageID", "5")               # <a random msgID>
# print g.put("mapping", "MappingValue123")   # MappingValue123
# print g.gmap                                # {'mapping': 'MappingValue123'}
# print g.get("mapping")                      # MappingValue123
# print g.get("sender")                       # None
# print g.get("recipient")                    # #pqr

# in_map = dict()
# in_map["test1"] = "T1"
# in_map["test2"] = "T2"
# in_map["test3"] = "T3"
# g.putAll(in_map)
# print g.gmap                                # {'test1': 'T1', 'test3': 'T3', 'test2': 'T2'}

# print g.remove("test1")                     # T1
# print g.gmap                                # {'test3': 'T3', 'test2': 'T2'}
# print g.remove("1")                         # None

# print g.size()                              # 2
# print g.values()                            # ['T3', 'T2']

# print g.get_as_string("test3", "Null")      # T3
# print g.get_as_string("test4", "Null")      # Null

# g.put("test4", "4")
# g.put("test5", 5)
# # print g.get_as_int("test3", 13)
# print g.get_as_int("test4", 14)             # 4
# print g.get_as_int("test5", 15)             # 5
# print g.get_as_int("test6", 16)             # 16

# g.put("test7", "65537")
# g.put("test8", 299999)
# # print g.get_as_long("test3", 13)
# print g.get_as_long("test7", 170000)        # 65537
# print g.get_as_long("test8", 180000)        # 299999
# print g.get_as_long("test9", 190000)        # 190000

# g.put("test10", "3.14")
# g.put("test11", 1.2345)
# # print g.get_as_double("test3", 13)
# print g.get_as_double("test10", 10.1)       # 3.14
# print g.get_as_double("test11", 11.2)       # 1.2345
# print g.get_as_double("test12", 12.3)       # 12.3
# print g.gmap                                # {'test3': 'T3', 'test2': 'T2', 'test5': 5, 'test4': '4', 'test7': '65537', 'test8': 299999, 'test11': 1.2345, 'test10': '3.14'}
# g.clear()
# print g.gmap                                # {}
