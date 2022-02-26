import aiohttp
import asyncio

async def test():
    headers = {
        "Authorization": "Bearer "}
    url = f"https://www.patreon.com/api/oauth2/api/campaigns/8183553/pledges"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json(content_type=None)
            print(data)


loop =asyncio.get_event_loop()
loop.run_until_complete(test())