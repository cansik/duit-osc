# OSC for Duit
[![PyPI](https://img.shields.io/pypi/v/duit-osc)](https://pypi.org/project/duit-osc/)
[![Github](https://img.shields.io/badge/duit-osc?logo=github&label=github&color=green)
](https://github.com/cansik/duit-osc)


Open Sound Control communication for duit datafields.

This is an addon module for the data ui toolkit ([duit](https://github.com/cansik/duit)) which adds OSC in and output support for [DataFields](https://cansik.github.io/duit/duit.html#data-field).

## Installation
The package can ben installed directly from [PyPI](https://pypi.org/project/duit-osc/).

```
pip install duit-osc
```

## Documentation
Duit-osc uses [python-osc](https://pypi.org/project/python-osc/) (`~=1.8`) as OSC backend to receive and send message. The main class is the `OscService` which handles the incoming and outgoing OSC server and client. It also maps the annotated `DataFields` to the corresponding route.

### OscEndpoint
It is possible to annotate existing `DataFields` with the `OscEndpoint` annotation. This annotation later tell the `OscService` if the field has to be exposed over OSC. It is recommended to gather all DataFields in a single object:

```python
from duit_osc.OscEndpoint import OscEndpoint

class Config:
    def __init__(self):
        self.name = DataField("Cat") | OscEndpoint()
```

By default, the name of the variable (e.g. `name`) is used as OSC address identifier. It is possible to change the name through the `OscEndpoint` annotation.

```python
self.name = DataField("Cat") | OscEndpoint(name="the-cats-name")
```

#### Direction
By default, an annotated `DataField` sends out an OSC message on change and is changed by incoming OSC messages. This behaviour can be controlled by the `OscDirection` option of the `OscEndpoint` annotation.

```python
from duit_osc.OscDirection import OscDirection

# ...
self.name = DataField("Cat") | OscEndpoint(direction=OscDirection.Send)
```

- `OscDirection`
  - Send - *Does only send the datafield value on change.*
  - Receive - *Does only receive the datafield value.*
  - Bidirectional (Default) - *Sends and receives the value over OSC*

### OscService
As already mentioned, the OscService handles the OSC server and mapping with the `DataFields`. Here is a simple example on how to create an `OscService`, add the previous defined config and start the service.

```python
# create an actual instance of the config
config = Config()

# create an osc service
osc_service = OscService()

# add the config object (create mapping) under the route "/config"
osc_service.add_route("/config", config)

# print the api description of the service (experimental)
print(osc_service.api_description())

# run the service
osc_service.run()
```

#### Settings

The `OscService` has several default arguments, like the `host`, `in_port`, `out_port` and so on. These can be changed before the service is started:

```python
# OscService parameters and the default values
host: str = "0.0.0.0", # on which interface the service is running
in_port: Optional[int] = 8000, # on which port the OscServer is started
out_port: Optional[int] = 9000, # on which port the OscClient is sending
allow_broadcast: bool = True, # if broadcasting is allowed
send_on_receive: bool = False # Indicated if a message that has been received should be also sent out again (reply the change back)
```

#### Routes
It is possible to add various objects to the OscService, each with a unique route (address).

```python
osc_service.add_route("/config", config)
```

Each `DataField` is added under this route, so for example the `name` field would get the OSC address `/config/name`.

#### Start
To start the service, it is necessary to call `run()`. This is a blocking method, which does not return until the service is shutdown. If it should run as a background thread, use the `blocking` parameter:

```python
osc_service.run(blocking=False)
```

#### API Description
It is possible to print an API description. This is highly experimental and will change in the future:

```python
print(osc_service.api_description())
```
 
## About
Copyright (c) 2024 Florian Bruggisser
