import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime

GPIO.setmode(GPIO.BOARD)

# message to be imported from AWS
message = 11
close = 11
open = 12
if message = close:
        Motor1A = close
else:
        Motor1A = open
        
GPIO.setup(Motor1A,GPIO.OUT)
stop = False
try: 
        while stop == False:
                now = datetime.now()
                now_str = str(now)[:-7]
                d1 =  datetime(2023, 3, 3, 00, 29, 0)
                d1_str = str(d1)
                print("now: ", now_str, " d1: ", d1_str)
                if now_str == d1_str:
                        print("turning on")
                        GPIO.output(Motor1A,GPIO.HIGH)
                        sleep(10)
                        print("Stopping motor")
                        GPIO.output(Motor1A,GPIO.LOW)
                        stop = True
finally:
        GPIO.cleanup()