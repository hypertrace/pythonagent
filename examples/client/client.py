import aiohttp
import asyncio
from hypertrace.agent import Agent
import os

agent = Agent()
agent.register_aiohttp_client()


async def main():
    async with aiohttp.ClientSession() as session:
        query = ""
        if 'STREAM' in os.environ and os.environ['STREAM'] == 'true':
            query = "?stream=true"

        async with session.post(
                'http://localhost:9000/' + query,
                data='{"name":"Dave"}',
                headers={'content-type': 'application/json'}
        ) as resp:
            resBody = await resp.json()
            print(resBody['message'])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
