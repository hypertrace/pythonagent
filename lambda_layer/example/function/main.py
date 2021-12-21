import os
import json
import aiohttp
import asyncio


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def callAioHttp():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, "http://httpbin.org/")


# lambda function
def lambda_handler(event, context):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(callAioHttp())

    return {"statusCode": 200,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"x-amzn-trace-id": os.environ.get("_X_AMZN_TRACE_ID")})}
