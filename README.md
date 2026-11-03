# MQTT IoT Implementation

This repository is a small IoT example built on the MQTT protocol. Publisher clients send data to a broker, and subscriber clients receive that data from the broker. Publishers and subscribers do not connect to each other.

The demo simulates a pH sensor. `renee_publisher.py` opens a desktop window, builds readings with `renee_generator.py`, and publishes JSON to the topic `phLevel`. `renee_subscriber.py` opens another window, subscribes to `phLevel`, and shows each message that arrives.

```text
renee_generator.py  ->  renee_publisher.py  ->  MQTT broker  ->  renee_subscriber.py
   simulated pH          GUI publisher        localhost:1883      GUI subscriber
                                              topic: phLevel
```

## Requirements

- **Python 3.6 or newer.** The scripts use f-strings. They also use Tkinter, which ships with the standard library.
- **Tkinter present in that Python install.** The official Windows and macOS installers from python.org include it. On Debian or Ubuntu, install the OS package `python3-tk`. On Fedora, install `python3-tkinter`.
- **[`paho-mqtt` 1.6.x](https://pypi.org/project/paho-mqtt/1.6.1/),** listed in `requirements.txt`. Both clients call `mqtt.Client()` and the subscriber uses the 1.x `on_connect(client, userdata, flags, rc)` callback. `paho-mqtt` 2.0.0 rejects `mqtt.Client()` with no callback API version (`TypeError: Client.__init__() missing 1 required positional argument: 'callback_api_version'`). Version 2.1.0 accepts the call again and emits a deprecation warning. The pin stays on 1.x so a fresh install matches the code.
- **An MQTT broker listening on `localhost` port `1883` that allows anonymous clients.** These scripts send no username, password, or TLS settings, and they use MQTT 3.1.1 (the paho-mqtt default). The repository does not include a broker or a script that starts one.

A machine running the GUIs needs a graphical display. On a headless session, Tkinter exits with an error about the display.

## Installation

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python3 -m pip install -r requirements.txt
```

Use `python` instead of `python3` when that command already runs Python 3.

Install Tkinter from the OS if `python3 -c "import tkinter"` fails. It is not a pip package; the unrelated `tk` project on PyPI is something else.

## MQTT broker

Start the broker before either client. Both scripts call `client.connect()` while the window is being created, before `mainloop()`. If nothing is accepting TCP connections on `localhost:1883`, that call raises `ConnectionRefusedError` and the script exits with a traceback.

[Eclipse Mosquitto](https://mosquitto.org/) is a broker that satisfies this when you run it with no configuration file. In that mode Mosquitto 2.x binds to the loopback interface and allows anonymous clients:

```bash
mosquitto
```

`mosquitto -p 1883` is the same default listener. If port 1883 is already in use, an existing local broker may already be running.

Mosquitto 2.x turns anonymous access off for a listener you define in a configuration file. These clients connect without a username, so that listener needs anonymous access enabled:

```conf
listener 1883 127.0.0.1
allow_anonymous true
```

Save that as a file of your own (this repository does not ship one) and start Mosquitto with it:

```bash
mosquitto -c /path/to/mosquitto.conf
```

Any other broker works if it meets the same contract: `localhost`, port `1883`, anonymous MQTT 3.1.1.

## Configuration

Nothing in the repository reads command-line arguments, environment variables, or a config file for the connection. Host, port, and topic are module-level constants, duplicated in the two clients:

```python
broker = "localhost"
port = 1883
topic = "phLevel"
```

Those lines are at the top of `renee_publisher.py` and `renee_subscriber.py`. Change them in both files so the publisher and subscriber still meet on the same broker and topic. Restart both scripts after editing.

Other connection choices are the library defaults:

| Setting | Value in this code |
| --- | --- |
| Broker host | `localhost` |
| Port | `1883` |
| Topic | `phLevel` |
| Protocol | MQTT 3.1.1 |
| Username / password | none |
| TLS | none |
| Client id | none (paho-mqtt generates one per process) |
| Publish QoS | `0` |
| Subscribe QoS | `0` |
| Retained messages | off |

`renee_generator.py` has no broker settings. The pause between publishes is `random.uniform(1, 5)` seconds inside `renee_publisher.py`, so each gap is somewhere from 1 to 5 seconds.

## Usage

Run the commands from the repository root, after the broker is up. Start the subscriber first if you want to see the first readings. Messages are not retained, so a subscriber only shows readings published after it connects.

```bash
python3 renee_subscriber.py
python3 renee_publisher.py
```

You can launch either script by path from another directory. Python puts the script's folder on `sys.path`, which is how the publisher imports `renee_generator`.

### Subscriber

`renee_subscriber.py` opens a window titled `Subscriber_`. On startup it connects to the broker, starts the paho network loop, and subscribes to `phLevel` from `on_connect`. There is no start button. Incoming payloads are parsed with `json.loads` and appended to the log as `Received: ...`. The **Close** button destroys the window and ends the program.

A payload that is not JSON raises inside the message callback. The publisher always sends JSON.

### Publisher

`renee_publisher.py` opens a window titled `Publisher_`. It connects to the broker while the window is being created, and it stays idle until you press **Start Publishing**.

That button starts one background thread and then disables itself. The thread loops until you close the window:

1. It takes the next `packet_id`, starting at `1` for that process.
2. It calls `DataGenerator.generate_data()`.
3. It publishes one JSON object to `phLevel`.
4. It appends `Published: ...` to the log.
5. It sleeps for a random interval between 1 and 5 seconds.

The thread is a daemon, so closing the window stops publishing. There is no stop button. Run the script again to start another session. The button can be pressed once per process.

Several publisher processes and several subscriber processes can run at the same time. Every subscriber to `phLevel` receives every message. Each publisher keeps its own `packet_id` counter, starting at `1`.

### Reading the log

Each log is a read-only scrolled text area, 10 lines tall. The text you see is the Python dictionary after `json.loads` (or the dictionary before `json.dumps` on the publisher), so keys appear with single quotes. The bytes on the wire are JSON.

## Message format

Each publish is one JSON object. The numeric pH is the inner `ph_value`. The outer `ph_value` is the whole dictionary returned by `DataGenerator.generate_data()`. Example:

```json
{
  "timestamp": "2026-11-03T12:00:01.100000",
  "packet_id": 1,
  "ph_value": {
    "timestamp": "2026-11-03T12:00:01.099000",
    "packet_id": 4821,
    "ph_value": 7.14
  }
}
```

| Field | Meaning |
| --- | --- |
| `timestamp` | Local time from `datetime.now().isoformat()`, with no timezone offset. The outer value is taken just after the inner one. |
| `packet_id` | Outer: integer counter for this publisher process, starting at `1`. Inner: random integer from `1000` through `9999`, chosen by the generator. |
| `ph_value` | Outer: the generator dictionary. Inner: a float. Usually it is drawn from the range 6.5 to 8.5. On 1 in 1,001 readings (`random.randint(0, 1000) == 0`) it is drawn from the range 0 to 14 instead. |

`renee_generator.py` only supplies that inner dictionary. The publisher adds the outer `timestamp` and `packet_id` and places the dictionary under `ph_value`. Running `renee_generator.py` by itself defines `DataGenerator` and exits; it does not print samples or open a window.

## Project structure

The repository is flat: three scripts plus this documentation and `requirements.txt`. There is no package layout and there are no tests.

| Path | Role |
| --- | --- |
| `renee_generator.py` | `DataGenerator.generate_data()`, the simulated pH reading. Imported by the publisher. |
| `renee_publisher.py` | Tkinter publisher. Connects to the broker, and publishes after **Start Publishing**. |
| `renee_subscriber.py` | Tkinter subscriber. Connects, subscribes, and logs messages as they arrive. |
| `requirements.txt` | Pins `paho-mqtt` to the 1.x line these clients call. |
| `README.md` | This document. |

## Limitations

- The value a subscriber must read for the simulated pH is `payload["ph_value"]["ph_value"]`. The outer `ph_value` is a dictionary.
- Both windows include a check that is meant to drop the oldest log line once 10 entries are stored. The check compares the text line number with the string `"11.0"`, so the two sides never match and the scrollback keeps every line. The widget still shows 10 lines at a time.
- Neither client reconnects, and neither sets a username, password, or TLS. A broker that requires authentication will reject the connection.
- Publishes use QoS 0 and are not retained, so a subscriber that connects later misses earlier readings. The publisher never calls `loop_start()`. paho-mqtt 1.x still writes these QoS 0 packets from `publish()`. The subscriber calls `loop_start()` so it can receive messages.
- The repository has no license file.
