fjåge protocol documentation
=====

Introduction
------------

fjåge agents reside in one or more containers that provide agent management, directory and messaging services. Various containers may run on the same node, or on different nodes in a network. The containers communicate with each other using some form of communication mechanism. Until version 1.3 fjåge an RPC based mechanism was used to communicate between containers.

From version 1.4, fjåge uses [JSON](https://en.wikipedia.org/wiki/JSON) for communication between remote containers. The JSON objects are exchanged over some low level networked connection protocol like TCP. This document defines the protocol of the JSON objects exchanged between the containers.


Transport and Framing
---------------------

fjåge containers are connected to each other over some form of networked transport. Typically this is a TCP connection, however, the JSON protocol does not assume any specific behavior of the underlying transport connection. Other transports like Serial-UART may also be used.

Over the networked transport, the containers communicate using [line delimited JSON messages](https://en.wikipedia.org/wiki/JSON_Streaming#Line_delimited_JSON). These JSON objects are framed by a newline characters (`\n` or `\r` or `\r\n`).

Each such frame contain a single JSON object which adheres to the JSON as defined in [RFC7159](https://tools.ietf.org/html/rfc7159), and does not support unescaped new-line characters inside a JSON object. The prettified JSON objects with new-lines are shown below for examples and should be "JSONified" before being used.

JSON Object Format
------------------

## Basics

fjåge's JSON protocol objects are typically shallow JSON objects. The first level of attributes are typically used by the containers to hold metadata and perform housekeeping tasks such as agent directory service. The attribute `message` in the JSON object contains the actual message that is exchanged between agents residing in different containers.

Here is a JSON object which exemplifies format of the protocol.

```
{  
   "action":"send",
   "message":{  
      "ticks":3020735000,
      "temp1":33,
      "temp2":33,
      "time":1001098512120885,
      "msgID":"59b60c55-bd94-4ce5-934e-5dfd523aeef2",
      "perf":"INFORM",
      "recipient":"#dsp__ntf",
      "sender":"dsp",
      "msgType":"org.arl.modem.DSPStatusNtf"
   },
   "relay":false
}
```

There are some identifiers that are used throughout the JSON Object.

- `AgentID` : And AgentID is a unique String identifier given to each fjage agent running containers.
- `id` and `msgID` : Universally Unique Identifiers ([UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier)) stored a a String to tag and distinguish JSON objects and messages in fjåge.

## Actions

Each JSON object is defined to execute a certain action when it reaches the target container.

These 7 actions are supported in the fjåge's JSON protocol are `agents, containsAgent, services, agentForService, agentsForService, send, shutdown`, and the `action` top level attribute is used in the JSON object to define the action the container is to perform on receiving the object.

`agents` - Request for a list of all agents running on the target container.
`containsAgent` - Request to check if a specific container has a agent with a given AgentID running.
`services` - Request for a list of all services running on the target container.
`agentForService` - Request for AgentID of an agent that is providing a specific service.
`agentForService` - Request for AgentID of all agents that is providing a specific service.
`send` - Request to send a payload to the target container.
`shutdown` - Request to shutdown the target container.

## Responses

Based on the action and the state of the container, a JSON object may optionally trigger a response JSON object from the target container. The response JSON object has the exact same `id` as the original action JSON object and has a attribute `inResponseTo` which contains the action to which this message is a response to.

## Attributes

Attributes supported at the top level of the JSON object are listed below.

`id` : **String** (mandatory) - A UUID assigned to to each object.

`action` : **String** (optional) - Denotes the main action the object is supposed to perform. Valid actions are : `agents, containsAgent, services, agentForService, agentsForService, send, shutdown`. If this attribute is empty, then the object is a response to a previous action object and should have the `inResponseTo` field populated.

`inResponseTo` : **String** (optional) - Denotes the action to which this object is a response to. A response object will have the exact same `id` as the original action object.

`agentID` :  **String** (optional) - An AgentID. This attribute is populated in objects which are responses to objects requesting the ID of an agent providing a specific service `"action" : "agentForService"`. This field may also be used in objects with `"action" : "containsAgent"` to check if an agent with the given AgentID is running on a target container.

`agentIDs`: **Array** (optional) - This attribute is populated in objects which are responses to objects requesting the IDs of agents providing a specific service with `action : "agentsForService"`, or objects which are responses to objects requesting a list of all agents running in a container.

`service` :  **String** (optional) - Used in conjunction with `"action" : "agentForService"` and `"action" : "agentsForService"` to query for agent(s) providing this specific service.

`services`: **Array** (optional) - This attribute is populated in objects which are responses to objects requesting the services available with `"action" : "services"`.

`answer` : **Boolean** (optional) - This attribute is populated in objects which are responses to query objects with `"action" : "containsAgent"`.

`relay` : **Boolean** (optional) - This attribute defines if the target container should relay (forward) the message to other containers it is connected to or not.

`message` : **Object** (optional) - The main payload. This holds the contents of the payload in objects with `"action" : "send"`. The structure and format of this Object is discussed in the next section.


Payload Message Format
----------------------

JSON object with `"action" : "send"` have a payload of type Object contained in the `message` attribute, which is sent to the appropriate agent when the JSON message reaches the target container. This Object, referred to in fjåge documentation as a [Message](https://org-arl.github.io/fjage/doc/html/messages.html#sending-and-receiving-messages), has a type associated with it. Messages are also targeted certain agents and can carry other attributes depending on the type of the message.

## Attributes

The attributes contained within each message are dependent on the message type and it's function. However, all messages share some common attributes.

`msgID` : **String** (mandatory) - A [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) assigned to to each message.
`perf` : **String** (mandatory) - Performative. Defines the purpose of the message. Valid performatives are : `REQUEST, AGREE, REFUSE, FAILURE, INFORM, CONFIRM, DISCONFIRM, QUERY_IF, NOT_UNDERSTOOD, CFP, PROPOSE, CANCEL`.
`recipient` : **String** (mandatory) - An AgentID of the fjåge agent this message is being addressed to.
`sender` : **String** (mandatory) - An AgentID on the fjåge this message is being sent by.
`inReplyTo` : **String** (optional) - A UUID. Included in a reply to another object to indicate that this object is a reply to a object with this `id`.
`msgType` : **String** (optional) - A string identifier that identifies the type of the message. This is usually a fully qualified Java class name of the class of that type of message.

##Performatives

Performative is an action represented by a message. These are performatives supported by fjåge.

`AGREE` - Agree to performing the requested action.
`CANCEL` - Cancel pending request.
`CFP` - Call for proposal.
`CONFIRM` - Confirm that the answer to a query is true.
`DISCONFIRM` - Confirm that the answer to a query is false.
`FAILURE` - Notification of failure to perform a requested or agreed action.
`INFORM` - Notification of an event.
`NOT_UNDERSTOOD` - Notification that a message was not understood.
`PROPOSE` - Response for CFP.
`QUERY_IF` - Query if some statement is true or false.
`REFUSE` - Refuse to perform the requested action.
`REQUEST` - Request an action to be performed.

Examples
--------

Here are some example valid JSON objects and their descriptions.

#### containAgent action-response

The following JSON object is a query to the target container if it contains an agent with the AgentID, _PythonGW_.

```
{
  "action": "containsAgent",
  "agentID": "PythonGW",
  "id": "acc215d2-6d91-4b23-bd1c-2e263c18d2f8"
}
```

This JSON object is a response to the previous JSON object, with an answer _false_ and hence indicates that there is no such agent in the container.

```
{
  "id": "acc215d2-6d91-4b23-bd1c-2e263c18d2f8",
  "inResponseTo": "containsAgent",
  "answer": false
}
```

#### agentForService action-response

The following JSON object is a directory service query to check find an agent which provides the _org.arl.fjage.shell.Services.SHELL_ service..

```
{  
   "action":"agentsForService",
   "id":"6d877f78-f41e-4436-b67d-c65056810185",
   "service":"org.arl.fjage.shell.Services.SHELL"
}
```

This JSON Object is a response to the previous JSON object, with an answer _shell_ which is the AgentID of the agent which provides the specified service.

```
{  
   "id":"a4d64c03-3f12-4cd0-a0ce-c787c889a962",
   "inResponseTo":"agentForService",
   "agentID":"shell"
}
```


#### Request

```
{
  "action": "send",
  "message": {
    "index": -1,
    "requests": [],
    "msgID": "d554a686-f209-418c-a08f-740dcfb1ba11",
    "perf": "REQUEST",
    "recipient": "mac",
    "sender": "unetsh#5tc6uv",
    "msgType": "org.arl.unet.ParameterReq"
  },
  "relay": true
}
```

#### Response


```
{  
   "action":"send",
   "message":{  
      "index":-1,
      "values":{  
         "channelBusy":false,
         "reservationsPending":0,
         "load":0.0,
         "maxBackoff":10.0,
         "memory":0.5,
         "ackPayloadSize":0,
         "targetLoad":1.0,
         "maxReservationDuration":Infinity,
         "idleLoad":0.1,
         "minRate":0.1,
         "reservationPayloadSize":0
      },
      "msgID":"e113749a-c7fe-4919-bb47-e73303be666f",
      "perf":"INFORM",
      "recipient":"unetsh#5tc6uv",
      "sender":"mac",
      "inReplyTo":"d554a686-f209-418c-a08f-740dcfb1ba11",
      "msgType":"org.arl.unet.ParameterRsp"
   },
   "relay":false
}
```

#### Notification

```
{  
   "action":"send",
   "message":{  
      "ticks":3020735000,
      "temp1":33,
      "temp2":33,
      "time":1001098512120885,
      "msgID":"59b60c55-bd94-4ce5-934e-5dfd523aeef2",
      "perf":"INFORM",
      "recipient":"#dsp__ntf",
      "sender":"dsp",
      "msgType":"org.arl.modem.DSPStatusNtf"
   },
   "relay":false
}
```