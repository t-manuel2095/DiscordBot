import aiohttp
import asyncio

#API created using Cursor

class APIClient:
    def __init__(self, base_url='http://localhost:8000/api/v1'):
        self.base_url = base_url
    
    async def get_queue(self, guild_id):
        """Fetch queue for guild"""
        async with aiohttp.ClientSession() as session:
            url = f'{self.base_url}/queues/{guild_id}/'
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
    
    async def create_queue(self, guild_id):
        """Create new queue for guild"""
        async with aiohttp.ClientSession() as session:
            url = f'{self.base_url}/queues/'
            data = {'guild_id': guild_id}
            async with session.post(url, json=data) as response:
                if response.status == 201:
                    return await response.json()
                return None
    
    async def add_song(self, guild_id, title, url, added_by):
        """Add song to queue"""
        async with aiohttp.ClientSession() as session:
            endpoint = f'{self.base_url}/queues/{guild_id}/add_song/'
            data = {
                'title': title,
                'url': url,
                'added_by': added_by
            }
            print(f'[*] API: Posting to {endpoint}')
            print(f'[*] API: URL in request: {url[:80] if url else "None"}...')
            async with session.post(endpoint, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    print(f'[+] API: Song stored with URL: {result.get("url", "")[:80]}...')
                    return result
                else:
                    print(f'[-] API: Error {response.status}')
                return None
    
    async def delete_song(self, song_id):
        """Remove song from queue"""
        async with aiohttp.ClientSession() as session:
            url = f'{self.base_url}/songs/{song_id}/'
            async with session.delete(url) as response:
                return response.status == 204
    
    async def next_song(self, guild_id):
        """Advance to next song"""
        async with aiohttp.ClientSession() as session:
            url = f'{self.base_url}/queues/{guild_id}/next_song/'
            async with session.post(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
    
    async def delete_queue(self, guild_id):
        """Delete queue for guild"""
        async with aiohttp.ClientSession() as session:
            url = f'{self.base_url}/queues/{guild_id}/'
            async with session.delete(url) as response:
                return response.status == 204


