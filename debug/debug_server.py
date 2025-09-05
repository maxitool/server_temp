import socket
import logging
import sys
import os
from typing import Final
from main_server import SIZE_BUFFER
from request_processing import RequestProcessing
import asyncio
import textwrap
from concurrent.futures import ThreadPoolExecutor

HOST: Final[str] = 'localhost'
PORT: Final[int] = 9095
MAX_COUNT_PACKETS_CAPACITY: Final[int] = 4
SIZE_BUFFER: Final[int] = 8192;

def __str_to_packets(data: str):
    count_packets = (len(data) + MAX_COUNT_PACKETS_CAPACITY) // SIZE_BUFFER
    if int((len(data) + MAX_COUNT_PACKETS_CAPACITY) % SIZE_BUFFER) > 0:
        count_packets += 1
    if count_packets < 1 or len(str(count_packets)) > MAX_COUNT_PACKETS_CAPACITY:
        return
    data = '0' * (MAX_COUNT_PACKETS_CAPACITY - len(str(count_packets))) + str(count_packets) + data
    result = [data[i * SIZE_BUFFER:i * SIZE_BUFFER + SIZE_BUFFER] for i in range(count_packets)]
    return result

async def handle_client(reader, writer):
    try:
        data = await reader.read(SIZE_BUFFER)
        message = data.decode()
        #print(message)
        count_packets = int(message[:MAX_COUNT_PACKETS_CAPACITY])
        if count_packets <= 0:
            print("count_packets <= 0")
            return
        message = message[MAX_COUNT_PACKETS_CAPACITY:]
        for i in range(count_packets - 1):
            data = await reader.read(SIZE_BUFFER)
            message += data.decode()
        response = await RequestProcessing.request_run(message)
        list_response = __str_to_packets(str(response))
        if not list_response:
            print("count_packets <= 0")
            return
        for item in list_response:
            writer.write(item.encode())
            await writer.drain()
        await writer.wait_closed()
    except Exception as e:
        print(str(e))

async def initialize_server():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        print("Server started.")
        await server.serve_forever()