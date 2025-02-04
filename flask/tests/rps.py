import requests
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import asyncio

url = "http://127.0.0.1:5000/api/v1/wallets"
num_requests = 10000
'''
def send_request(_):
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(send_request, range(num_requests))
'''

async def send_request(session):
    try:
        async with session.get(url) as response:
            print(f"Status: {response.status}")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session) for _ in range(num_requests)]
        await asyncio.gather(*tasks)

asyncio.run(main())