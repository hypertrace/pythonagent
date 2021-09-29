import aiohttp
import asyncio
from hypertrace.agent import Agent
import os
import json
import logging

agent = Agent()
agent.instrument()

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


async def main():
    async with aiohttp.ClientSession() as session:
        isStream = False
        if 'STREAM' in os.environ and os.environ['STREAM'] == 'true':
            isStream = True

        query = ""
        if isStream:
            logging.debug('Receving response stream')
            query = "?stream=true"

        async with session.post(
                'http://localhost:9000/' + query,
                data='{"name":"Dave"}',
                headers={'content-type': 'application/json'}
        ) as resp:
            if isStream:
                # Read the response as a stream
                content = b''
                async for line in resp.content:
                    content += line
                    logging.debug("Receiving response chunk")
                resBody = json.loads(content)
            else:
                # Read the entire response
                resBody = await resp.json()

            print(resBody['message'])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
