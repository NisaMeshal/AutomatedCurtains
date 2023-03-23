import command_line_utils
from awscrt import mqtt
import sys
import threading
import time
from uuid import uuid4
import json


class RunMotor():
    import RPi.GPIO as GPIO
    from time import sleep
    from datetime import datetime

    GPIO.setmode(GPIO.BOARD)
    
    time_setting = False
    open = True
    open_time = []
    close_time = []
    
    def parse_setting(self, payload):
        if payload["setting"] == "open":
            if open == True:
                return
            else:
                self.open_curtain()
                open = True
        if payload["setting"] == "close":
            if open == True:
                self.close_curtain()
                open = False
            else:
                return
        if payload["setting"] == "time":
            time_setting = True
            open_time = payload["setting"]["open"]
            close_time = payload["setting"]["close"]
            

    def open_curtain(self):
        GPIO.setup(12, GPIO.OUT)
        stop = False
        try:
            while stop == False:
                print("turning on")
                GPIO.output(12, GPIO.HIGH)
                # need to change this depending on the length
                sleep(10)
                print("Stopping motor")
                GPIO.output(12, GPIO.LOW)
                stop = True
        finally:
            GPIO.cleanup()
        self.open = True

    def close_curtain(self):
        GPIO.setup(11, GPIO.OUT)
        stop = False
        try:
            while stop == False:
                print("turning on")
                GPIO.output(11, GPIO.HIGH)
                # need to change this depending on the length
                sleep(10)
                print("Stopping motor")
                GPIO.output(11, GPIO.LOW)
                stop = True
        finally:
            GPIO.cleanup()
        self.open = False

    def is_now(self, time):
        now = datetime.now().time().replace(second=0, microsecond=0)
        now = int(now.strftime('%H:%M')
        now = now.split(":")
        now = [str(x) for x in now]
        if now == time:
            print("it's now")
            return True
        else:
            ("it's not now")
            return False


curtain = RunMotor()
# This sample uses the Message Broker for AWS IoT to send and receive messages
# through an MQTT connection. On startup, the device connects to the server,
# subscribes to a topic, and begins publishing messages to that topic.
# The device should receive those same messages back from the message broker,
# since it is subscribed to that same topic.


# Parse arguments
cmdUtils = command_line_utils.CommandLineUtils(
    "PubSub - Send and recieve messages through an MQTT connection.")
cmdUtils.add_common_mqtt_commands()
cmdUtils.add_common_topic_message_commands()
cmdUtils.add_common_proxy_commands()
cmdUtils.add_common_logging_commands()
cmdUtils.register_command(
    "key", "<path>", "Path to your key in PEM format.", True, str)
cmdUtils.register_command(
    "cert", "<path>", "Path to your client certificate in PEM format.", True, str)
cmdUtils.register_command(
    "port", "<int>", "Connection port. AWS IoT supports 443 and 8883 (optional, default=auto).", type=int)
cmdUtils.register_command(
    "client_id", "<str>", "Client ID to use for MQTT connection (optional, default='test-*').", default="test-" + str(uuid4()))
cmdUtils.register_command(
    "count", "<int>", "The number of messages to send (optional, default='10').", default=5, type=int)
cmdUtils.register_command(
    "is_ci", "<str>", "If present the sample will run in CI mode (optional, default='None')")
# Needs to be called so the command utils parse the commands
cmdUtils.get_args()

received_count = 0
received_all_event = threading.Event()
is_ci = cmdUtils.get_command("is_ci", None) != None

# Callback when connection is accidentally lost.


def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

# Callback when an interrupted connection is re-established.


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(
        return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))

# Callback when the subscribed topic receives a message


def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    """
    Hypothetical message object we might use
    {
            "setting": "time" or "sensor",
            "open": [hour, minute],
            "close": [hour, minute]
    }
    * open and close are only included if setting is "time"
    * hour and minute are ints
    """
    print("Received message from topic '{}': {}".format(topic, payload))
    global received_count
    
    curtain.parse_setting(payload)
    
    received_count += 1
    if received_count == cmdUtils.get_command("count"):
        received_all_event.set()


if __name__ == '__main__':
    curtain = RunMotor()
    mqtt_connection = cmdUtils.build_mqtt_connection(
        on_connection_interrupted, on_connection_resumed)

    if is_ci == False:
        print("Connecting to {} with client ID '{}'...".format(
            cmdUtils.get_command(cmdUtils.m_cmd_endpoint), cmdUtils.get_command("client_id")))
    else:
        print("Connecting to endpoint with client ID")
    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    message_count = cmdUtils.get_command("count")
    message_topic = cmdUtils.get_command(cmdUtils.m_cmd_topic)
    message_topic = "curtain/setting"

    # Subscribe
    print("Subscribing to topic '{}'...".format(message_topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=message_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if message_count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
