import aiohttp
import asyncio
from hypertrace.agent import Agent


agent = Agent(True)
agent.register_aiohttp_client()


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post(
                'https://petstore.swagger.io/v2/pet',
                data='{"name":"Dave"}',
                headers={'content-type': 'application/json'}
        ) as resp:
            print(await resp.json())
            #print("Call succeeded: %s" % resBody['message'])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
