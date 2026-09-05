import httpx
class HTTPClient:
    async def post(self,url,headers,json_data,timeout=120):
        async with httpx.AsyncClient(verify=True,timeout=timeout,follow_redirects=True) as c:
            return await c.post(url,headers=headers,json=json_data)
