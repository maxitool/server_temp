import logging
import sys
import os
from typing import Final
from request_processing import RequestProcessing
import asyncio
import textwrap
from concurrent.futures import ThreadPoolExecutor
import websockets
import ssl
from debug import debug_server
from tonsdk.crypto import mnemonic_new

HOST: Final[str] = 'localhost'
PORT: Final[int] = 443
MAX_COUNT_PACKETS_CAPACITY: Final[int] = 4
SIZE_BUFFER: Final[int] = 8192;
#ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#ssl_context.load_cert_chain("fullchain.pem", "privkey.pem")
#ssl_context.check_hostname = False
#ssl_context.verify_mode = ssl.CERT_NONE

def __str_to_packets(data: str):
    count_packets = (len(data) + MAX_COUNT_PACKETS_CAPACITY) // SIZE_BUFFER
    if int((len(data) + MAX_COUNT_PACKETS_CAPACITY) % SIZE_BUFFER) > 0:
        count_packets += 1
    if count_packets < 1 or len(str(count_packets)) > MAX_COUNT_PACKETS_CAPACITY:
        return
    data = '0' * (MAX_COUNT_PACKETS_CAPACITY - len(str(count_packets))) + str(count_packets) + data
    result = [data[i * SIZE_BUFFER:i * SIZE_BUFFER + SIZE_BUFFER] for i in range(count_packets)]
    return result

async def websocket_handler(websocket):
    websocket_connected = True
    while websocket_connected:
        try:
            data = await websocket.recv()
            #if (len(data) != SIZE_BUFFER):
            #    websocket_connected = False
             #   websocket.close()
              #  break
            message = data.decode()
            #print(message)
            count_packets = int(message[:MAX_COUNT_PACKETS_CAPACITY])
            if count_packets <= 0:
                print("count_packets <= 0")
                continue
            message = message[MAX_COUNT_PACKETS_CAPACITY:]
            for i in range(count_packets - 1):
                data = await websocket.recv()
                message += data.decode()
            response = await RequestProcessing.request_run(message)
            list_response = __str_to_packets(str(response))
            if not list_response:
                print("count_packets <= 0")
                continue
            for item in list_response:
                websocket.send(item.encode())
        except websockets.exceptions.ConnectionClosed:
            websocket_connected = False
            break
        except Exception as e:
            websocket_connected = False
            print(e)

async def main():
    #async with websockets.serve(websocket_handler, HOST, PORT, ssl=ssl_context):
    async with websockets.serve(websocket_handler, HOST, PORT):
        print("Server started.")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        # initialize debug socket server
        #asyncio.run(debug_server.initialize_server())
        # initialize release websocket server
        asyncio.run(main())
    except Exception as e:
        print("Can't run server, reason: " + str(e))