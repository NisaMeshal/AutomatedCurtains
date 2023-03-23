from typing import Optional
from fastapi import FastAPI

from app.sender import send_message

app = FastAPI()

# @app.get("/")
# async def root():
#     return {"message": "Hello World!"}

@app.get("/")
async def send(setting: int, open: Optional[str] = None, close: Optional[str] = None):
    print(f"setting: {setting}")
    print(f"open: {open}")
    print(f"close: {close}")

    send_message({"hi": "bye"})

    if setting == 1: # sensor
        message = {"setting": "sensor"}
        print(message)
        send_message(message)
    elif setting == 0:
        message = {"setting": "time"}
        open_hour, open_minute = [int(x) for x in open.split(":")]
        close_hour, close_minute = [int(x) for x in close.split(":")]
        open = [open_hour, open_minute]
        close = [close_hour, close_minute]
        message["open"] = open
        message["close"] = close
        print(message)
        send_message(message)

    return {"hi": "bye"}

@app.get("/time/{open_hour}/{open_minute}/{close_hour}/{close_minute}")
async def time(open_hour: int, open_minute: int, close_hour: int, close_minute: int):
    if open_hour < 0 or open_hour > 23 or close_hour < 0 or close_hour > 23:
        return {"error": "hour must be int in [0 : 23]"}
    if open_minute < 0 or open_minute > 59 or close_minute < 0 or close_minute > 59:
        return {"error": "minute must be int in [0 : 59]"}
    message = {"setting": "time", "open": [open_hour, open_minute], "close": [close_hour, close_minute]}
    try:
        send_message(message)
        return {"message": "Success"}
    except:
        return {"error": "Failed to send message"}
    
@app.get("/sensor/")
async def sensor():
    try:
        send_message({"setting": "sensor"})
        return {"message": "Success"}
    except Exception as e:
        print(e)
        return {"error": "Failed to send message"}
