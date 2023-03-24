import command_line_utils
from awscrt import mqtt
import sys
import threading
import time
from uuid import uuid4
import json
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime


class RunMotor():
    

    GPIO.setmode(GPIO.BOARD)
    open = True
    open_time = []
    close_time = []
    open_GPIO = 12
    close_GPIO = 11
    setting = "time"
    
    def setting_sensor(self):
        # if var >= some value
        #     self.open_curtain()
        # else
        #     self.close_curtain()
        pass

    def parse_setting(self, payload):
        if payload[0] == "time":
            self.setting = "time"
            self.open_time = payload[1]
            self.close_time = payload[2]
        elif payload[0] == "sensor":
            self.setting = "sensor"
            self.setting_sensor()
            

    def open_curtain(self):
        GPIO.setup(self.open_GPIO, GPIO.OUT)
        stop = False
        try:
            while stop == False:
                print("turning on")
                GPIO.output(self.open_GPIO, GPIO.HIGH)
                # need to change this depending on the length
                sleep(10)
                print("Stopping motor")
                GPIO.output(self.open_GPIO, GPIO.LOW)
                stop = True
        finally:
            GPIO.cleanup()
        self.open = True

    def close_curtain(self):
        GPIO.setup(self.close_GPIO, GPIO.OUT)
        stop = False
        try:
            while stop == False:
                print("turning on")
                GPIO.output(self.close_GPIO, GPIO.HIGH)
                # need to change this depending on the length
                sleep(10)
                print("Stopping motor")
                GPIO.output(self.close_GPIO, GPIO.LOW)
                stop = True
        finally:
            GPIO.cleanup()
        self.open = False

    def is_now(self, time):
        now = datetime.now().time().replace(second=0, microsecond=0)
        now = now.strftime('%H:%M')
        now = now.split(":")
        now = [int(x) for x in now]
        print("now: ", now)
        print("time: ", time)
        if now == time:
            print("it's now")
            return True
        else:
            ("it's not now")
            return False


curtain = RunMotor()

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
    print("Checking setting")
    if curtain.setting == "time":
        print(curtain.open_time)
        if curtain.is_now(curtain.open_time) == True:
            curtain.open_curtain()
        elif curtain.is_now(curtain.close_time) == True:
            curtain.close_curtain()
    if curtain.setting == "sensor":
        curtain.setting_sensor()
    
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

    while True:
        sleep(5)
        print("Checking setting")
        if curtain.setting == "time":
            if curtain.is_now(curtain.open_time) == True:
                curtain.open_curtain()
            elif curtain.is_now(curtain.close_time) == True:
                curtain.close_curtain()
        if curtain.setting == "sensor":
            curtain.setting_sensor()

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
