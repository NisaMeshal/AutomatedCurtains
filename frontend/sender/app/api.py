from typing import Optional
from fastapi import FastAPI

from app.sender import send_message

app = FastAPI()

# This is the api endpoint that receives form data from the webpage
#  and uses it to send a message to the pi through AWS
@app.get("/")
async def send(setting: int, open: Optional[str] = None, close: Optional[str] = None):
    print(f"setting: {setting}")
    print(f"open: {open}")
    print(f"close: {close}")

    if setting == 1: # sensor
        message = {"setting": "sensor"}
        print(message)
        send_message(message)
    elif setting == 0: # time
        message = {"setting": "time"}
        open_hour, open_minute = [int(x) for x in open.split(":")]
        close_hour, close_minute = [int(x) for x in close.split(":")]
        open = [open_hour, open_minute]
        close = [close_hour, close_minute]
        message["open"] = open
        message["close"] = close
        print(message)
        send_message(message)

    return "Success"